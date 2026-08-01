# from pathlib import Path
# LEARNING_DIR = Path(__file__).resolve().parents[1]
# SCRIPTS_DIR = LEARNING_DIR / "scripts"

# import sys
# sys.path.insert(0, str(SCRIPTS_DIR))
# from common import SOURCE_CSV, load_runtime_results


from pathlib import Path
LEARNING_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = LEARNING_DIR/"scripts"


import sys
sys.path.insert(0, str(SCRIPT_DIR))
from common import load_runtime_results, clean_runtime_results, THREAD_ORDER


def main():
    raw = load_runtime_results()
    clean = clean_runtime_results(raw)

    # print(f"Raw rows: {len(raw)}")
    # print(f"Raw rows: {raw.shape[0]}")
    # print(f"rows after status/thread/runtime filtering: {len(clean)}")
    # print(f"thread values kept: {list(THREAD_ORDER)}")

    print("\nrows by scale:")
    print(clean["threads"].value_counts(sort=True))

    print("\nTotal core values:")
    print(sorted(clean["total_cores"].unique()))

    print("\nCheck total_cores formula")
    calculated = clean["nodes"] * clean["ppn"] * clean["threads"].astype(int)
    print((clean["total_cores"] == calculated).value_counts().to_string())

    print("\nClean sample:")
    columns = ["scale", "unknowns", "nodes", "ppn", "threads", "total_cores", "runtime_seconds"]
    print(clean[columns].head(12).to_string(index=False))




if __name__ == "__main__":
    main()