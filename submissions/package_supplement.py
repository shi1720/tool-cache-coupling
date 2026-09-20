"""Create an anonymous code supplement without altering the public experiment."""
from pathlib import Path
import hashlib, json, re, shutil, tempfile, zipfile
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'research/cache-coupling'
TARGET = ROOT/'submissions/tmlr-code.zip'
with tempfile.TemporaryDirectory(prefix='anonymous-supplement-') as temporary:
 stage=Path(temporary)
 dst=stage/'research/cache-coupling'
 dst.mkdir(parents=True)
 for name in ('src','tests','docs','results'):
  shutil.copytree(BASE/name,dst/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ('README.md','requirements-runtime.lock'):
  shutil.copy2(BASE/name,dst/name)
 (dst/'reviews').mkdir()
 shutil.copy2(BASE/'reviews/check_extensions.py',dst/'reviews/check_extensions.py')
 prep=dst/'src/prepare_tvcache.py'
 old=prep.read_bytes()
 text=old.decode()
 text=re.sub(r'^DEFAULT = .*$', 'DEFAULT = str(ROOT / "work/TVCache")',text,flags=re.M)
 prep.write_text(text)
 manifest=dst/'results/runtime-002-manifest.json'
 data=json.loads(manifest.read_text())
 data['sources']['src/prepare_tvcache.py']=hashlib.sha256(prep.read_bytes()).hexdigest()
 manifest.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
 (stage/'README.md').write_text('''# Anonymous reproducibility supplement

This package accompanies “Marginally Correct Tool Caches Can Reverse Group-Normalized Policy Updates”. It contains a controlled mathematical study and a scripted implementation audit, not language-model training results.

## Run from this directory

```sh
python3 -m unittest discover -s research/cache-coupling/tests -v
python3 research/cache-coupling/src/reproduce.py numerical
python3 research/cache-coupling/reviews/check_extensions.py
```

See `research/cache-coupling/README.md` for the pinned runtime dependencies and preparation instructions. The safe reproduction command executes in a disposable copy and preserves historical result files.

## Contents

| Path inside research/cache-coupling | Purpose |
| --- | --- |
| docs/protocol-001.md | Numerical grid fixed before execution |
| src/enumerate_updates.py | Original finite-sum computation |
| tests/test_enumeration.py | Ordered-outcome checks and identities |
| reviews/check_extensions.py | Variance and stabilizer checks |
| results/enumeration-001.json | All 540 configurations |
| docs/protocol-002.md | Adaptive implementation-audit protocol |
| src/runtime_probe.py | Original scripted runtime audit |
| results/runtime-002.json | Returned sequences and execution counts |
| results/*manifest*.json | Source and result hashes |
| requirements-runtime.lock | Exact runtime dependencies |
| src/reproduce.py | Non-destructive reproduction wrapper |

## Anonymization and provenance

The preparation script's author-specific default local clone path was replaced by a relative default (`work/TVCache`). Its corresponding source hash in the runtime manifest was updated to match the packaged file. No experiment logic or numerical/runtime result bytes were changed. Passing an explicit clone path is the documented preparation command. Original third-party TVCache source is retrieved at the pinned revision and is not redistributed here. Internal AI reviews and identifying manuscript files are excluded.

Generative AI tools assisted research development, code, analysis, writing, and internal review. Automated checks are not external peer review. See the manuscript's AI use statement.
''')
 for p in stage.rglob('*'):
  if p.is_file() and p.suffix in ('.py','.md','.json','.lock','.tex'):
   if re.search(r'shivam|shi1720|/Users/|@gmail|sk-proj-',p.read_text(),re.I):
    raise RuntimeError('Identifying text remains: '+str(p.relative_to(stage)))
 with zipfile.ZipFile(TARGET,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(stage.rglob('*')):
   if p.is_file(): z.write(p,p.relative_to(stage))
 print('Created anonymous supplement:',TARGET.name)
