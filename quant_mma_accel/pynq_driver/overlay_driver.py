from __future__ import annotations


class OverlayDriver:
    def __init__(self, bitfile: str, ip_name: str):
        from pynq import Overlay

        self.bitfile = bitfile
        self.ip_name = ip_name
        self.overlay = Overlay(bitfile)

        if ip_name not in self.overlay.ip_dict:
            available = sorted(self.overlay.ip_dict.keys())
            raise KeyError(
                f"IP {ip_name!r} was not found in overlay {bitfile!r}. "
                f"Available IP names: {available}"
            )

    def get_ip(self):
        target = self.overlay
        try:
            for part in self.ip_name.split("/"):
                target = getattr(target, part)
            return target
        except AttributeError as exc:
            raise KeyError(
                f"IP {self.ip_name!r} exists in ip_dict but could not be accessed as an "
                "Overlay attribute. Check the PYNQ hierarchy name."
            ) from exc

    def print_ip_dict(self) -> None:
        for name in sorted(self.overlay.ip_dict.keys()):
            print(name)
