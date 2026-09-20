# Final manuscript audit

Date: 20 September 2026. Internal automated review, not independent peer review.

## Verdict

The central mathematics is sound under the stated model. I found no substantive mathematical error, fabricated citation, unsupported numerical headline, or hidden claim of language-model training in the reviewed manuscript. The paper is a defensible, narrowly scoped analytical counterexample plus an implementation-path audit. It is not evidence of a practical training regression, a production cache defect, or a new optimizer.

An arXiv preprint is scientifically defensible with the present claim boundaries and the small clarification below. A TMLR submission is defensible after required formatting and anonymization, but acceptance cannot be predicted. The likely scientific discussion is whether the exact execution-induced coupling result teaches the intended audience enough beyond established normalization bias. More numerical sweep points would not resolve that question.

TMLR does not require a novel method or a new benchmark state of the art. Its stated criteria are supported claims and clear findings of interest to some readers. A real-model training run is therefore not a formal prerequisite for this explicitly analytical paper. Its criteria also note concerns with work generated entirely by AI with little human involvement. The author needs to personally understand and endorse the argument and evidence; an automated audit cannot substitute for that. [TMLR acceptance criteria](https://jmlr.org/tmlr/acceptance-criteria.html).

## Concrete corrections and packaging checks

1. **Qualify the affine-equivalence sentence.** In Related Work, change “Our independent-execution model is affinely equivalent to their three-reward setting” to “Our Bernoulli independent-execution model is affinely equivalent to their three-reward setting.” The paper now permits arbitrary scalar Y, for which three-reward equivalence need not hold. For the Bernoulli case the mapping is r' = (r-c)/(1-c), with error penalty lambda = c/(1-c), giving rewards 0, 1, and -lambda. The current claim is accurate for the specialization, but its scope should be explicit. [Che et al., Proposition 6 and Appendix G](https://arxiv.org/html/2608.00301v1).

2. **Anonymize the full TMLR package.** The current bylined source includes an author, affiliation, email, author footer, PDF author metadata, and an identifying GitHub link. The anonymous version must remove those identifiers and use the TMLR style. The supplement also must be anonymous. Do not include this internal audit in that supplement without reviewing its links and provenance. A bylined arXiv version is allowed, but the anonymous submission should not link to the named version or identifying artifact. The separate bylined package may retain its full provenance. [TMLR author guide](https://jmlr.org/tmlr/author-guide.html).

3. **Keep audit boundaries when moving the file inventory.** Moving the artifact map to the supplement is sensible. Preserve the adjoining paragraph that limits the runtime audit to sequential one-call rollouts and explicitly distinguishes its varying fixture from the probabilistic theorem. Otherwise the narrative loses a useful boundary on what the implementation test establishes.

4. **Normalize one manifest path in packaging or explain it in the checker.** The frozen runtime source manifest uses `work/../src/runtime_probe.py`. Its hash matches `src/runtime_probe.py` after path normalization. A naive reader in a fresh package lacking a `work` directory gets a missing-path failure before normalization, despite the correct source being present. This is a minor reproducibility issue, not a source-integrity discrepancy. If preserving the frozen manifest, ensure verification normalizes its paths before opening them.

5. **Regenerate validation for each final PDF.** Existing `paper/pdf-validation.json` describes a nine-page bylined PDF and its old checksum. It cannot certify newly generated arXiv or TMLR PDFs. New builds need their own checksums, font/text checks, and visual review. No em dash or TeX triple-hyphen was present in the reviewed manuscript source.

## Mathematical checks

- The conditional score cancellation is correct, including all-A and all-B groups. In shared groups, V = h_G(N)(Y-c), while s = w_G(N)|Y-c|, so the sign formula and tie convention follow exactly.
- Integrability is sufficient for the expected-return comparison and centered mean. The normalized update itself is bounded for almost surely finite Y, as the appendix states.
- The wrong-direction Bernoulli intervals are correctly stated. G=2 update distributions agree between modes even when all-B independent rewards differ, because the scores are then identical and centered rewards sum to zero.
- The independent asymptotic variance denominator is the correct mixture variance. The absolute update bound of 1/2 justifies convergence of first and second moments.
- The finite shared second moment and variance floor are correct. The floor is within groups and does not imply an inability to average independent groups.
- Both centered-estimator variances and the G/(G-1) baseline correction are correct.
- The positive-epsilon threshold inequalities follow from the termwise comparisons. Population/sample standard-deviation equivalence is correctly restricted to zero epsilon unless the stabilizer is also rescaled.
- No end-to-end optimization, clipping, multi-epoch, or adaptive-optimizer guarantee is inferred from these one-step identities.

## Numerical and artifact verification performed

Read the manuscript, protocols, findings, derivations, relevant source tests, frozen result files, and manifests. Re-ran the six unit-test methods successfully, including the ordered-sequence checker with 288 combinations. Re-ran `reviews/check_extensions.py` on all 540 configurations. Largest extension-identity absolute error was about 3.11e-16.

Independently recounted the stored grid: 54 opposite-sign execution-mode pairs at each epsilon, 54 independent normalized estimators opposing the expected-return gradient, and 108 shared ones. The reported precision bounds agree with the stored checks. The runtime JSON totals agree with the text: eight cases, 256 rollouts, 196 physical executions, 648 in-process HTTP requests, and no recorded network attempts.

All checked frozen source digests match after normalizing the path noted above. This audit did not rerun the vendor runtime stack or independently reproduce the claim of three byte-identical process runs. Those remain documented historical runtime results, not new runs made by this review.

## References and source claims

All seven cited paper identifiers resolved on primary arXiv pages, with matching titles and listed authors. The public artifact repository also resolved and was public at the time of inspection. No citation correction is required beyond the model-scope clarification above.

- [DeepSeekMath](https://arxiv.org/abs/2402.03300): reference identity and GRPO introduction match.
- [Understanding R1-Zero-Like Training](https://arxiv.org/abs/2503.20783): title and eight-author list match. Attribution of the existing centered control is appropriately cautious.
- [Che et al.](https://arxiv.org/html/2608.00301v1): Proposition 6 and Appendix G establish the closely related sparse-answer threshold mechanism. This manuscript explicitly acknowledges the overlap.
- [Noise-corrected GRPO](https://arxiv.org/abs/2510.18924): title and authors match; the paper has a May 2026 revision, while its first preprint year is correctly 2025. The manuscript makes only the modest reward-corruption attribution supported by its abstract.
- [Xin](https://arxiv.org/abs/2609.06386): title and single-author credit match. Its empirical dependence study is not misrepresented as a causal cache experiment.
- [TVCache](https://arxiv.org/html/2602.10986v1): Appendix B assumes output determination by state and arguments; Appendix C lists EgoSchema under importance sampling. The manuscript correctly avoids attributing GRPO to that workload or claiming the stochastic witness refutes the stated contract.
- [CacheRL](https://arxiv.org/abs/2606.14179): title/authors match; cache-aware rewards and environment-token masking support the related-work description.
- [Public artifact](https://github.com/shi1720/tool-cache-coupling): repository and source/results availability claim verified at inspection time.

This was a focused claim and reference audit, not a complete novelty search or a reproduction of the cited papers.

## Language and scientific readiness

The manuscript is clear and candid about its limits. Its title says “can,” the abstract identifies a controlled study, the centered remedy is credited as existing, and the implementation audit is separated from the probabilistic result. No added blanket disclaimer or speculative new experiment is needed to make those claims accurate.

A small optional wording improvement is to replace “one practical numerical stabilizer” with “the tested stabilizer value.” The current epsilon result is mathematically correct; the replacement avoids suggesting that 1e-4 is a verified default in a specific production implementation.

The remaining limitation is substantive scope: one constant alternative and one shared outcome admit a simple exact cancellation. The runtime audit demonstrates that sharing can occur through the chosen stack, but does not measure stochastic tool variability or expose a trained policy to the intervention. These limitations are already disclosed. Reviewers may reasonably ask for broader evidence, but that uncertainty should not be restated as an unsupported claim that the existing theorem is wrong or that a preprint cannot be released.
