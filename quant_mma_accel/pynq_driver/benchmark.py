from __future__ import annotations

import time

import numpy as np

from pynq_driver.matmul_accel import MatmulAccel
from software.cpu_ref import matmul_int8_ref
from software.test_vectors import generate_int8_matrices


def run_benchmark(cases: list[dict], accel: MatmulAccel) -> list[dict]:
    """Run multiple M/K/N/shift cases and return result rows."""
    rows = []
    for index, case in enumerate(cases):
        M = int(case["M"])
        K = int(case["K"])
        N = int(case["N"])
        shift = int(case.get("shift", 7))
        seed = int(case.get("seed", index))

        input_a, input_b = generate_int8_matrices(M, K, N, seed=seed)

        cpu_start = time.perf_counter()
        golden_c = matmul_int8_ref(input_a, input_b, shift)
        cpu_time_ms = (time.perf_counter() - cpu_start) * 1000.0

        fpga_c, timing = accel.run_with_timing(input_a, input_b, shift)
        diff = fpga_c.astype(np.int64) - golden_c.astype(np.int64)
        max_abs_error = int(np.max(np.abs(diff))) if diff.size else 0

        rows.append(
            {
                "M": M,
                "K": K,
                "N": N,
                "shift": shift,
                "pass": bool(np.array_equal(fpga_c, golden_c)),
                "max_abs_error": max_abs_error,
                "cpu_time_ms": cpu_time_ms,
                "fpga_kernel_time_ms": timing["fpga_kernel_time_ms"],
                "total_time_ms": timing["total_time_ms"],
            }
        )
    return rows
