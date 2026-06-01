import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from software.cpu_ref import matmul_int8_ref
from software.test_vectors import generate_int8_matrices, save_test_vectors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate INT8 matmul test vectors.")
    parser.add_argument("--M", type=int, default=16)
    parser.add_argument("--K", type=int, default=64)
    parser.add_argument("--N", type=int, default=16)
    parser.add_argument("--shift", type=int, default=7)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("test_vectors/default"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_a, input_b = generate_int8_matrices(args.M, args.K, args.N, seed=args.seed)
    golden_c = matmul_int8_ref(input_a, input_b, args.shift)
    save_test_vectors(
        args.out,
        input_a,
        input_b,
        golden_c,
        {"M": args.M, "K": args.K, "N": args.N, "shift": args.shift, "seed": args.seed},
    )
    print(f"Wrote test vectors to {args.out}")


if __name__ == "__main__":
    main()
