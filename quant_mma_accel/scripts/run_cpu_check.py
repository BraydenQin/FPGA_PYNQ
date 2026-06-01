import argparse
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from software.cpu_ref import matmul_int8_ref
from software.test_vectors import load_test_vectors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run CPU golden-result validation.")
    parser.add_argument("--vectors", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_a, input_b, golden_c, metadata = load_test_vectors(args.vectors)
    shift = int(metadata["shift"])

    start = time.perf_counter()
    computed_c = matmul_int8_ref(input_a, input_b, shift)
    cpu_time_ms = (time.perf_counter() - start) * 1000.0

    passed = np.array_equal(computed_c, golden_c)
    max_abs_error = int(np.max(np.abs(computed_c.astype(np.int64) - golden_c.astype(np.int64))))
    print("PASS" if passed else "FAIL")
    print(f"M={metadata['M']} K={metadata['K']} N={metadata['N']} shift={shift}")
    print(f"max_abs_error={max_abs_error}")
    print(f"cpu_time_ms={cpu_time_ms:.6f}")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
