# What changes when a stochastic result is shared?

This is a derivation for protocol 001, not a claim to have discovered policy
gradient bias or a new optimization algorithm.

Let n be the number of B actions among G independent Bernoulli(p) choices, and
k the number of their successful outcomes. A has deterministic reward c. The
group mean is m=((G-n)c+k)/G. For the logit of p, each policy score is a_i-p.
Because centered rewards sum to zero, the p term cancels. Thus

    U_centered = (G-n)(k-nc)/G².

Its expectation conditional on n is n(G-n)(q-c)/G² under either execution
mode, since both have E[k|n]=nq. Using E[n(G-n)]=G(G-1)p(1-p) gives

    E[U_centered] = (1-1/G)p(1-p)(q-c).

This is the usual self-including baseline factor. Sharing changes its variance,
but not its expectation in this specific model. It is not a general claim about
adaptive caches, clipping, or arbitrary multi-turn agents.

For fresh execution, k|n is Binomial(n,q). For shared execution, k=nY with
Y~Bernoulli(q) independent of n. When 0<n<G, the latter group has just two
reward values, c and Y. Its standard deviation is

    sigma_shared = |Y-c| sqrt(n(G-n))/G.

For epsilon=0 and 0<c<1, division cancels the reward gap magnitude:

    U_shared = sign(Y-c) sqrt(n(G-n))/G.

Constant-action groups contribute zero. Therefore, for every finite G>=2,

    E[U_shared] = (2q-1) sum_n BinomialPMF(n;G,p) sqrt(n(G-n))/G.

For p strictly between zero and one the sum is positive. The shared update
changes direction at q=1/2, regardless of c. The expected-return gradient
changes direction at q=c. In the region 1/2<q<c<1, increasing B lowers expected
return but the shared normalized update increases it.

This does not mean fresh group normalization is unbiased. In fact G=2 has
identical expected updates in both modes: a group with both actions has only one
B outcome. Some finite-G fresh updates point the wrong way too. Protocol 001
reports those cases rather than using fresh execution as a universally correct
oracle.

For fixed interior p and 0<q<1, as G grows the fresh sample moments converge to

    mean = (1-p)c+pq,
    variance = p q(1-q) + p(1-p)(q-c)²,

so its normalized update converges to

    p(1-p)(q-c) / sqrt(p q(1-q) + p(1-p)(q-c)²).

The shared update instead converges to (2q-1)sqrt(p(1-p)). These limits also
hold in expectation: by Cauchy-Schwarz, the absolute sample update is at most
sqrt(p_hat(1-p_hat))<=1/2, giving a uniform dominating bound. The two limits
have opposite signs throughout the region above. Larger rollout groups alone
cannot restore independent tool outcome sampling.

## Relationship to prior results

[Che et al., Proposition 6 and Appendix G](https://arxiv.org/html/2608.00301v1)
already establish reward-magnitude cancellation for sparse non-abstention under
group normalization. Our fresh model is an affine transformation of their
three-reward setting: subtract c, then divide by 1-c, giving rewards
0, +1, and -c/(1-c). The shared calculation makes the two-level reward structure
hold at every interior action frequency, not only in a sparse-action limit.
This connection materially limits novelty. The candidate contribution would
have to be the execution-induced coupling and its practical measurement, not
the cancellation identity or removal of normalization.

## A useful conditional interpretation

A random cache realization C defines a deterministic reward map in this model.
Conditional on C, the action samples remain independent. For large groups,
normalization first divides the conditional gradient by the conditional reward
standard deviation and then averages over C. Fresh execution instead averages
the tool noise within the group before normalizing. These operations generally
do not commute. In practical terms, a cache can change the relative weight of
possible tool outcomes without changing their marginal frequency.

This is a specialization of known normalization and sampling principles. It is
not a proof that a deterministic cache is incorrect, that a particular library
has this problem in its benchmarks, or that a language model was trained here.
