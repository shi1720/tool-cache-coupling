# Final code and reproducibility audit

Audit date: 2026-09-20. Audited checkout: `37f46e85bc8b8585f0933310abe3edf64e4e3648` (`main`). This is a bounded audit, not an error-free guarantee.

## Outcome

The tested numerical results and scripted implementation bridge reproduce exactly. No numerical defect was found within the declared protocol domains. The reproducibility/path-handling and provenance-overwrite issues are addressed by supported numerical/runtime wrappers that execute unchanged historical programs in disposable copies. The historical programs retain their original limitations; see the final addendum below. Frozen experiment source, tests, protocols, numerical results, and manifests were not modified by this audit. All runtime writes occurred in a temporary copy. No paid APIs, model inference, training, or remote tool execution were used.

## Inspection and validation

Read all four original `src/*.py` files, `tests/test_enumeration.py`, `reviews/check_extensions.py`, both experiment manifests, the vendor source manifest, figure provenance, runtime lockfile, README, and both protocols.

- `python3 -m unittest discover -s research/cache-coupling/tests -v`: all six test methods passed under Python 3.9.6. These include the independent ordered-sequence oracle, centered identity, shared normalized formula, deterministic and group-two controls, and marginal reward/mass checks.
- Called `enumerate_updates.run()` in memory and serialized it with the source's exact JSON settings. All 540 configurations / 3,240 mode-estimator evaluations reproduced `enumeration-001.json` byte for byte; no result file was rewritten. Its maximum mass, marginal-reward, centered-identity, and shared-formula errors were respectively `3.3306690738754696e-15`, `1.7763568394002505e-15`, `3.3306690738754696e-16`, and `8.326672684688674e-17`. Deterministic and group-two mode differences were exactly zero.
- `python3 research/cache-coupling/reviews/check_extensions.py`: all 540 configurations passed. Maximum errors: shared normalized variance `3.1008182133085427e-16`; centered shared and fresh variances each `1.1817803680091998e-17`; centered variance gap `3.469446951953614e-18`; epsilon mean `1.1102230246251565e-16`.
- Independently extended the existing literal ordered-sequence oracle in an ephemeral command to compare all four reported moments, including fresh normalized variance. All 288 combinations of groups `{2,3,4,5}`, probabilities `{0.2,0.5}`, constants `{0.3,0.9}`, success probabilities `{0,0.6,1}`, two modes, and three estimators passed. Maximum errors for mass, update mean, variance, and reward were respectively `2.220446049250313e-16`, `1.6653345369377348e-16`, `9.71445146547012e-17`, and `1.1102230246251565e-16`.
- Verified the source/result SHA-256 values in both experiment manifests after canonicalizing their paths. Verified figure input/script hashes and both existing image/PDF output hashes. The figure selects the intended `p=0.5, c=0.9, q=0.8` witness and normalized/centered estimators; rendering was not rerun.
- Verified all 29 exported vendor file hashes against both the existing vendor tree and `git show` contents at pinned revision `3a4f95a6582eea1e4b7e84a9f3a0c74eaa8fde02` in the existing TVCache clone. This verifies the recorded bytes, not the historical authenticity of upstream commit timestamps or experimental chronology.
- Ran unchanged `runtime_probe.py` from a temporary copy using the existing Python 3.12.14 virtual environment and a link to the hash-verified vendor directory. After using a canonical script path as described below, all eight cases and 256 rollouts passed and `runtime-002.json` reproduced byte for byte. Both shared cases used two physical calls; all six other cases used 32. The recorded blocked-network-attempt count was zero. All 17 installed dependency versions exactly matched `requirements-runtime.lock`; no package installation was performed.

For each normalized epsilon (`0` and `0.0001`), the reproduced sweep counts are 54 fresh/shared opposite signs, 54 fresh updates opposing the return gradient, and 108 shared updates opposing it. All three centered-only counts are zero. These are grid counts, not statistical prevalence estimates.

## Observed defect and provenance limitations

### Noncanonical source path breaks manifest generation

`runtime_probe.py` resolves `ROOT` at line 13 but puts unresolved `Path(__file__)` into its source list at line 189 and calls `relative_to(ROOT)` at line 195. Running the unmodified script through macOS's `/var/...` path to a temporary directory whose resolved path begins `/private/var/...` completed the eight cases and result comparison/write, then raised `ValueError: ... is not in the subpath ...` when constructing the manifest. Repeating with the resolved absolute script path succeeded. `enumerate_updates.py:138-140` uses the same mixed-path pattern; the runtime failure was directly reproduced, while the corresponding enumerator failure was identified by inspection rather than a separate execution.

The frozen runtime manifest also records `work/../src/runtime_probe.py`. A literal filesystem lookup of that key fails in this clean checkout because the intermediate `work` directory does not exist. Canonicalizing paths verifies the hash successfully. The documented preparation sequence creates `work`, so this does not invalidate that sequence or the frozen result.

The supported runtime command now uses the separate `src/run_runtime.py` launcher. It resolves its project root, creates/enters `work`, and executes the unchanged probe with a canonical absolute `__file__` via `runpy`. The README explains this command, the historical manifest key, path-normalized verification, and disposable-copy reproduction to preserve provenance. No frozen source was edited.

