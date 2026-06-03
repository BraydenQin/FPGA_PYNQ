
import shutil
import tarfile
import zipfile
from pathlib import Path


class OverlayDriver:
    def __init__(self, bitfile: str, ip_name: str):
        from pynq import Overlay

        self.bitfile = str(_prepare_overlay_bitfile(bitfile))
        self.ip_name = ip_name
        self.overlay = Overlay(self.bitfile)

        if ip_name not in self.overlay.ip_dict:
            available = sorted(self.overlay.ip_dict.keys())
            raise KeyError(
                f"IP {ip_name!r} was not found in overlay {self.bitfile!r}. "
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


def _prepare_overlay_bitfile(overlay_source):
    # type: (str) -> Path
    source = Path(overlay_source).expanduser()
    if source.suffix.lower() == ".xsa":
        return _extract_overlay_from_xsa(source)
    return source


def _extract_overlay_from_xsa(xsa_path):
    # type: (Path) -> Path
    if not xsa_path.exists():
        raise FileNotFoundError("XSA overlay source was not found: %s" % xsa_path)

    output_dir = Path(__file__).resolve().parents[1] / "overlays" / "generated" / xsa_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    bit_out = output_dir / (xsa_path.stem + ".bit")
    hwh_out = output_dir / (xsa_path.stem + ".hwh")

    if tarfile.is_tarfile(str(xsa_path)):
        _extract_from_tar_xsa(xsa_path, bit_out, hwh_out)
    elif zipfile.is_zipfile(str(xsa_path)):
        _extract_from_zip_xsa(xsa_path, bit_out, hwh_out)
    else:
        raise ValueError("XSA file is not a supported tar/zip archive: %s" % xsa_path)

    return bit_out


def _extract_from_tar_xsa(xsa_path, bit_out, hwh_out):
    # type: (Path, Path, Path) -> None
    with tarfile.open(str(xsa_path), "r:*") as archive:
        members = archive.getmembers()
        bit_member = _select_archive_name([member.name for member in members], ".bit")
        hwh_member = _select_archive_name([member.name for member in members], ".hwh")
        member_by_name = {member.name: member for member in members}
        _copy_tar_member(archive, member_by_name[bit_member], bit_out)
        _copy_tar_member(archive, member_by_name[hwh_member], hwh_out)


def _extract_from_zip_xsa(xsa_path, bit_out, hwh_out):
    # type: (Path, Path, Path) -> None
    with zipfile.ZipFile(str(xsa_path), "r") as archive:
        names = archive.namelist()
        bit_name = _select_archive_name(names, ".bit")
        hwh_name = _select_archive_name(names, ".hwh")
        with archive.open(bit_name) as source_file, bit_out.open("wb") as target_file:
            shutil.copyfileobj(source_file, target_file)
        with archive.open(hwh_name) as source_file, hwh_out.open("wb") as target_file:
            shutil.copyfileobj(source_file, target_file)


def _select_archive_name(names, suffix):
    # type: (list, str) -> str
    candidates = [name for name in names if name.lower().endswith(suffix)]
    if not candidates:
        raise ValueError("XSA archive does not contain a %s file" % suffix)
    if suffix == ".hwh":
        top_level = [name for name in candidates if "/" not in name and "smartconnect" not in name.lower()]
        if top_level:
            return sorted(top_level)[0]
        non_smartconnect = [name for name in candidates if "smartconnect" not in name.lower()]
        if non_smartconnect:
            return sorted(non_smartconnect)[0]
    return sorted(candidates)[0]


def _copy_tar_member(archive, member, output_path):
    # type: (tarfile.TarFile, tarfile.TarInfo, Path) -> None
    source_file = archive.extractfile(member)
    if source_file is None:
        raise ValueError("XSA archive member is not a regular file: %s" % member.name)
    with source_file, output_path.open("wb") as target_file:
        shutil.copyfileobj(source_file, target_file)
