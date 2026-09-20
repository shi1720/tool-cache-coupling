"""Reproduce frozen results in a disposable copy without replacing provenance."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = {
    "numerical": ("enumerate_updates.py", "enumeration-001.json", "manifest-001.json"),
    "runtime": ("runtime_probe.py", "runtime-002.json", "runtime-002-manifest.json"),
}


def verify_file(path, checksum):
    if hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
        raise RuntimeError("SHA-256 mismatch: " + str(path))


def reproduce(mode, vendor=None):
    script, result_name, manifest_name = EXPERIMENTS[mode]
    manifest = json.loads((ROOT / "results" / manifest_name).read_text())
    # Historical manifests may contain work/../src even without a work directory.
    for name, checksum in manifest["sources"].items():
        source = (ROOT / name).resolve()
        source.relative_to(ROOT)
        verify_file(source, checksum)
    frozen = ROOT / "results" / result_name
    verify_file(frozen, manifest["result_sha256"])
    expected = frozen.read_bytes()
    if mode == "runtime":
        vendor = (vendor or ROOT / "work/vendor").resolve()
        sources = json.loads((ROOT / "results/tvcache-sources.json").read_text())
        for name, checksum in sources["files"].items():
            verify_file(vendor / name, checksum)
        for line in (ROOT / "requirements-runtime.lock").read_text().splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            package, version = line.split("==")
            actual = importlib.metadata.version(package)
            if actual != version:
                raise RuntimeError(f"Runtime dependency mismatch: {package}=={actual}; expected {version}")
    with tempfile.TemporaryDirectory(prefix="cache-coupling-reproduce-") as temporary:
        # resolve() also canonicalizes the macOS /var -> /private/var alias.
        scratch = Path(temporary).resolve() / "experiment"
        scratch.mkdir()
        for directory in ("src", "docs", "tests", "results"):
            shutil.copytree(ROOT / directory, scratch / directory)
        lock = ROOT / "requirements-runtime.lock"
        if lock.exists():
            shutil.copyfile(lock, scratch / lock.name)
        work = scratch / "work"
        work.mkdir()
        if mode == "runtime":
            (work / "vendor").symlink_to(vendor, target_is_directory=True)
        output = scratch / "results" / result_name
        output.unlink()
        subprocess.run([sys.executable, "-B", str(scratch / "src" / script)],
                       cwd=work, check=True)
        if output.read_bytes() != expected:
            raise RuntimeError("Reproduction mismatch: " + result_name)
    print(f"Verified {mode}: {result_name} is byte-identical; historical files preserved.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=EXPERIMENTS)
    parser.add_argument("--vendor", type=Path,
                        help="Existing pinned vendor tree (runtime only); never copied or modified")
    args = parser.parse_args(argv)
    if args.vendor is not None and args.mode != "runtime":
        parser.error("--vendor applies only to runtime")
    try:
        reproduce(args.mode, args.vendor)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError,
            importlib.metadata.PackageNotFoundError) as error:
        parser.exit(1, f"Reproduction failed: {error}\n")


if __name__ == "__main__":
    main()
