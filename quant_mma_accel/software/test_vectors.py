import json
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import numpy as np


def generate_int8_matrices(
    M: int, K: int, N: int, seed: int = 0
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate deterministic INT8 matrices A[M,K] and B[K,N]."""
    for name, value in {"M": M, "K": K, "N": N}.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")

    np.random.seed(seed)
    input_a = np.random.randint(-128, 128, size=(M, K), dtype=np.int16).astype(np.int8)
    input_b = np.random.randint(-128, 128, size=(K, N), dtype=np.int16).astype(np.int8)
    return input_a, input_b


def save_test_vectors(
    output_dir,
    input_a: np.ndarray,
    input_b: np.ndarray,
    golden_c: np.ndarray,
    metadata,
) -> None:
    # type: (Union[str, Path], np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]) -> None
    """Save input_a.npy, input_b.npy, golden_c.npy, and metadata.json."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    full_metadata = {
        "M": int(input_a.shape[0]),
        "K": int(input_a.shape[1]),
        "N": int(input_b.shape[1]),
        "a_dtype": str(input_a.dtype),
        "b_dtype": str(input_b.dtype),
        "c_dtype": str(golden_c.dtype),
        "layout": "row-major",
    }
    full_metadata.update(metadata)

    required = {"M", "K", "N", "shift", "seed", "a_dtype", "b_dtype", "c_dtype", "layout"}
    missing = sorted(required - set(full_metadata))
    if missing:
        raise ValueError(f"metadata is missing required fields: {', '.join(missing)}")

    np.save(output_path / "input_a.npy", input_a)
    np.save(output_path / "input_b.npy", input_b)
    np.save(output_path / "golden_c.npy", golden_c)
    with (output_path / "metadata.json").open("w", encoding="utf-8") as metadata_file:
        json.dump(full_metadata, metadata_file, indent=2, sort_keys=True)
        metadata_file.write("\n")


def load_test_vectors(vector_dir):
    # type: (Union[str, Path]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]
    """Load vectors and metadata."""
    vector_path = Path(vector_dir)
    input_a = np.load(vector_path / "input_a.npy")
    input_b = np.load(vector_path / "input_b.npy")
    golden_c = np.load(vector_path / "golden_c.npy")
    with (vector_path / "metadata.json").open("r", encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)
    return input_a, input_b, golden_c, metadata