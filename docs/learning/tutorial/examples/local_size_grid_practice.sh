#!/usr/bin/env bash

# WSL-safe practice version of scripts/run_ex2_size_grid.sbatch.
# It generates a run plan by default and only launches ex2 when DRY_RUN=0.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"

SIZE_TABLE="${SIZE_TABLE:-${SCRIPT_DIR}/local_problem_sizes.csv}"
OUT_DIR="${OUT_DIR:-${PROJECT_ROOT}/tutorial_output/size_grid_practice}"
PLAN_CSV="${OUT_DIR}/run_plan.csv"

SCALES="${SCALES:-tiny}"
RANKS="${RANKS:-1 2 4}"
THREADS="${THREADS:-1 2 4}"
MAX_CORES="${MAX_CORES:-4}"
REPEAT="${REPEAT:-1}"
DRY_RUN="${DRY_RUN:-1}"
EX2_BIN="${EX2_BIN:-}"

read -r -a RANKS_LIST <<< "${RANKS}"
read -r -a THREADS_LIST <<< "${THREADS}"

mkdir -p "${OUT_DIR}"
printf 'scale,m,n,unknowns,ranks,threads,total_cores,rep,mode\n' > "${PLAN_CSV}"

want_scale() {
  local needle="$1"
  local selected

  for selected in ${SCALES}; do
    [[ "${selected}" == "${needle}" ]] && return 0
  done
  return 1
}

if [[ ! -f "${SIZE_TABLE}" ]]; then
  printf '[ERROR] Size table does not exist: %s\n' "${SIZE_TABLE}" >&2
  exit 1
fi

if [[ "${DRY_RUN}" == "0" ]]; then
  if [[ -z "${EX2_BIN}" || ! -x "${EX2_BIN}" ]]; then
    printf '[ERROR] Set EX2_BIN to an executable local ex2 when DRY_RUN=0.\n' >&2
    exit 1
  fi
  if ! command -v mpirun >/dev/null 2>&1; then
    printf '[ERROR] mpirun is required when DRY_RUN=0.\n' >&2
    exit 1
  fi
fi

printf 'Size table: %s\n' "${SIZE_TABLE}"
printf 'Selected scales: %s\n' "${SCALES}"
printf 'Ranks: %s | Threads: %s | Maximum cores: %s\n' \
  "${RANKS}" "${THREADS}" "${MAX_CORES}"
printf 'Dry run: %s\n\n' "${DRY_RUN}"

ran_any_scale=0

while IFS=, read -r scale m n unknowns; do
  [[ "${scale}" == "scale" ]] && continue
  [[ -z "${scale}" ]] && continue
  want_scale "${scale}" || continue

  ran_any_scale=1

  for r in "${RANKS_LIST[@]}"; do
    (( r > MAX_CORES )) && continue
    max_threads=$(( MAX_CORES / r ))

    for t in "${THREADS_LIST[@]}"; do
      (( t > max_threads )) && continue

      total_cores=$(( r * t ))
      export OMP_NUM_THREADS="${t}"

      for rep in $(seq 1 "${REPEAT}"); do
        if [[ "${DRY_RUN}" == "1" ]]; then
          printf '[PLAN] scale=%s m=%s n=%s ranks=%s threads=%s cores=%s rep=%s\n' \
            "${scale}" "${m}" "${n}" "${r}" "${t}" "${total_cores}" "${rep}"
          printf '       mpirun -n %s EX2_BIN -m %s -n %s -ksp_converged_reason -log_view\n' \
            "${r}" "${m}" "${n}"
          mode="dry-run"
        else
          log="${OUT_DIR}/ex2_${scale}_r${r}_t${t}_rep${rep}.log"
          printf '[RUN] scale=%s ranks=%s threads=%s rep=%s\n' \
            "${scale}" "${r}" "${t}" "${rep}"
          mpirun -n "${r}" "${EX2_BIN}" \
            -m "${m}" -n "${n}" -ksp_converged_reason -log_view | tee "${log}"
          mode="local-run"
        fi

        printf '%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
          "${scale}" "${m}" "${n}" "${unknowns}" "${r}" "${t}" \
          "${total_cores}" "${rep}" "${mode}" >> "${PLAN_CSV}"
      done
    done
  done
done < "${SIZE_TABLE}"

if (( ran_any_scale == 0 )); then
  printf '[ERROR] No selected scales were found in %s.\n' "${SIZE_TABLE}" >&2
  exit 1
fi

printf '\nPlan written to: %s\n' "${PLAN_CSV}"
