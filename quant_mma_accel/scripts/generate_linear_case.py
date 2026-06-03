import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from llm.linear_layer import generate_linear_case, save_linear_case


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a reusable INT8 linear-layer NPZ case.")
    parser.add_argument("--M", type=int, default=16)
    parser.add_argument("--K", type=int, default=512)
    parser.add_argument("--N", type=int, default=512)
    parser.add_argument("--shift", type=int, default=7)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("test_vectors/linear/synthetic_m16_k512_n512.npz"))
    return parser.parse_args()


def main():
    args = parse_args()
    case = generate_linear_case(args.M, args.K, args.N, shift=args.shift, seed=args.seed)
    metadata = dict(case["metadata"])
    metadata["note"] = "Synthetic LLM-like INT8 linear layer case for CPU/FPGA comparison."
    save_linear_case(str(args.out), case["input_a"], case["weight_b"], case["shift"], metadata)
    print("Wrote %s" % args.out)
    print("shape input_a=%r weight_b=%r shift=%d" % (case["input_a"].shape, case["weight_b"].shape, case["shift"]))


if __name__ == "__main__":
    main()
