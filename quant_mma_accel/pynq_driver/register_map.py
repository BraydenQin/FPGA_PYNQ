import json
from pathlib import Path
from typing import Dict, Optional, Tuple, Union


def _parse_offset(name: str, value: object) -> int:
    if isinstance(value, int):
        if value < 0:
            raise ValueError(f"offset {name} must be non-negative, got {value}")
        return value
    if isinstance(value, str):
        try:
            parsed = int(value, 0)
        except ValueError as exc:
            raise ValueError(f"offset {name} must be an integer or hex string, got {value!r}") from exc
        if parsed < 0:
            raise ValueError(f"offset {name} must be non-negative, got {value!r}")
        return parsed
    raise TypeError(f"offset {name} must be an integer or string, got {type(value).__name__}")


class RegisterMap:
    def __init__(
        self,
        CTRL,
        A_ADDR,
        B_ADDR,
        C_ADDR,
        M,
        K,
        N,
        SHIFT,
        A_ADDR_HIGH=None,
        B_ADDR_HIGH=None,
        C_ADDR_HIGH=None,
    ):
        self.CTRL = CTRL
        self.A_ADDR = A_ADDR
        self.B_ADDR = B_ADDR
        self.C_ADDR = C_ADDR
        self.M = M
        self.K = K
        self.N = N
        self.SHIFT = SHIFT
        self.A_ADDR_HIGH = A_ADDR_HIGH
        self.B_ADDR_HIGH = B_ADDR_HIGH
        self.C_ADDR_HIGH = C_ADDR_HIGH

    @classmethod
    def from_json(cls, path):
        # type: (Union[str, Path]) -> "RegisterMap"
        with Path(path).open("r", encoding="utf-8") as register_file:
            raw = json.load(register_file)

        if not isinstance(raw, dict):
            raise ValueError("register map JSON must contain an object")

        required = ["A_ADDR", "B_ADDR", "C_ADDR", "M", "K", "N", "SHIFT"]
        missing = [name for name in required if name not in raw]
        if missing:
            raise ValueError(f"register map is missing required fields: {', '.join(missing)}")

        parsed = {name: _parse_offset(name, raw[name]) for name in required}
        parsed["CTRL"] = _parse_offset("CTRL", raw.get("CTRL", 0x00))

        for base in ("A_ADDR", "B_ADDR", "C_ADDR"):
            high_key = _find_high_word_key(raw, base)
            parsed[f"{base}_HIGH"] = _parse_offset(high_key, raw[high_key]) if high_key else None

        return cls(**parsed)

    def address_offsets(self, base):
        # type: (str) -> Tuple[int, Optional[int]]
        """Return low and optional high-word offsets for A_ADDR, B_ADDR, or C_ADDR."""
        if base not in {"A_ADDR", "B_ADDR", "C_ADDR"}:
            raise ValueError(f"unknown address register base {base!r}")
        return getattr(self, base), getattr(self, f"{base}_HIGH")


def _find_high_word_key(raw, base):
    # type: (Dict[str, object], str) -> Optional[str]
    aliases = (
        f"{base}_HIGH",
        f"{base}_HI",
        f"{base}_MSB",
        f"{base}_2",
        base.replace("_ADDR", "_ADDR_HIGH"),
    )
    for alias in aliases:
        if alias in raw:
            return alias
    return None
