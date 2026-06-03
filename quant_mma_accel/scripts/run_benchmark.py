import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_OVERLAY_SOURCE = ROOT.parent / "fpga_hardware" / "accelerator_hardware" / "AI_accelerator.xsa"
DEFAULT_REGISTER_MAP = ROOT / "configs" / "register_map.fpga_hardware.json"

from pynq_driver.benchmark import run_benchmark
from pynq_driver.matmul_accel import MatmulAccel
from pynq_driver.register_map import RegisterMap


DEFAULT_CASES = [
    {"name": "tiny", "M": 2, "K": 4, "N": 2, "shift": 7, "seed": 0},
    {"name": "small", "M": 16, "K": 64, "N": 16, "shift": 7, "seed": 1},
    {"name": "medium", "M": 32, "K": 128, "N": 32, "shift": 7, "seed": 2},
    {"name": "shift", "M": 16, "K": 64, "N": 16, "shift": 3, "seed": 3},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PYNQ matmul accelerator benchmark cases.")
    parser.add_argument(
        "--overlay-source",
        "--bitfile",
        dest="overlay_source",
        type=str,
        default=str(DEFAULT_OVERLAY_SOURCE),
        help="Overlay source from fpga_hardware; accepts .xsa directly or a prepared .bit file.",
    )
    parser.add_argument("--ip-name", type=str, default="matmul_accel_0")
    parser.add_argument("--register-map", type=Path, default=DEFAULT_REGISTER_MAP)
    parser.add_argument("--timeout-s", type=float, default=5.0)
    parser.add_argument("--format", choices=("markdown", "csv"), default="markdown")
    parser.add_argument("--csv-out", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    register_map = RegisterMap.from_json(args.register_map)
    accel = MatmulAccel(args.overlay_source, args.ip_name, register_map, timeout_s=args.timeout_s)
    rows = run_benchmark(DEFAULT_CASES, accel)

    for row, case in zip(rows, DEFAULT_CASES):
        row["case"] = case["name"]

    if args.format == "csv":
        write_csv(rows, args.csv_out)
    else:
        print_markdown(rows)

    if not all(row["pass"] for row in rows):
        raise SystemExit(1)


def write_csv(rows, csv_out):
    # type: (List[Dict[str, Any]], Optional[Path]) -> None
    fieldnames = [
        "case",
        "M",
        "K",
        "N",
        "shift",
        "pass",
        "max_abs_error",
        "cpu_time_ms",
        "fpga_kernel_time_ms",
        "total_time_ms",
    ]
    if csv_out is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    else:
        with csv_out.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote benchmark CSV to {csv_out}")


def print_markdown(rows):
    # type: (List[Dict[str, Any]]) -> None
    headers = [
        "case",
        "M",
        "K",
        "N",
        "shift",
        "pass",
        "max_abs_error",
        "cpu_time_ms",
        "fpga_kernel_time_ms",
        "total_time_ms",
    ]
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        print(
            "| "
            + " | ".join(
                [
                    str(row["case"]),
                    str(row["M"]),
                    str(row["K"]),
                    str(row["N"]),
                    str(row["shift"]),
                    str(row["pass"]),
                    str(row["max_abs_error"]),
                    f"{row['cpu_time_ms']:.6f}",
                    f"{row['fpga_kernel_time_ms']:.6f}",
                    f"{row['total_time_ms']:.6f}",
                ]
            )
            + " |"
        )


if __name__ == "__main__":
    main()
