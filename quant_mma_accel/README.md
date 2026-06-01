# PYNQ-Z2 Quantized Matmul Accelerator Driver

中文说明见 [README.zh-CN.md](README.zh-CN.md)。

This project contains a Python software framework for a PYNQ-Z2 INT8 matrix multiplication accelerator. The core logic lives in Python modules so it can be developed in VS Code and reused from command line scripts or a PYNQ notebook.

The first version targets the minimal closed loop:

- Generate deterministic INT8 input matrices on PC or PYNQ.
- Compute a NumPy INT32 golden result for `C = (A @ B) >> shift`.
- Load a Vivado `.bit/.hwh` overlay on PYNQ.
- Allocate physically contiguous buffers through PYNQ.
- Configure the HLS IP through AXI Lite registers.
- Start the IP, wait for completion with timeout protection, and compare FPGA output against the CPU golden result.
- Print CPU, FPGA kernel, and end-to-end timing.

The project does not require `pynq` on a PC. PYNQ imports are delayed until board-side code is executed.

## Python Version

The workspace is kept compatible with Python 3.6.5.

- Source files avoid Python 3.7+ only syntax such as `from __future__ import annotations`, builtin generic types like `list[str]`, and union syntax like `A | B`.
- `requirements.txt` is pinned to the last `numpy` and `pytest` lines that still support Python 3.6.
- If your Python 3.6 environment has a newer `pip`, downgrade it first because recent `pip` releases dropped Python 3.6 support.

## Layout

```text
quant_mma_accel/
  configs/                  Default runtime configuration and register map template
  software/                 PC-safe NumPy reference and vector generation utilities
  pynq_driver/              PYNQ overlay, AXI Lite, and benchmark drivers
  scripts/                  Command line entry points
  tests/                    PC-side unit tests
  test_vectors/             Generated `.npy` vectors
  overlays/                 Put Vivado-exported `.bit/.hwh` files here
```

## PC Setup And Checks

From this directory:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade "pip<22"
pip install -r requirements.txt
python scripts/generate_vectors.py --M 16 --K 64 --N 16 --shift 7 --seed 0 --out test_vectors/default
python scripts/run_cpu_check.py --vectors test_vectors/default
pytest
```

On Linux or PYNQ, activate the virtual environment with `source .venv/bin/activate` instead.

If the board already ships with Python 3.6.5 and PYNQ preinstalled, you usually only need:

```bash
python -m pip install --upgrade "pip<22"
pip install -r requirements.txt
```

## PYNQ Board Flow

Copy this project to the board, for example:

```text
/home/xilinx/jupyter_notebooks/matmul_accel/quant_mma_accel
```

Place the hardware files here:

```text
overlays/matmul_overlay.bit
overlays/matmul_overlay.hwh
```

Generate or copy test vectors, then run:

```bash
python scripts/run_pynq_once.py \
  --bitfile overlays/matmul_overlay.bit \
  --ip-name matmul_accel_0 \
  --register-map configs/register_map.example.json \
  --vectors test_vectors/default
```

Run the default benchmark cases:

```bash
python scripts/run_benchmark.py \
  --bitfile overlays/matmul_overlay.bit \
  --ip-name matmul_accel_0 \
  --register-map configs/register_map.example.json
```

## Register Map

The example register map contains placeholder offsets. Replace `configs/register_map.example.json` with offsets from the HLS/Vivado driver header, such as `xmatmul_accel_hw.h`.

Required logical registers:

- `CTRL`: AXI Lite control register. Defaults to `0x00` if omitted.
- `A_ADDR`, `B_ADDR`, `C_ADDR`: DDR physical addresses for row-major buffers.
- `M`, `K`, `N`, `SHIFT`: matrix dimensions and output shift.

Offsets may be JSON integers or strings such as `"0x10"`.

For 64-bit pointer registers, add high-word offsets using any of these key styles:

```json
{
  "A_ADDR": "0x10",
  "A_ADDR_HIGH": "0x14",
  "B_ADDR": "0x1c",
  "B_ADDR_HIGH": "0x20",
  "C_ADDR": "0x28",
  "C_ADDR_HIGH": "0x2c"
}
```

The driver writes the low 32 bits to `A_ADDR` and, when configured, the high 32 bits to `A_ADDR_HIGH`.

## Hardware Interface To Confirm

Ask the hardware team for the exported HLS control register map:

```text
Please send the HLS control register map, ideally xmatmul_accel_hw.h or the generated driver header.
I need the offsets for a/b/c pointers, M, K, N, shift, ap_start, ap_done, and whether pointer registers are 32-bit or 64-bit.
```

The expected data contract is:

- `A`: INT8, shape `M x K`, row-major.
- `B`: INT8, shape `K x N`, row-major.
- `C`: INT32, shape `M x N`, row-major.
- Formula: `C = (A @ B) >> shift`.

## Notebook

`pynq_driver/demo_notebook.ipynb` is an entry point for board demos. It imports and calls the Python modules instead of duplicating driver logic.
