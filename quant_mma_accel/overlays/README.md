# Overlay Cache

The software flow now uses the Vivado hardware export in `fpga_hardware` as the source of truth:

```text
../fpga_hardware/accelerator_hardware/AI_accelerator.xsa
```

When a `.xsa` file is passed to the PYNQ driver, the driver extracts the contained `.bit` and `.hwh` into `overlays/generated/` with matching base names, then loads the generated `.bit` through `pynq.Overlay`.

Do not copy `.bit/.hwh` from `pynq_delivery` for the default software flow.
