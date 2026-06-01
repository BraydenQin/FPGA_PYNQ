import argparse
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pynq_driver.matmul_accel import MatmulAccel
from pynq_driver.register_map import RegisterMap
from software.cpu_ref import matmul_int8_ref
from software.test_vectors import load_test_vectors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one PYNQ matmul accelerator validation.")
    parser.add_argument("--bitfile", type=str, required=True)
    parser.add_argument("--ip-name", type=str, required=True)
    parser.add_argument("--register-map", type=Path, required=True)
    parser.add_argument("--vectors", type=Path, required=True)
    parser.add_argument("--timeout-s", type=float, default=5.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_a, input_b, stored_golden_c, metadata = load_test_vectors(args.vectors)
    shift = int(metadata["shift"])

    cpu_start = time.perf_counter()
    golden_c = matmul_int8_ref(input_a, input_b, shift)
    cpu_time_ms = (time.perf_counter() - cpu_start) * 1000.0
    if not np.array_equal(golden_c, stored_golden_c):
        raise ValueError("stored golden_c.npy does not match CPU recomputation")

    register_map = RegisterMap.from_json(args.register_map)
    accel = MatmulAccel(args.bitfile, args.ip_name, register_map, timeout_s=args.timeout_s)
    fpga_c, timing = accel.run_with_timing(input_a, input_b, shift)

    diff = fpga_c.astype(np.int64) - golden_c.astype(np.int64)
    max_abs_error = int(np.max(np.abs(diff))) if diff.size else 0
    passed = np.array_equal(fpga_c, golden_c)

    print("PASS" if passed else "FAIL")
    print(f"M={metadata['M']} K={metadata['K']} N={metadata['N']} shift={shift}")
    print(f"max_abs_error={max_abs_error}")
    print(f"cpu_time_ms={cpu_time_ms:.6f}")
    print(f"fpga_kernel_time_ms={timing['fpga_kernel_time_ms']:.6f}")
    print(f"total_time_ms={timing['total_time_ms']:.6f}")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
