# Protocol 001: shared tool outcomes and group-normalized updates

Written on 2026-09-20 before executing this experiment. This is an analytical,
constructed hypothesis test, not a preregistered field study or model benchmark.

## Question

Can replacing independent stochastic tool outcomes with one outcome per tool
key per training group reverse the expected normalized policy update, while
preserving each rollout's marginal reward distribution? Does mean centering
without a random standard-deviation denominator avoid that reversal here?

## Model and estimands

An independent Bernoulli policy chooses action B with probability p. Action A
returns reward c; action B returns a Bernoulli(q) reward. There are G independent
action draws in a group. The tool result determines the terminal reward. There
are no intermediate observations, clipping, KL penalty, length weighting,
parameter updates, changing world state, stale outputs, or persistent caches.

Fresh execution draws an independent B outcome for each invocation. Shared
execution draws one B outcome for the group, independently of the actions, and
reuses it for every B invocation. Drawing on the first B miss is distributionally
equivalent. The shared result is refreshed at every group, so this experiment
does not rely on a permanently unlucky cache. A is deterministic in both modes.

For the logit of p, the score is a_i - p. Compute the expected ascent update

    U = (1/G) sum_i (a_i - p) (r_i - mean(r)) / (std_pop(r) + epsilon)

and its centered-only control, without the denominator. A constant-reward group
has update zero, including when epsilon is zero. Positive updates increase B.
The expected-return gradient is p(1-p)(q-c).

Enumerate every action count n and, for fresh execution, B success count k.
Weight n by Binomial(G,p), k by Binomial(n,q). Under sharing, k is either zero
or n, weighted by 1-q and q. This is exhaustive finite summation with floating
point arithmetic, not Monte Carlo. Report normalization mass and moments as
well as update means and variances.

## Fixed sweep and controls

- G in {2,4,8,16,32,64}; p in {0.1,0.5,0.9}.
- c in {0.1,0.3,0.5,0.7,0.9}; q in {0,0.2,0.4,0.6,0.8,1}.
- Both execution modes; normalized epsilon in {0,0.0001}; centered-only control.
- 540 environment/policy/group configurations, six estimators per configuration.
- Deterministic q=0 or 1 must give equal updates across execution modes.
- G=2 must give equal updates across modes, including epsilon=0.0001.
- Centered expectations must equal (1-1/G)p(1-p)(q-c) in both modes.
- Marginal mean rewards must equal (1-p)c+pq in both modes.
- For epsilon=0 and 0<c<1, shared expected update must equal
  (2q-1) E[sqrt(n(G-n))/G], independent of c.
- Independently enumerate ordered action/outcome sequences for small groups,
  using the literal per-rollout score expression, to check the count reduction.

The anticipated witness is p=0.5, c=0.9, q=0.8 with sufficiently large G:
fresh execution should prefer A, while shared execution should prefer B.
This witness was selected analytically before execution. Report all sweep
points, including cases with no reversal and cases where both modes disagree
with the expected-return gradient. Do not call sweep points independent trials
or use their fraction as a population prevalence estimate.

## Interpretation gate

An effect is not proof of a new contribution. Group normalization bias is known
from Dr. GRPO and reward-noise literature. This test isolates a cache-induced
change in the joint sampling law, rather than claiming that caching or
normalization bias has just been discovered. It is outside a deterministic-tool
cache contract and cannot refute such a contract or a published benchmark.
If the controls fail, debug and record the correction before interpreting
results. Real training evidence and a stronger prior-art comparison are required
before any paper-level claims.
