"""Reproduce frozen results in a disposable copy without replacing provenance."""
import argparse
import hashlib
import importlib.metadata
import json
import math
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


def compare_numerical(expected, actual):
    """Allow libm rounding only; retain structure, discrete results and study signs."""
    stats = {"rounded_values": 0, "max_absolute_difference": 0.0}

    def compare(left, right, path="$"):
        if type(left) is not type(right):
            raise RuntimeError("Numerical type mismatch: " + path)
        if isinstance(left, dict):
            if left.keys() != right.keys():
                raise RuntimeError("Numerical key mismatch: " + path)
            for key in left:
                compare(left[key], right[key], path + "." + key)
        elif isinstance(left, list):
            if len(left) != len(right):
                raise RuntimeError("Numerical length mismatch: " + path)
            for index, (a, b) in enumerate(zip(left, right)):
                compare(a, b, f"{path}[{index}]")
        elif isinstance(left, float):
            if not math.isfinite(left) or not math.isfinite(right):
                raise RuntimeError("Non-finite numerical value: " + path)
            if not math.isclose(left, right, rel_tol=1e-13, abs_tol=1e-14):
                raise RuntimeError(f"Numerical value mismatch: {path}: {left!r} != {right!r}")
            # The frozen experiment itself defines signs outside +/- 1e-12.
            # A tolerance must never change a reported update direction.
            if path.endswith((".expected_update", ".return_gradient")):
                sign = lambda value: 1 if value > 1e-12 else (-1 if value < -1e-12 else 0)
                if sign(left) != sign(right):
                    raise RuntimeError("Numerical sign mismatch: " + path)
            if left != right:
                stats["rounded_values"] += 1
                stats["max_absolute_difference"] = max(stats["max_absolute_difference"], abs(left-right))
        elif left != right:
            raise RuntimeError("Numerical discrete value mismatch: " + path)

    compare(expected, actual)
    return stats


def reproduce(mode, vendor=None, portable=False):
    if portable and mode != "numerical":
        raise ValueError("Portable comparison applies only to numerical results")
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
        actual = output.read_bytes()
        if portable:
            stats = compare_numerical(json.loads(expected), json.loads(actual))
        elif actual != expected:
            raise RuntimeError("Reproduction mismatch: " + result_name +
                               "; numerical results on another platform may require --portable")
    if portable:
        print(f"Verified numerical equivalence (rtol=1e-13, atol=1e-14): {stats}; historical files preserved.")
    else:
        print(f"Verified {mode}: {result_name} is byte-identical; historical files preserved.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=EXPERIMENTS)
    parser.add_argument("--vendor", type=Path,
                        help="Existing pinned vendor tree (runtime only); never copied or modified")
    parser.add_argument("--portable", action="store_true",
                        help="Numerical only: compare finite floats at rtol=1e-13, atol=1e-14; preserve types, counts and study signs")
    args = parser.parse_args(argv)
    if args.vendor is not None and args.mode != "runtime":
        parser.error("--vendor applies only to runtime")
    if args.portable and args.mode != "numerical":
        parser.error("--portable applies only to numerical")
    try:
        reproduce(args.mode, args.vendor, args.portable)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError,
            importlib.metadata.PackageNotFoundError) as error:
        parser.exit(1, f"Reproduction failed: {error}\n")


if __name__ == "__main__":
    main()
