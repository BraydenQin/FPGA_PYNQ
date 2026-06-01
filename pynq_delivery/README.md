# PYNQ Delivery Package

This directory contains the files that the PYNQ-side teammate can use directly
for the INT8 matrix multiplication overlay.

## Recommended files to hand off

- `matmul_overlay.bit`
- `matmul_overlay.hwh`
- `register_map.actual.json`
- `PYNQ_Delivery_Guide.docx`

## Additional reference files

- `matmul_overlay.xsa`
- `xmatmul_accel_hw.h`
- `csynth.rpt`
- `overlay_metadata.json`

## Hardware facts

- Overlay base name: `matmul_overlay`
- IP instance name: `matmul_accel_0`
- AXI Lite base address: `0x40000000`
- AXI Lite high address: `0x4000FFFF`
- Data contract:
  - `A`: `int8[M, K]`, row-major
  - `B`: `int8[K, N]`, row-major
  - `C`: `int32[M, N]`, row-major
  - Compute rule: `C = (A @ B) >> shift`
- Data movement path: PS configures the IP through AXI Lite, and the IP reads
  and writes DDR directly through `m_axi`.

## PYNQ usage notes

- Keep `matmul_overlay.bit` and `matmul_overlay.hwh` in the same directory and
  keep the same base name. PYNQ Overlay loading expects this.
- Use `matmul_accel_0` as `ip_name`.
- The provided `register_map.actual.json` is compatible with
  `RegisterMap.from_json(...)` in the local PYNQ driver.

## Minimal software example

```python
from pynq_driver.matmul_accel import MatmulAccel
from pynq_driver.register_map import RegisterMap

register_map = RegisterMap.from_json("register_map.actual.json")
accel = MatmulAccel(
    bitfile="matmul_overlay.bit",
    ip_name="matmul_accel_0",
    register_map=register_map,
)

output = accel.run(input_a, input_b, shift=0)
```

## Naming note

The `matmul_overlay.*` files are convenience copies of the exported design for
PYNQ use. They are byte-identical to the corresponding `design_1_wrapper.*`
files, but renamed so the `.bit` and `.hwh` clearly share one overlay base
name.
