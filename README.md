# Marginally Correct Tool Caches Can Reverse Group-Normalized Policy Updates

**Shivam Gupta | Research artifact | September 2026**

[Read the paper (PDF)](paper.pdf) · [Build the manuscript](research/cache-coupling/paper/README.md)

This repository accompanies a controlled analytical and implementation study of stochastic tool-result sharing. It contains proofs, exhaustive finite sums, reproducibility protocols, and a pinned TVCache runtime audit. It does not report language-model training or establish a defect in TVCache's published benchmarks.

The central result is that preserving each rollout's conditional reward distribution does not ensure an equivalent expected group-normalized update. Sharing can change the update direction and its variance. Centering without within-group standard-deviation scaling is an existing control, not a new optimizer.

## Reproduce

```sh
python3 -m unittest discover -s research/cache-coupling/tests -v
python3 research/cache-coupling/src/reproduce.py numerical
python3 research/cache-coupling/reviews/check_extensions.py
```

The numerical computation uses the Python standard library. The supported reproduction command verifies source hashes, executes in a disposable canonical copy, and requires byte-identical results while preserving historical results and manifests. [Full instructions](research/cache-coupling/README.md) include pinned runtime setup. After that setup, run:

```sh
research/cache-coupling/work/.venv/bin/python research/cache-coupling/src/reproduce.py runtime
```

The wrapper uses the invoking interpreter and checks every locked runtime package version. Runtime sources are retrieved at a fixed Git revision, never from an unpinned working tree; their hashes are checked before linking them into the disposable copy.

## Contents

- [Model and derivation](research/cache-coupling/docs/derivation.md)
- [Numerical protocol](research/cache-coupling/docs/protocol-001.md) and [results](research/cache-coupling/docs/findings-001.md)
- [Runtime protocol](research/cache-coupling/docs/protocol-002.md) and [results](research/cache-coupling/docs/findings-002.md)
- [Prior work and claim boundaries](research/cache-coupling/docs/literature-gate.md)
- [LaTeX manuscript source](research/cache-coupling/paper/manuscript.tex)

The grid contains 540 configurations and 3,240 estimator evaluations. The runtime probe covers eight scripted cases with 256 one-call rollouts, including direct controls. These counts are not independent statistical trials. Source and result manifests preserve the exact experiment inputs.

## Provenance and license

LLM-based tools assisted the research exploration, code, mathematical analysis, writing, and internal review. Automated checks and internal reviews are not external peer review. The work makes no claim of conference acceptance or universal novelty.

Original artifact code and documentation are MIT licensed. Third-party TVCache source is not redistributed; the preparation script retrieves its Apache-2.0-licensed code from the specified public revision. See its license in the retrieved source.
