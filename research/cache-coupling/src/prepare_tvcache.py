"""Export exact source bytes from an existing pinned clone, never working files."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REVISION = "3a4f95a6582eea1e4b7e84a9f3a0c74eaa8fde02"
DEFAULT = "/Users/shivamgupta/Downloads/research-sources/TVCache"


def prepare(clone):
    names = subprocess.check_output(
        ["git", "-C", str(clone), "ls-tree", "-r", "--name-only", REVISION], text=True).splitlines()
    selected = [name for name in names if
        (name.startswith(("tvcache/client/", "tvcache/server/")) and
         (name.endswith(".py") or name.endswith("pyproject.toml"))) or
        name in ("tvcache/LICENSE", "README.md", "train/tvc_agent_loop.py",
                 "video-agent-tools/VideoAgent/tools.py",
                 "video-agent-tools/VideoAgent/captioning.py")]
    files = {}
    for name in selected:
        data = subprocess.check_output(["git", "-C", str(clone), "show", REVISION + ":" + name])
        path = ROOT / "work/vendor" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        files[name] = hashlib.sha256(data).hexdigest()
    manifest = {"repository": "https://github.com/TVCache/TVCache", "revision": REVISION,
                "files": files, "source_count": len(files)}
    output = ROOT / "results/tvcache-sources.json"
    serialized = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if output.exists() and output.read_text() != serialized:
        raise RuntimeError("Refusing to replace a different source manifest")
    output.write_text(serialized)
    print(f"Exported {len(files)} pinned source files")


if __name__ == "__main__":
    prepare(Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT))
