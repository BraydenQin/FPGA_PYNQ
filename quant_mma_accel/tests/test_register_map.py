import json

import pytest

from pynq_driver.register_map import RegisterMap


def test_register_map_parses_hex_int_and_high_word_offsets(tmp_path) -> None:
    register_map_path = tmp_path / "register_map.json"
    register_map_path.write_text(
        json.dumps(
            {
                "CTRL": "0x00",

                "A_ADDR": "0x10",
                "A_ADDR_HIGH": "0x14",
                "B_ADDR": 0x20,
                "B_ADDR_HIGH": 0x24,
                "C_ADDR": "0x30",
                "M": "0x40",
                "K": "0x48",
                "N": "0x50",
                "SHIFT": "0x58",
            }
        ),
        encoding="utf-8",
    )

    register_map = RegisterMap.from_json(register_map_path)

    assert register_map.CTRL == 0x00
    assert register_map.A_ADDR == 0x10
    assert register_map.A_ADDR_HIGH == 0x14
    assert register_map.B_ADDR == 0x20
    assert register_map.B_ADDR_HIGH == 0x24
    assert register_map.address_offsets("C_ADDR") == (0x30, None)


def test_register_map_defaults_ctrl(tmp_path) -> None:
    register_map_path = tmp_path / "register_map.json"
    register_map_path.write_text(
        json.dumps(
            {
                "A_ADDR": "0x10",
                "B_ADDR": "0x1c",
                "C_ADDR": "0x28",
                "M": "0x34",
                "K": "0x3c",
                "N": "0x44",
                "SHIFT": "0x4c",
            }
        ),
        encoding="utf-8",
    )

    register_map = RegisterMap.from_json(register_map_path)

    assert register_map.CTRL == 0x00


def test_register_map_reports_missing_required_fields(tmp_path) -> None:
    register_map_path = tmp_path / "register_map.json"
    register_map_path.write_text(json.dumps({"A_ADDR": "0x10"}), encoding="utf-8")

    with pytest.raises(ValueError, match="missing required fields"):
        RegisterMap.from_json(register_map_path)
