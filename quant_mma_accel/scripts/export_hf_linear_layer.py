import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from llm.linear_layer import quantize_symmetric_int8, save_linear_case


DEFAULT_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
DEFAULT_LAYER = "model.layers.0.mlp.down_proj.weight"


def parse_args():
    parser = argparse.ArgumentParser(description="Export one HuggingFace linear weight as an INT8 NPZ case.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--layer-name", type=str, default=DEFAULT_LAYER)
    parser.add_argument("--out", type=Path, default=Path("test_vectors/linear/tinyllama_layer0_down_proj.npz"))
    parser.add_argument("--M", type=int, default=16)
    parser.add_argument("--shift", type=int, default=7)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--dtype", choices=("float32", "float16"), default="float16")
    return parser.parse_args()


def main():
    args = parse_args()
    weight = load_hf_weight(args.model, args.layer_name, args.local_files_only, args.dtype)
    if weight.ndim != 2:
        raise ValueError("layer %s is not a 2D weight, got shape %r" % (args.layer_name, weight.shape))

    # PyTorch Linear stores [out_features, in_features]; hardware expects B=[K, N].
    weight_b_float = np.ascontiguousarray(weight.T, dtype=np.float32)
    weight_b, weight_scale = quantize_symmetric_int8(weight_b_float)
    rng = np.random.RandomState(args.seed)
    input_a = rng.randint(-128, 128, size=(args.M, weight_b.shape[0])).astype(np.int8)
    metadata = {
        "model": args.model,
        "layer_name": args.layer_name,
        "weight_scale": weight_scale,
        "source": "huggingface",
        "note": "PyTorch Linear weight was transposed from [out, in] to hardware [K, N].",
    }
    save_linear_case(str(args.out), input_a, weight_b, args.shift, metadata)
    print("Wrote %s" % args.out)
    print("shape input_a=%r weight_b=%r shift=%d" % (input_a.shape, weight_b.shape, args.shift))


def load_hf_weight(model_name, layer_name, local_files_only, dtype):
    try:
        import torch
        from transformers import AutoModelForCausalLM
    except ImportError as exc:
        raise SystemExit(
            "HuggingFace export requires optional PC-side packages: torch and transformers. "
            "Install them on a PC environment, export the NPZ, then copy the NPZ to PYNQ. "
            "Original import error: %s" % exc
        )

    torch_dtype = torch.float16 if dtype == "float16" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        local_files_only=local_files_only,
    )
    state = model.state_dict()
    if layer_name not in state:
        matches = [name for name in state.keys() if name.endswith("weight") and "proj" in name]
        raise KeyError("layer %r was not found. Example linear weights: %r" % (layer_name, matches[:20]))
    tensor = state[layer_name].detach().cpu().to(torch.float32).numpy()
    del model
    return tensor


if __name__ == "__main__":
    main()
