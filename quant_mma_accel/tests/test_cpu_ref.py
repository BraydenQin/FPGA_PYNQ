import numpy as np
import pytest

from software.cpu_ref import matmul_int8_ref


def test_matmul_int8_ref_returns_int32_shifted_result() -> None:
    input_a = np.array([[1, 2, -3], [4, -5, 6]], dtype=np.int8)
    input_b = np.array([[7, -8], [9, 10], [-11, 12]], dtype=np.int8)

    result = matmul_int8_ref(input_a, input_b, shift=1)

    expected = ((input_a.astype(np.int32) @ input_b.astype(np.int32)) >> 1).astype(np.int32)
    assert result.dtype == np.int32
    np.testing.assert_array_equal(result, expected)


def test_matmul_int8_ref_rejects_non_2d_input() -> None:
    with pytest.raises(ValueError, match="2D"):
        matmul_int8_ref(np.array([1, 2], dtype=np.int8), np.ones((2, 2), dtype=np.int8), 0)


def test_matmul_int8_ref_rejects_incompatible_shapes() -> None:
    with pytest.raises(ValueError, match="incompatible"):
        matmul_int8_ref(np.ones((2, 3), dtype=np.int8), np.ones((4, 2), dtype=np.int8), 0)


def test_matmul_int8_ref_uses_int32_accumulation() -> None:
    input_a = np.full((1, 64), 127, dtype=np.int8)
    input_b = np.full((64, 1), 127, dtype=np.int8)

    result = matmul_int8_ref(input_a, input_b, shift=0)

    assert int(result[0, 0]) == 127 * 127 * 64


def test_matmul_int8_ref_rejects_negative_shift() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        matmul_int8_ref(np.ones((1, 1), dtype=np.int8), np.ones((1, 1), dtype=np.int8), -1)
