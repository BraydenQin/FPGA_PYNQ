from __future__ import annotations

import time
from typing import Any

import numpy as np

from pynq_driver.overlay_driver import OverlayDriver
from pynq_driver.register_map import RegisterMap


class MatmulAccel:
    def __init__(
        self,
        bitfile: str,
        ip_name: str,
        register_map: RegisterMap,
        timeout_s: float = 5.0,
    ):
        self.overlay_driver = OverlayDriver(bitfile, ip_name)
        self.ip = self.overlay_driver.get_ip()
        self.register_map = register_map
        self.timeout_s = timeout_s

    def run(self, input_a: np.ndarray, input_b: np.ndarray, shift: int) -> np.ndarray:
        """Run hardware matmul and return INT32 output matrix."""
        result, _ = self.run_with_timing(input_a, input_b, shift)
        return result

    def run_with_timing(
        self, input_a: np.ndarray, input_b: np.ndarray, shift: int
    ) -> tuple[np.ndarray, dict[str, float]]:
        """Run hardware matmul and return result plus timing dict."""
        self._validate_inputs(input_a, input_b, shift)
        M, K = input_a.shape
        _, N = input_b.shape

        from pynq import allocate

        total_start = time.perf_counter()
        a_buf = b_buf = c_buf = None
        try:
            a_buf = allocate(shape=(M * K,), dtype=np.int8)
            b_buf = allocate(shape=(K * N,), dtype=np.int8)
            c_buf = allocate(shape=(M * N,), dtype=np.int32)

            a_buf[:] = np.ascontiguousarray(input_a).reshape(-1)
            b_buf[:] = np.ascontiguousarray(input_b).reshape(-1)
            c_buf[:] = 0

            _flush_if_available(a_buf)
            _flush_if_available(b_buf)
            _flush_if_available(c_buf)

            kernel_start = time.perf_counter()
            self._write_address("A_ADDR", int(a_buf.physical_address))
            self._write_address("B_ADDR", int(b_buf.physical_address))
            self._write_address("C_ADDR", int(c_buf.physical_address))
            self._write(self.register_map.M, M)
            self._write(self.register_map.K, K)
            self._write(self.register_map.N, N)
            self._write(self.register_map.SHIFT, int(shift))
            self._write(self.register_map.CTRL, 0x01)
            self._wait_done()
            kernel_end = time.perf_counter()

            _invalidate_if_available(c_buf)
            output = np.array(c_buf, dtype=np.int32, copy=True).reshape(M, N)
            total_end = time.perf_counter()
        finally:
            for buffer in (a_buf, b_buf, c_buf):
                _free_if_available(buffer)

        timing = {
            "fpga_kernel_time_ms": (kernel_end - kernel_start) * 1000.0,
            "total_time_ms": (total_end - total_start) * 1000.0,
        }
        return output, timing

    @staticmethod
    def _validate_inputs(input_a: np.ndarray, input_b: np.ndarray, shift: int) -> None:
        if input_a.ndim != 2:
            raise ValueError(f"input_a must be a 2D matrix, got shape {input_a.shape}")
        if input_b.ndim != 2:
            raise ValueError(f"input_b must be a 2D matrix, got shape {input_b.shape}")
        if input_a.dtype != np.int8:
            raise TypeError(f"input_a must have dtype np.int8, got {input_a.dtype}")
        if input_b.dtype != np.int8:
            raise TypeError(f"input_b must have dtype np.int8, got {input_b.dtype}")
        if input_a.shape[1] != input_b.shape[0]:
            raise ValueError(
                "matrix shapes are incompatible: "
                f"input_a has K={input_a.shape[1]}, input_b has K={input_b.shape[0]}"
            )
        if shift < 0:
            raise ValueError(f"shift must be non-negative, got {shift}")

    def _write_address(self, base: str, physical_address: int) -> None:
        low_offset, high_offset = self.register_map.address_offsets(base)
        self._write(low_offset, physical_address & 0xFFFFFFFF)
        if high_offset is not None:
            self._write(high_offset, (physical_address >> 32) & 0xFFFFFFFF)
        elif physical_address >> 32:
            raise ValueError(
                f"physical address 0x{physical_address:x} for {base} needs a high-word register, "
                "but no high offset is configured in the register map"
            )

    def _wait_done(self) -> None:
        deadline = time.perf_counter() + self.timeout_s
        while True:
            ctrl = int(self._read(self.register_map.CTRL))
            if ctrl & 0x02:
                return
            if time.perf_counter() >= deadline:
                raise TimeoutError(
                    f"matmul accelerator did not assert ap_done within {self.timeout_s:.3f}s; "
                    f"last CTRL value was 0x{ctrl:08x}"
                )
            time.sleep(0.0001)

    def _write(self, offset: int, value: int) -> None:
        self.ip.write(offset, int(value))

    def _read(self, offset: int) -> Any:
        return self.ip.read(offset)


def _flush_if_available(buffer: Any) -> None:
    if hasattr(buffer, "flush"):
        buffer.flush()


def _invalidate_if_available(buffer: Any) -> None:
    if hasattr(buffer, "invalidate"):
        buffer.invalidate()


def _free_if_available(buffer: Any) -> None:
    if buffer is None:
        return
    if hasattr(buffer, "freebuffer"):
        buffer.freebuffer()
    elif hasattr(buffer, "close"):
        buffer.close()
