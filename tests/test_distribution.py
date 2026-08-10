from __future__ import annotations

import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def test_builds_complete_wheel_and_sdist(tmp_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--no-isolation",
            "--outdir",
            str(tmp_path),
        ],
        cwd=PACKAGE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    wheel = next(tmp_path.glob("tyxter-*.whl"))
    sdist = next(tmp_path.glob("tyxter-*.tar.gz"))

    with zipfile.ZipFile(wheel) as archive:
        wheel_names = set(archive.namelist())
        metadata_path = next(name for name in wheel_names if name.endswith(".dist-info/METADATA"))
        metadata = archive.read(metadata_path).decode("utf-8")
    assert {
        "tyxter/_version.py",
        "tyxter/client.py",
        "tyxter/py.typed",
        "tyxter/resources/media.py",
        "tyxter/resources/messages.py",
        "tyxter/types/media.py",
        "tyxter/types/messages.py",
        "tyxter/types/provider_connections.py",
        "tyxter/webhooks.py",
    } <= wheel_names
    assert any(name.endswith(".dist-info/METADATA") for name in wheel_names)
    assert any(name.endswith(".dist-info/licenses/LICENSE") for name in wheel_names)
    assert "Version: 0.6.0" in metadata.splitlines()
    assert "Requires-Python: >=3.10" in metadata
    assert "Requires-Dist: typing-extensions" in metadata

    with tarfile.open(sdist, mode="r:gz") as archive:
        sdist_names = {name.split("/", 1)[-1] for name in archive.getnames()}
    assert {
        "CHANGELOG.md",
        "LICENSE",
        "README.md",
        "pyproject.toml",
        "src/tyxter/_version.py",
        "src/tyxter/py.typed",
        "src/tyxter/resources/media.py",
        "src/tyxter/resources/messages.py",
        "src/tyxter/types/media.py",
        "src/tyxter/types/messages.py",
        "src/tyxter/types/provider_connections.py",
    } <= sdist_names
