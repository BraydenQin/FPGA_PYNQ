from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


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


@dataclass(frozen=True)
class RegisterMap:
    CTRL: int
    A_ADDR: int
    B_ADDR: int
    C_ADDR: int
    M: int
    K: int
    N: int
    SHIFT: int
    A_ADDR_HIGH: int | None = None
    B_ADDR_HIGH: int | None = None
    C_ADDR_HIGH: int | None = None

    @classmethod
    def from_json(cls, path: str | Path) -> "RegisterMap":
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

    def address_offsets(self, base: str) -> tuple[int, int | None]:
        """Return low and optional high-word offsets for A_ADDR, B_ADDR, or C_ADDR."""
        if base not in {"A_ADDR", "B_ADDR", "C_ADDR"}:
            raise ValueError(f"unknown address register base {base!r}")
        return getattr(self, base), getattr(self, f"{base}_HIGH")


def _find_high_word_key(raw: dict[str, object], base: str) -> str | None:
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
