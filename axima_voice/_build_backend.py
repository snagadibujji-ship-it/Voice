from __future__ import annotations

import base64
import csv
import hashlib
import io
import time
import zipfile
from pathlib import Path
from typing import Any

NAME = "axima_voice"
DIST_NAME = "axima_voice"
VERSION = "0.1.0"


def _metadata() -> str:
    return "\n".join(
        [
            "Metadata-Version: 2.1",
            "Name: axima-voice",
            f"Version: {VERSION}",
            "Summary: Meaning-first experimental voice engine for Axima",
            "Requires-Python: >=3.10",
            "",
        ]
    )


def _wheel() -> str:
    return "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: axima_voice._build_backend",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        ]
    )


def _hash(data: bytes) -> tuple[str, int]:
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
    return f"sha256={digest.decode()}", len(data)


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    del config_settings, metadata_directory
    root = Path(__file__).resolve().parents[1]
    dist_info = f"{DIST_NAME}-{VERSION}.dist-info"
    wheel_name = f"{DIST_NAME}-{VERSION}-py3-none-any.whl"
    wheel_path = Path(wheel_directory) / wheel_name
    records: list[tuple[str, str, int]] = []

    def write_file(archive: zipfile.ZipFile, arcname: str, data: bytes) -> None:
        info = zipfile.ZipInfo(arcname, time.localtime()[:6])
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, data)
        digest, size = _hash(data)
        records.append((arcname, digest, size))

    with zipfile.ZipFile(wheel_path, "w") as archive:
        for path in sorted((root / NAME).glob("*.py")):
            write_file(archive, f"{NAME}/{path.name}", path.read_bytes())
        write_file(archive, f"{dist_info}/METADATA", _metadata().encode())
        write_file(archive, f"{dist_info}/WHEEL", _wheel().encode())
        record_name = f"{dist_info}/RECORD"
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        for arcname, digest, size in records:
            writer.writerow([arcname, digest, size])
        writer.writerow([record_name, "", ""])
        archive.writestr(record_name, output.getvalue().encode())
    return wheel_name


def prepare_metadata_for_build_wheel(
    metadata_directory: str, config_settings: dict[str, Any] | None = None
) -> str:
    del config_settings
    dist_info = Path(metadata_directory) / f"{DIST_NAME}-{VERSION}.dist-info"
    dist_info.mkdir(parents=True, exist_ok=True)
    (dist_info / "METADATA").write_text(_metadata())
    (dist_info / "WHEEL").write_text(_wheel())
    return dist_info.name


def build_sdist(
    sdist_directory: str, config_settings: dict[str, Any] | None = None
) -> str:
    del config_settings
    raise NotImplementedError("sdist builds are not used by the Phase 10 quality gate")
