import numpy as np


def quantize_to_int8(values: np.ndarray, scale: float) -> np.ndarray:
    """Quantize float array to INT8 with round, clip, and cast."""
    if scale <= 0:
        raise ValueError(f"scale must be positive, got {scale}")
    quantized = np.round(values * scale)
    clipped = np.clip(quantized, -128, 127)
    return clipped.astype(np.int8)


def dequantize_from_int8(values: np.ndarray, scale: float) -> np.ndarray:
    """Convert INT8 values back to float32."""
    if scale <= 0:
        raise ValueError(f"scale must be positive, got {scale}")
    return (values.astype(np.float32) / np.float32(scale)).astype(np.float32, copy=False)
