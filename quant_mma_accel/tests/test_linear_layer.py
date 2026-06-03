import numpy as np

from llm.linear_layer import generate_linear_case, load_linear_case, run_cpu_linear, save_linear_case
from software.cpu_ref import matmul_int8_ref


def test_generate_linear_case_shapes_and_cpu_result():
    case = generate_linear_case(3, 5, 2, shift=1, seed=10)

    assert case["input_a"].shape == (3, 5)
    assert case["weight_b"].shape == (5, 2)
    output, elapsed_ms = run_cpu_linear(case["input_a"], case["weight_b"], case["shift"])

    np.testing.assert_array_equal(output, matmul_int8_ref(case["input_a"], case["weight_b"], 1))
    assert elapsed_ms >= 0.0


def test_save_and_load_linear_case(tmp_path):
    case = generate_linear_case(2, 4, 3, shift=2, seed=11)
    path = tmp_path / "case.npz"

    save_linear_case(str(path), case["input_a"], case["weight_b"], case["shift"], {"layer_name": "toy"})
    loaded = load_linear_case(str(path))

    np.testing.assert_array_equal(loaded["input_a"], case["input_a"])
    np.testing.assert_array_equal(loaded["weight_b"], case["weight_b"])
    assert loaded["shift"] == 2
    assert loaded["metadata"]["layer_name"] == "toy"