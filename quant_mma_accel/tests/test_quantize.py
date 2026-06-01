import numpy as np
import pytest

from software.quantize import dequantize_from_int8, quantize_to_int8


def test_quantize_to_int8_rounds_clips_and_casts() -> None:
    values = np.array([-2.0, -1.2, -0.4, 0.4, 1.2, 2.0], dtype=np.float32)

    result = quantize_to_int8(values, scale=100.0)

    expected = np.array([-128, -120, -40, 40, 120, 127], dtype=np.int8)
    assert result.dtype == np.int8
    np.testing.assert_array_equal(result, expected)


def test_dequantize_from_int8_returns_float32() -> None:
    values = np.array([-128, -64, 0, 64, 127], dtype=np.int8)

    result = dequantize_from_int8(values, scale=64.0)

    assert result.dtype == np.float32
    np.testing.assert_allclose(result, values.astype(np.float32) / 64.0)


def test_quantize_rejects_non_positive_scale() -> None:
    with pytest.raises(ValueError, match="positive"):
        quantize_to_int8(np.array([1.0], dtype=np.float32), scale=0.0)


def test_dequantize_rejects_non_positive_scale() -> None:
    with pytest.raises(ValueError, match="positive"):
        dequantize_from_int8(np.array([1], dtype=np.int8), scale=-1.0)
