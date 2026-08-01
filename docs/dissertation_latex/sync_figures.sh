#!/usr/bin/env bash
# Copy the generated formal-campaign figures into figures/ for draft.tex.
#
# draft.tex must reference figures by bare filename with \graphicspath{{figures/}}
# only. Do not \includegraphics a relative path into analysis/ — reorganising the
# plots tree then silently breaks the build.
#
# Regenerate the sources first:
#   analysis/.venv/bin/python analysis/scripts/nproc_2d_libsci/analyze_repeated_fullnode_logs.py
#   analysis/.venv/bin/python analysis/scripts/nproc_3d_libsci/analyze_repeated_fullnode_logs.py
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
FIGURES="$HERE/figures"

copy_one() {  # <dim> <generated basename> <target basename>
  local src="$REPO/analysis/plots/nproc_$1_libsci/repeated_fullnode/$2.pdf"
  if [[ ! -f "$src" ]]; then
    echo "MISSING: $src  (regenerate the analysis pipeline first)" >&2
    return 1
  fi
  cp "$src" "$FIGURES/$3.pdf"
  echo "  $3.pdf"
}

copy_flat() {  # <plots subdir> <generated basename> <target basename>
  local src="$REPO/analysis/plots/$1/$2.pdf"
  if [[ ! -f "$src" ]]; then
    echo "MISSING: $src  (regenerate the analysis pipeline first)" >&2
    return 1
  fi
  cp "$src" "$FIGURES/$3.pdf"
  echo "  $3.pdf"
}

echo "Syncing figures into $FIGURES"

# Ch3: single-node default-solver sweep
#   analysis/.venv/bin/python analysis/scripts/size_grid/analyze_single_node_sweep.py
copy_flat size_grid single_node_cost_per_iteration "size_grid_single_node_cost_per_iteration"

for dim in 2d 3d; do
  copy_one "$dim" repeated_fullnode_equations_per_second_vs_nodes  "ksp${dim}_throughput_vs_nodes"
  copy_one "$dim" repeated_fullnode_seconds_per_iteration_vs_nodes "ksp${dim}_seconds_per_iteration"
  copy_one "$dim" repeated_fullnode_layout_speedup_vs_mpi          "ksp${dim}_layout_vs_mpi"
  # Ch6: analysis/scripts/nproc_2d_libsci/analyze_event_breakdown.py (covers both dims)
  copy_one "$dim" repeated_fullnode_time_breakdown                 "ksp${dim}_sync_share"
  # Ch4 fixed-20m strong scaling:
  #   analysis/scripts/strong_scaling_20m/analyze_strong_scaling_20m.py --dimension $dim
  copy_flat "nproc_${dim}_libsci/strong_scaling_20m" \
    strong_scaling_20m_runtime_vs_nodes    "ksp${dim}_strong20m_runtime"
  # Ch5: analysis/scripts/nproc_2d_libsci/analyze_event_breakdown.py (covers both dims)
  copy_one "$dim" repeated_fullnode_exposure_tradeoff "ksp${dim}_exposure_tradeoff"
done

# Ch4: 3D parallel efficiency. Only 3D is included -- nothing saturates in 2D, so the
# 2D efficiency curve says nothing the runtime figure does not. Both are generated.
copy_flat nproc_3d_libsci/strong_scaling_20m \
  strong_scaling_20m_efficiency_vs_nodes "ksp3d_strong20m_efficiency"

# Ch5: analysis/scripts/map_profiles/analyze_map_profiles.py
copy_flat nproc_2d_libsci/map_profiles map_solve_window_shares "map_solve_window_shares"
# The vs-NPROC figures were dropped in the 2026-07-31 Ch5 rewrite: the ratio plot
# states the same comparison more directly, and the current analysis script no
# longer regenerates them. Copies are in .trash/2026-07-31/.
echo "Done."
