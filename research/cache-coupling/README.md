# Shared tool outcomes and group-normalized learning

A bounded research experiment asks whether tool-result sharing changes the
expected policy update despite preserving marginal rewards. It includes an
analytical derivation, exhaustive finite-sum calculations, independent tests,
and a candid comparison with prior work. It is not a model-training study or a
claim of a new optimization method.

```sh
python3 -m unittest discover -s research/cache-coupling/tests -v
python3 research/cache-coupling/src/reproduce.py numerical
python3 research/cache-coupling/reviews/check_extensions.py
```

These commands need only Python 3.8+ and its standard library. The supported
reproduction wrapper checks source and result hashes, runs the frozen program
in a disposable canonical copy, and fails explicitly if result bytes differ.
Original result files and historical manifests remain unchanged. The existing
figure is included; rerendering its frozen script requires Matplotlib and should
also be done in a disposable copy if preserving figure provenance.

- [Pre-execution protocol](docs/protocol-001.md)
- [Derivation and assumptions](docs/derivation.md)
- [Results and limits](docs/findings-001.md)
- [Literature and novelty gate](docs/literature-gate.md)
- [All numerical results](results/enumeration-001.json)
- [Pinned runtime protocol](docs/protocol-002.md)
- [Runtime findings and limits](docs/findings-002.md)
- [Figure](results/shared-outcome-updates.png)

To repeat the implementation bridge, clone
`https://github.com/TVCache/TVCache` to a location of your choice, then run:

```sh
python3 research/cache-coupling/src/prepare_tvcache.py /path/to/TVCache
python3.12 -m venv research/cache-coupling/work/.venv
research/cache-coupling/work/.venv/bin/python -m pip install -r research/cache-coupling/requirements-runtime.lock
research/cache-coupling/work/.venv/bin/python research/cache-coupling/src/reproduce.py runtime
```

The preparation script retrieves the pinned Git revision, exports original
source bytes, and records their hashes. The runtime uses the actual executor,
HTTP client, Flask endpoints and cache backend with in-process transport and a
scripted environment. Package versions are pinned. It needs no credentials,
network access during execution, model weights, or video data. The wrapper uses
the invoking virtual environment's interpreter and verifies every package
version against the lockfile. It links the hash-verified vendor tree into the
disposable copy without copying the virtual environment. To reuse an existing
vendor export elsewhere, append `--vendor /absolute/path/to/vendor`.

The frozen probe runs with a canonical script path inside the disposable work
directory, which also contains the vendor import's local log file. This supports
checkouts reached through directory symlinks. `src/run_runtime.py` is a compatibility
entry point for the same provenance-preserving runtime command.

The original probe and its historical manifest remain frozen. The manifest's
`work/../src/runtime_probe.py` key names `src/runtime_probe.py`; resolve manifest
paths before verifying hashes, especially in a clean checkout without `work`.
The original scripts can fail under path aliases and rewrite manifests on
successful reruns. Use the supported `reproduce.py` commands above to handle
path normalization and preserve historical provenance automatically. These
commands do not change the frozen experiment programs or their committed files.

Current status: the mechanism is verified in the constructed model. Novelty and
practical importance remain unestablished. Prior experiments elsewhere in this
repository are preserved unchanged.
