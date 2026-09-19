# Findings 001

The fixed sweep completed 540 configurations and 3,240 expected-update
calculations. Each is a finite probability-weighted sum, not a sampled trial.
There are no live model calls or parameter updates in this experiment.

## Primary witness

Action A returns 0.9. Action B returns 1 with probability 0.8 and zero otherwise.
The policy initially chooses each action with probability 0.5. Both execution
modes have mean reward 0.85 and true expected-return gradient -0.025.

| Group size | Fresh normalized update | Shared normalized update | Centered update, either mode |
|---:|---:|---:|---:|
| 2 | 0.150000 | 0.150000 | -0.012500 |
| 4 | 0.187129 | 0.242404 | -0.018750 |
| 8 | 0.111526 | 0.278348 | -0.021875 |
| 16 | 0.005998 | 0.290118 | -0.023438 |
| 32 | -0.059543 | 0.295196 | -0.024219 |
| 64 | -0.078867 | 0.297628 | -0.024609 |

Positive updates increase the worse-mean action B. The normalized columns use
population standard deviation and epsilon=0. At G=32 and G=64 the modes point
in opposite directions. At smaller groups both can point the wrong way.
The cache is refreshed every group; persistence across training is unnecessary
for this witness. Adding epsilon=0.0001 retains the sign reversal.

## Complete sweep

There are 54 opposite-sign mode comparisons among 540 configurations at each
tested epsilon. Fresh normalization opposes the expected-return gradient in
54 configurations; shared normalization does so in 108. Centering alone has
neither discrepancy. These are descriptive counts on a deliberately chosen
grid, not failure prevalence or independent statistical replicates.

## Verification

Six test methods pass. An independent literal, ordered-sequence oracle checks
288 small-group combinations against the count-based calculation. Deterministic
tool controls and G=2 mode comparisons agree exactly. Across the full sweep,
probability mass error is below 3.4e-15, mean reward error below 1.8e-15, centered
identity error below 3.4e-16, and shared normalized formula error below 8.4e-17.

## Decision

This is a reproducible candidate mechanism, not a finished research contribution.
The mathematical relation to existing group-normalization work is close. The
existing centered estimator already repairs the sign in this model. Further
work is justified only by evidence that actual stochastic tool sharing creates
an important, previously unmeasured training effect. Do not expand the numerical
sweep simply to make the artifact look larger. No conference-readiness,
patentability, real-model degradation, or vendor defect is established here.
