# Findings 002: implementation bridge

Eight controlled cases completed, comprising 256 scripted one-call rollouts.
Of these, 64 called the local environment directly; 192 passed through the
unmodified pinned cache stack. There were 196 physical tool executions in total.
These are not LLM rollouts or independent experimental replicates.

| Mode | Physical calls per 32 rollouts | Varying B results | Deterministic control |
|---|---:|---|---|
| Direct | 32 | Alternating 1, 0 | Original outputs |
| Shared identity | 2 | Sixteen copies of first result, 1 | Original outputs |
| Separate task namespace | 32 | Alternating 1, 0 | Original outputs |
| Separate draw identity | 32 | Alternating 1, 0 | Original outputs |

Three full runs in separate Python processes produced byte-identical result JSON.
All 29 exported source files passed SHA-256 checks before import. Socket
connection and DNS guards recorded zero attempts. The actual async client used
an HTTPX mock transport routed into the actual Flask endpoints and prefix-tree
backend. No vendor method body was edited. No real network listener, video
pipeline, external model, sandbox fork, concurrent request, or training run was
used. The fake environment and empty fork bank are explicit test fixtures.

## Source grounding

Repository: [TVCache/TVCache](https://github.com/TVCache/TVCache), revision
`3a4f95a6582eea1e4b7e84a9f3a0c74eaa8fde02`. The cache package contains an Apache
2.0 license. Third-party source exports remain in ignored work storage; the
committed manifest and preparation script allow exact retrieval.

- [Executor lines 217-229](https://github.com/TVCache/TVCache/blob/3a4f95a6582eea1e4b7e84a9f3a0c74eaa8fde02/tvcache/client/tvclient/tools/async_semantic_stateful_executor.py#L217-L229)
  return the stored value after a matching task and serialized stateful chain.
- [Video tool identity and annotations](https://github.com/TVCache/TVCache/blob/3a4f95a6582eea1e4b7e84a9f3a0c74eaa8fde02/train/tvc_agent_loop.py#L16-L36)
  serialize function and arguments; loading and preprocessing are the operations
  marked as state-changing.
- [Caption tool](https://github.com/TVCache/TVCache/blob/3a4f95a6582eea1e4b7e84a9f3a0c74eaa8fde02/video-agent-tools/VideoAgent/tools.py#L89-L114)
  calls a caption generator. Its
  [request site](https://github.com/TVCache/TVCache/blob/3a4f95a6582eea1e4b7e84a9f3a0c74eaa8fde02/video-agent-tools/VideoAgent/captioning.py#L170-L196)
  invokes a model API without an explicit seed or temperature argument there.
  This is a reason to measure output variability, not evidence of a measured
  variance, a particular default, or degraded benchmark results.

## Interpretation

The runtime test connects the analytical sharing intervention to a concrete
implementation path. It does not establish that the paper's deterministic
assumption is violated in its reported experiments. The scripted stream does
not estimate Bernoulli probabilities or verify marginal equality; those claims
are confined to the separate analytical model. Distinct identities disable the
sharing but also give up the reuse, so they are controls, not a cost-free fix or
new caching algorithm.

## Next decision, not an experiment claim

Before training a model, require a representative stochastic tool workload with
measured repeated-call distributions and useful reuse. Compare the original
normalizer and existing centered estimators at both equal rollout and equal
physical-tool budgets. Split any model/prompt selection from evaluation.
Abandon the paper direction if only the known normalization remedy explains
the result and no practically important new systems finding remains.
