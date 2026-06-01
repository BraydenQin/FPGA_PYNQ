import numpy as np


def matmul_int8_ref(input_a: np.ndarray, input_b: np.ndarray, shift: int) -> np.ndarray:
    """Return INT32 golden result for C = (A @ B) >> shift."""
    if input_a.ndim != 2:
        raise ValueError(f"input_a must be a 2D matrix, got shape {input_a.shape}")
    if input_b.ndim != 2:
        raise ValueError(f"input_b must be a 2D matrix, got shape {input_b.shape}")
    if input_a.shape[1] != input_b.shape[0]:
        raise ValueError(
            "matrix shapes are incompatible: "
            f"input_a has K={input_a.shape[1]}, input_b has K={input_b.shape[0]}"
        )
    if shift < 0:
        raise ValueError(f"shift must be non-negative, got {shift}")

    accum = input_a.astype(np.int32) @ input_b.astype(np.int32)
    return np.right_shift(accum, shift).astype(np.int32, copy=False)
