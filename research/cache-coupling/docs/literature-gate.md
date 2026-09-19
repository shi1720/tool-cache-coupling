# Focused literature gate, 2026-09-20

## Why the preceding cache-recovery idea is insufficient

[TVCache](https://arxiv.org/html/2602.10986v1) handles stateful tool-value reuse
through trajectory matching and sandbox restoration. Appendix B explicitly
assumes outputs are determined by state and arguments. Our stochastic witness
is outside that assumption, not a refutation. Its training setting motivates
checking statistical coupling separately from state consistency.

[Tool Cache Agent](https://openreview.net/pdf?id=tX3YcbNa5w) describes tool-specific
cache plans, expiration and inter-tool invalidation. The abstract and indexed
excerpts were available; direct PDF retrieval hit a browser challenge. It is
sufficient overlap to reject generic dependency-aware cache planning as our
novel contribution, but not enough for a full methods comparison.

[AgentCheck](https://arxiv.org/html/2607.11098v1) already implements MCP fault
interventions and mitigation testing, including stale responses. A new fault
wrapper alone would not establish novelty.

## Closest work to the stochastic-sharing experiment

| Source | Established overlap | Consequence for our claims |
|---|---|---|
| [Understanding R1-Zero-Like Training](https://arxiv.org/html/2503.20783v1), section 3 | Group standard-deviation scaling changes training weights; removing it is an existing method. | Neither normalization bias nor the centered control is new. |
| [Abstention as an Action](https://arxiv.org/html/2608.00301v1), Proposition 6 and Appendix G | Sparse-action normalization erases reward magnitude and shifts the preference threshold. | Our fresh bandit is affinely equivalent to its reward structure; the candidate distinction is cache-induced sharing at non-sparse frequencies. |
| [Noise-corrected GRPO](https://arxiv.org/html/2510.18924v1), noise model | Explicit reward corruption and corrected policy-gradient estimators. | Do not claim the first treatment of noisy rewards. Our fixture uses valid stochastic outcomes, not incorrect labels. |
| [Are Verifier Errors Independent Within a GRPO Group?](https://arxiv.org/html/2609.06386v1), discussion and limitations | Empirical within-group dependence and advantage changes; causal interpretation is carefully limited. | Dependence affecting group-based training is already studied. Our intervention controls the coupling directly in a toy model, without verifier error. |
| [CacheRL](https://arxiv.org/html/2606.14179v1), CacheAgentLoop | Cached training rollouts, environment-token masking and cache-aware reward design. | Neither training with cached tools nor handling cache-related training limitations is new. |

## Current gate

**Hold, not novelty established.** The precise shared-outcome calculation is
worth preserving. It has not been shown to exceed an application of known
normalization bias in a realistic training system. No broad absence-of-prior-art
claim follows from these searches. Remaining discriminating evidence is actual
stochastic tool behavior, measured reuse patterns, and matched training or
gradient comparisons against existing estimators under equal tool-call budgets.

Source status matters: main methods and Appendix B were read for TVCache;
selected relevant sections were read for the other primary papers. This file
does not claim a complete review of every paper or reproduction of its results.
