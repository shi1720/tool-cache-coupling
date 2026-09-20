"""Regression checks for canonical, provenance-preserving reproduction."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class ReproductionTests(unittest.TestCase):
    def make_project(self, base, mode, mismatch=False):
        original = Path(__file__).resolve().parents[1]
        root = base / "real-project"
        for directory in ("src", "docs", "tests", "results"):
            (root / directory).mkdir(parents=True)
        for name in ("reproduce.py", "run_runtime.py"):
            shutil.copyfile(original / "src" / name, root / "src" / name)
        script, output, manifest = {
            "numerical": ("enumerate_updates.py", "enumeration-001.json", "manifest-001.json"),
            "runtime": ("runtime_probe.py", "runtime-002.json", "runtime-002-manifest.json"),
        }[mode]
        expected = b"historical result\n"
        actual = b"different result\n" if mismatch else expected
        (root / "results" / output).write_bytes(expected)
        probe = root / "src" / script
        probe.write_text(
            "from pathlib import Path\n"
            "assert Path(__file__) == Path(__file__).resolve()\n"
            "root = Path(__file__).parents[1]\n"
            "assert Path.cwd() == root / 'work'\n"
            "assert __name__ == '__main__'\n"
            f"(root / 'results' / {output!r}).write_bytes({actual!r})\n"
            f"(root / 'results' / {manifest!r}).write_text('new execution metadata')\n"
        )
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        key = "work/../src/" + script if mode == "runtime" else "src/" + script
        sources = {key: digest(probe)}
        if mode == "runtime":
            # An external vendor directory avoids creating work in the original.
            vendor = base / "vendor"
            vendor.mkdir()
            (vendor / "fixture.py").write_text("# pinned vendor fixture\n")
            vendor_manifest = root / "results/tvcache-sources.json"
            vendor_manifest.write_text(json.dumps({"files": {
                "fixture.py": digest(vendor / "fixture.py")}}))
            (root / "requirements-runtime.lock").write_text("")
            sources["results/tvcache-sources.json"] = digest(vendor_manifest)
            sources["requirements-runtime.lock"] = digest(root / "requirements-runtime.lock")
        (root / "results" / manifest).write_text(json.dumps({
            "sources": sources,
            "result_sha256": hashlib.sha256(expected).hexdigest(),
            "historical_metadata": "must survive rerun",
        }))
        alias = base / "project-alias"
        alias.symlink_to(root, target_is_directory=True)
        return root, alias

    def snapshot(self, root):
        return {str(path.relative_to(root)): path.read_bytes()
                for path in root.rglob("*") if path.is_file()}

    def test_symlink_numerical_reproduction_preserves_original_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            root, alias = self.make_project(base, "numerical")
            before = self.snapshot(root)
            result = subprocess.run(
                [sys.executable, str(alias / "src/reproduce.py"), "numerical"],
                cwd=base, capture_output=True, text=True, check=True)
            self.assertIn("byte-identical", result.stdout)
            self.assertEqual(before, self.snapshot(root))
            self.assertFalse((root / "work").exists())

    def test_runtime_normalizes_historical_manifest_and_preserves_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            root, alias = self.make_project(base, "runtime")
            before = self.snapshot(root)
            vendor_before = self.snapshot(base / "vendor")
            subprocess.run(
                [sys.executable, str(alias / "src/reproduce.py"), "runtime",
                 "--vendor", str(base / "vendor")],
                cwd=base, capture_output=True, text=True, check=True)
            self.assertEqual(before, self.snapshot(root))
            self.assertEqual(vendor_before, self.snapshot(base / "vendor"))
            self.assertFalse((root / "work").exists())

    def test_mismatched_result_fails_without_replacing_original_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            root, alias = self.make_project(base, "numerical", mismatch=True)
            before = self.snapshot(root)
            result = subprocess.run(
                [sys.executable, str(alias / "src/reproduce.py"), "numerical"],
                cwd=base, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Reproduction mismatch", result.stderr)
            self.assertEqual(before, self.snapshot(root))

    def test_vendor_hash_mismatch_fails_before_runtime_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            root, alias = self.make_project(base, "runtime")
            (base / "vendor/fixture.py").write_text("changed vendor bytes")
            before = self.snapshot(root)
            result = subprocess.run(
                [sys.executable, str(alias / "src/reproduce.py"), "runtime",
                 "--vendor", str(base / "vendor")],
                cwd=base, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SHA-256 mismatch", result.stderr)
            self.assertEqual(before, self.snapshot(root))


if __name__ == "__main__":
    unittest.main()
