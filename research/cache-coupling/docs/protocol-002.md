# Protocol 002: pinned executor and cache runtime

Written after protocol 001 and source inspection, before running this follow-up.
This is explicitly adaptive implementation work.

Pin TVCache at 3a4f95a6582eea1e4b7e84a9f3a0c74eaa8fde02. Execute its unmodified
AsyncSemanticStatefulExecutor, async HTTP client, Flask routes and
ImmutableEnvPrefixTreeCache. Replace only the HTTP transport with an in-process
bridge to Flask's test client and implement the provided environment interface
with a local scripted tool. Block socket connections and DNS resolution.
Do not execute video tools, download model weights, invoke model APIs, or train.

Each case contains 32 sequential one-call rollouts, alternating A and B. A
returns the string "0.9". For the deterministic control, B returns "0.8";
for the varying fixture, actual B executions alternate "1" and "0" starting
with "1". The stream is deliberately scripted, not a probabilistic sample.

Compare four modes with a new backend and fresh stream per case:

1. Direct tool execution without the cache.
2. Actual executor, same task and tool identity across all rollouts.
3. Actual executor, distinct task namespace per rollout.
4. Actual executor, same task, distinct draw identifier in tool arguments.

Use a fresh executor for each rollout but share the cache backend within a case.
All tools report no sandbox mutation. No forks are required; a fork request is
an assertion failure. Stop cleanup threads after each case. No concurrent
misses, eviction, expiry, multi-step trajectories, restored sandbox, or network
server is tested.

Record the full returned sequence, physical tool calls, executor counters,
in-process HTTP request count and blocked network attempts. Expect 32 physical
tool calls in direct and identity-separated modes, and two in shared mode.
For the varying stream, only shared mode should collapse the returned B values
to the first result. All modes should agree for the deterministic control.

This establishes a concrete implementation path for result sharing. It cannot
show output variability of a real caption model, equal marginal rewards from
eight scripted cases, a vendor benchmark failure, or real training degradation.
Numerical probability claims belong to protocol 001, not this runtime fixture.
