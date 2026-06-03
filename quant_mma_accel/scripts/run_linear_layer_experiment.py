import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from llm.linear_layer import compare_outputs, generate_linear_case, load_linear_case, run_cpu_linear, run_fpga_linear
from pynq_driver.matmul_accel import MatmulAccel
from pynq_driver.register_map import RegisterMap


DEFAULT_OVERLAY_SOURCE = ROOT.parent / "fpga_hardware" / "accelerator_hardware" / "AI_accelerator.xsa"
DEFAULT_REGISTER_MAP = ROOT / "configs" / "register_map.fpga_hardware.json"


def parse_args():
    parser = argparse.ArgumentParser(description="Run one INT8 linear-layer CPU/FPGA comparison.")
    parser.add_argument("--backend", choices=("cpu", "fpga", "both"), default="cpu")
    parser.add_argument("--case-npz", type=Path, default=None)
    parser.add_argument("--M", type=int, default=16)
    parser.add_argument("--K", type=int, default=512)
    parser.add_argument("--N", type=int, default=512)
    parser.add_argument("--shift", type=int, default=7)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--cpu-repeats", type=int, default=3)
    parser.add_argument("--fpga-repeats", type=int, default=3)
    parser.add_argument("--overlay-source", "--bitfile", dest="overlay_source", type=str, default=str(DEFAULT_OVERLAY_SOURCE))
    parser.add_argument("--ip-name", type=str, default="matmul_accel_0")
    parser.add_argument("--register-map", type=Path, default=DEFAULT_REGISTER_MAP)
    parser.add_argument("--json-out", type=Path, default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.case_npz is None:
        case = generate_linear_case(args.M, args.K, args.N, shift=args.shift, seed=args.seed)
    else:
        case = load_linear_case(args.case_npz, M=args.M, shift=args.shift, seed=args.seed)

    input_a = case["input_a"]
    weight_b = case["weight_b"]
    shift = int(case["shift"])
    metadata = case["metadata"]

    rows = []
    cpu_output = None
    if args.backend in ("cpu", "both"):
        cpu_output, cpu_time_ms = run_cpu_linear(input_a, weight_b, shift, repeats=args.cpu_repeats)
        rows.append({"backend": "cpu", "time_ms": cpu_time_ms, "kernel_time_ms": cpu_time_ms})

    if args.backend in ("fpga", "both"):
        register_map = RegisterMap.from_json(args.register_map)
        accel = MatmulAccel(args.overlay_source, args.ip_name, register_map)
        fpga_output, fpga_timing = run_fpga_linear(accel, input_a, weight_b, shift, repeats=args.fpga_repeats)
        row = {
            "backend": "fpga",
            "time_ms": fpga_timing["total_time_ms"],
            "kernel_time_ms": fpga_timing["fpga_kernel_time_ms"],
        }
        if cpu_output is None:
            cpu_output, cpu_time_ms = run_cpu_linear(input_a, weight_b, shift, repeats=1)
        row.update(compare_outputs(fpga_output, cpu_output))
        row["speedup_vs_cpu_kernel"] = cpu_time_ms / fpga_timing["fpga_kernel_time_ms"] if fpga_timing["fpga_kernel_time_ms"] > 0 else None
        row["speedup_vs_cpu_total"] = cpu_time_ms / fpga_timing["total_time_ms"] if fpga_timing["total_time_ms"] > 0 else None
        rows.append(row)

    result = {"metadata": metadata, "rows": rows}
    print_summary(result)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        with args.json_out.open("w", encoding="utf-8") as output_file:
            json.dump(result, output_file, indent=2, sort_keys=True)
        print("Wrote %s" % args.json_out)


def print_summary(result):
    metadata = result["metadata"]
    print("linear_layer M={M} K={K} N={N} shift={shift} source={source}".format(**metadata))
    print("| backend | time_ms | kernel_time_ms | pass | max_abs_error | speedup_vs_cpu_kernel | speedup_vs_cpu_total |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for row in result["rows"]:
        print(
            "| {backend} | {time_ms:.6f} | {kernel_time_ms:.6f} | {passed} | {max_abs_error} | {speedup_kernel} | {speedup_total} |".format(
                backend=row["backend"],
                time_ms=float(row["time_ms"]),
                kernel_time_ms=float(row["kernel_time_ms"]),
                passed=row.get("pass", ""),
                max_abs_error=row.get("max_abs_error", ""),
                speedup_kernel=_format_optional(row.get("speedup_vs_cpu_kernel")),
                speedup_total=_format_optional(row.get("speedup_vs_cpu_total")),
            )
        )


def _format_optional(value):
    if value is None or value == "":
        return ""
    return "%.3f" % float(value)


if __name__ == "__main__":
    main()
