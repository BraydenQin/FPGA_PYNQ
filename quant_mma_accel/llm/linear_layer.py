import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np

from software.cpu_ref import matmul_int8_ref


DEFAULT_SHIFT = 7


def symmetric_int8_scale(values):
    # type: (np.ndarray) -> float
    max_abs = float(np.max(np.abs(values))) if values.size else 0.0
    if max_abs == 0.0:
        return 1.0
    return 127.0 / max_abs


def quantize_symmetric_int8(values, scale=None):
    # type: (np.ndarray, Optional[float]) -> Tuple[np.ndarray, float]
    values = np.asarray(values, dtype=np.float32)
    if scale is None:
        scale = symmetric_int8_scale(values)
    if scale <= 0:
        raise ValueError("scale must be positive, got %r" % scale)
    quantized = np.round(values * np.float32(scale))
    clipped = np.clip(quantized, -128, 127)
    return clipped.astype(np.int8), float(scale)


def generate_linear_case(M, K, N, shift=DEFAULT_SHIFT, seed=0):
    # type: (int, int, int, int, int) -> Dict[str, Any]
    rng = np.random.RandomState(seed)
    input_a = rng.randint(-128, 128, size=(M, K)).astype(np.int8)
    weight_b = rng.randint(-128, 128, size=(K, N)).astype(np.int8)
    return {
        "input_a": input_a,
        "weight_b": weight_b,
        "shift": int(shift),
        "metadata": {
            "source": "synthetic",
            "M": int(M),
            "K": int(K),
            "N": int(N),
            "shift": int(shift),
            "seed": int(seed),
        },
    }


def load_linear_case(path, M=None, shift=DEFAULT_SHIFT, seed=0):
    # type: (str, Optional[int], int, int) -> Dict[str, Any]
    with np.load(str(path), allow_pickle=False) as data:
        if "weight_b" in data:
            weight_b = np.asarray(data["weight_b"], dtype=np.int8)
        elif "weight" in data:
            weight_b = np.asarray(data["weight"], dtype=np.int8)
        else:
            raise ValueError("linear case NPZ must contain weight_b or weight")

        metadata = _load_metadata_from_npz(data)
        case_shift = int(metadata.get("shift", shift))
        if "input_a" in data:
            input_a = np.asarray(data["input_a"], dtype=np.int8)
        else:
            if M is None:
                M = int(metadata.get("M", 1))
            rng = np.random.RandomState(seed)
            input_a = rng.randint(-128, 128, size=(int(M), weight_b.shape[0])).astype(np.int8)

    if input_a.ndim != 2 or weight_b.ndim != 2:
        raise ValueError("input_a and weight_b must be 2D matrices")
    if input_a.shape[1] != weight_b.shape[0]:
        raise ValueError(
            "input/weight shape mismatch: input_a K=%d, weight_b K=%d"
            % (input_a.shape[1], weight_b.shape[0])
        )

    metadata.update(
        {
            "source": str(path),
            "M": int(input_a.shape[0]),
            "K": int(input_a.shape[1]),
            "N": int(weight_b.shape[1]),
            "shift": int(case_shift),
        }
    )
    return {"input_a": input_a, "weight_b": weight_b, "shift": case_shift, "metadata": metadata}


def save_linear_case(path, input_a, weight_b, shift, metadata=None):
    # type: (str, np.ndarray, np.ndarray, int, Optional[Dict[str, Any]]) -> None
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = dict(metadata or {})
    metadata.update(
        {
            "M": int(input_a.shape[0]),
            "K": int(input_a.shape[1]),
            "N": int(weight_b.shape[1]),
            "shift": int(shift),
        }
    )
    np.savez(
        str(output_path),
        input_a=np.asarray(input_a, dtype=np.int8),
        weight_b=np.asarray(weight_b, dtype=np.int8),
        metadata_json=np.array(json.dumps(metadata, sort_keys=True)),
    )


def run_cpu_linear(input_a, weight_b, shift, repeats=1):
    # type: (np.ndarray, np.ndarray, int, int) -> Tuple[np.ndarray, float]
    best_ms = None
    best_output = None
    for _ in range(max(1, int(repeats))):
        start = time.perf_counter()
        output = matmul_int8_ref(input_a, weight_b, shift)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        if best_ms is None or elapsed_ms < best_ms:
            best_ms = elapsed_ms
            best_output = output
    return best_output, float(best_ms)


def run_fpga_linear(accel, input_a, weight_b, shift, repeats=1):
    # type: (Any, np.ndarray, np.ndarray, int, int) -> Tuple[np.ndarray, Dict[str, float]]
    best_timing = None
    best_output = None
    for _ in range(max(1, int(repeats))):
        output, timing = accel.run_with_timing(input_a, weight_b, shift)
        if best_timing is None or timing["fpga_kernel_time_ms"] < best_timing["fpga_kernel_time_ms"]:
            best_timing = timing
            best_output = output
    return best_output, best_timing


def compare_outputs(fpga_output, cpu_output):
    # type: (np.ndarray, np.ndarray) -> Dict[str, Any]
    diff = fpga_output.astype(np.int64) - cpu_output.astype(np.int64)
    max_abs_error = int(np.max(np.abs(diff))) if diff.size else 0
    return {"pass": bool(np.array_equal(fpga_output, cpu_output)), "max_abs_error": max_abs_error}


def _load_metadata_from_npz(data):
    # type: (Any) -> Dict[str, Any]
    if "metadata_json" not in data:
        return {}
    raw = data["metadata_json"]
    if hasattr(raw, "shape") and raw.shape == ():
        raw = raw.item()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    if not isinstance(raw, str):
        raw = str(raw)
    return json.loads(raw)
