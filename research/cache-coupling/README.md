# Shared tool outcomes and group-normalized learning

A bounded research experiment asks whether tool-result sharing changes the
expected policy update despite preserving marginal rewards. It includes an
analytical derivation, exhaustive finite-sum calculations, independent tests,
and a candid comparison with prior work. It is not a model-training study or a
claim of a new optimization method.

```sh
python3 -m unittest discover -s research/cache-coupling/tests -v
python3 research/cache-coupling/src/enumerate_updates.py
python3 research/cache-coupling/src/figure.py
```

The first two commands need only Python 3.8+ and its standard library. The figure
uses Matplotlib. Frozen results include source hashes; rerunning refuses to
replace different numerical results.

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
(cd research/cache-coupling/work && .venv/bin/python ../src/runtime_probe.py)
```

The preparation script retrieves the pinned Git revision, exports original
source bytes, and records their hashes. The runtime uses the actual executor,
HTTP client, Flask endpoints and cache backend with in-process transport and a
scripted environment. Package versions are pinned. It needs no credentials,
network access during execution, model weights, or video data. Run from the
ignored work directory as shown because a vendor import opens a local log file.

Current status: the mechanism is verified in the constructed model. Novelty and
practical importance remain unestablished. Prior experiments elsewhere in this
repository are preserved unchanged.