Added `tests/test_runtime_launcher.py`, which copies the launcher to an isolated temporary project, launches it through a directory symlink from an unrelated cwd, and uses a stub probe to verify the canonical script path, `__main__` execution, and newly created `work` cwd. The complete suite now passes all seven tests. Also launched the actual frozen runtime through the previously failing macOS `/var` alias using the new launcher in the temporary copy: all cases succeeded and output remained byte-identical to the frozen runtime result. Both frozen source manifests still match after the changes.

For the numerical enumerator, use a canonical checkout path if invoking its original main entry point. Manifest verification should resolve recorded paths before reading. A future separately versioned implementation should consistently resolve source paths before relativizing them.

### Frozen-result refusal does not freeze provenance

`enumerate_updates.py:142-143` and `runtime_probe.py:197-198` unconditionally overwrite their manifests after an identical result passes the overwrite check. A rerun can therefore replace historical Python/package metadata or source-path spelling even when numerical result bytes remain unchanged. `figure.py` similarly rewrites output figures/provenance on each render. This is a reproducibility-maintenance limitation, not evidence that the presently checked manifests are incorrect. Historical manifests should be retained and re-execution metadata written separately in future revisions.

## Exact limits of the audit

- Numerical checks cover the stated finite sweep and listed small-group oracle cases using floating-point arithmetic. They do not prove arbitrary-precision correctness or correctness over arbitrary inputs. In particular, the shared normalized closed form assumes `0<c<1`; the code is not a validated general-purpose API for invalid or out-of-domain parameters.
- The runtime fixture uses sequential one-call trajectories, in-process HTTP, two scripted reward streams, and no state mutation. It does not test concurrent misses, actual network serving, expiry/eviction, multi-step restoration/fork behavior, production tool randomness, model training, or real-task degradation.
- The network guard patches Python connection and DNS entry points used by this fixture; it is not an operating-system network sandbox. Zero recorded attempts describes those instrumented entry points and this run. No paid API calls were made.
- Many invariants and provenance checks use Python `assert`; optimized execution (`python -O`) removes them. This audit used normal execution with assertions enabled.
- Vendor integrity was verified for the 29 selected files; this was not a security or correctness audit of the whole TVCache repository. Dependency versions were checked against the lockfile, but package distributions were not hash-pinned or independently audited.
- Existing figure hashes and plotting code were checked. This audit does not claim a fresh rendering/visual inspection of the manuscript or figure, literature novelty, or independent verification that protocols preceded historical execution.

## Repository state

At inspection, the checkout was clean. `HEAD`, local `main`, and cached `origin/main` were all `37f46e85bc8b8585f0933310abe3edf64e4e3648`. A fresh read-only `git ls-remote --heads origin main` returned the same hash for `https://github.com/shi1720/tool-cache-coupling.git`. This comparison is a point-in-time check, not a guarantee against subsequent remote changes. No fetch, commit, push, branch change, or frozen-file edit was performed. Authorized audit follow-up changes are this report, separate reproduction/compatibility launchers and regression tests, and both README reproduction instructions. Frozen source/results/manifests remain unchanged. These changes have not been committed or pushed by this audit.


## Final addendum: supported reproduction preserves historical provenance

This addendum supersedes the earlier launcher-only remedy and direct-enumerator workaround. Both documented reproduction commands now invoke the new `src/reproduce.py` (`numerical` or `runtime`). `src/run_runtime.py` delegates to the same safe runtime route for compatibility; it no longer executes the probe inside the original checkout.

The wrapper verifies the frozen source and result hashes, resolving historical paths such as `work/../src/runtime_probe.py`. It copies the necessary experiment directories into a disposable directory whose path is canonicalized, removes only the temporary result, and invokes the unchanged frozen program with the current `sys.executable`. After execution, it compares generated result bytes against the verified historical result and exits nonzero with an explicit reproduction-mismatch message on disagreement. Generated manifests, results, and vendor log files remain within the temporary directory and are deleted afterward. Original manifests/results are never written by this wrapper.

For runtime execution, all 17 installed package versions must match the lockfile. The existing vendor export is SHA-256 checked before being linked into the disposable `work` directory; the virtual environment is not copied. The frozen subprocess runs with `-B` to avoid bytecode writes into the linked vendor tree. An optional `--vendor` path supports a pre-existing export elsewhere. The original Python 3.12.14 runtime environment was used for the actual runtime verification; the wrapper uses the caller's interpreter rather than finding or substituting one automatically.

Both root and experiment README files now show these supported commands and describe their provenance-preserving behavior. The frozen experiment scripts, their protocols, original test file, numerical/runtime results, and historical manifests remain unchanged.

Validation after the final changes:

- All ten unittest methods passed: the six original mathematical tests plus four wrapper regressions covering symlink/canonical execution and original-file preservation, normalization of the runtime manifest path without an original `work` directory, explicit mismatch failure without historical-file changes, and vendor-tampering rejection before runtime execution.
- `python3 research/cache-coupling/src/reproduce.py numerical` completed all 540 configurations and produced a byte-identical numerical result.
- The original Python 3.12.14 virtual environment ran `src/reproduce.py runtime --vendor` against the existing pinned export. All eight cases / 256 rollouts passed, all locked dependencies matched, and the full runtime result was byte-identical.
- Git comparison confirms no changes to any frozen source, result, manifest, protocol, or original mathematical test file. No paid APIs, commit, or push were used.

The direct historical programs remain available for inspection, so manually bypassing the documented wrappers still has the original path and manifest-overwrite limitations. Figure rerendering remains outside the supported numerical/runtime wrappers and is documented as requiring a disposable copy to preserve historical figure provenance. The scientific and coverage limits stated above continue to apply.
