"""Actual pinned cache stack, in-process HTTP, scripted environment, no network."""
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import json
import logging
import platform
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "work/vendor"
NETWORK_ATTEMPTS = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def forbidden(*args, **kwargs):
    NETWORK_ATTEMPTS.append("network_operation")
    raise RuntimeError("Network access disabled in runtime probe")


# socketpair for asyncio remains available; outbound sockets and DNS do not.
socket.socket.connect = forbidden
socket.socket.connect_ex = forbidden
socket.create_connection = forbidden
socket.getaddrinfo = forbidden

source_manifest = json.loads((ROOT / "results/tvcache-sources.json").read_text())
for name, checksum in source_manifest["files"].items():
    assert digest(VENDOR / name) == checksum, name
sys.path[:0] = [str(VENDOR / "tvcache/client"), str(VENDOR / "tvcache/server")]

import httpx
from tvclient.tools.tool_call_env import ToolCall, ToolCallEnv
from tvclient.tools.async_semantic_stateful_executor import AsyncSemanticStatefulExecutor
from tvcache.immutable_env_prefix_tree import ImmutableEnvPrefixTreeCache

spec = importlib.util.spec_from_file_location("audit_tvcache_server", VENDOR / "tvcache/server/tvcache_server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)
logging.disable(logging.CRITICAL)


def stop_backend(backend):
    backend.ttl_cleanup_stop_event.set()
    backend.ttl_cleanup_thread.join(timeout=2)
    assert not backend.ttl_cleanup_thread.is_alive()


stop_backend(server.cache)


class Call(ToolCall):
    def __init__(self, action, draw_id=None):
        self.action, self.draw_id = action, draw_id

    def to_dict(self):
        result = {"action": self.action}
        if self.draw_id is not None:
            result["draw_id"] = self.draw_id
        return result

    @staticmethod
    def from_dict(data):
        return Call(**data)

    def will_mutate_state(self):
        return False


class ScriptedEnv(ToolCallEnv):
    calls = []
    fixture = None

    def __init__(self, env_id=None, task_name="default_task"):
        self.env_id = env_id or task_name

    async def stop(self, **kwargs):
        return None

    async def execute(self, call, **kwargs):
        if call.action == "A":
            value = "0.9"
        else:
            index = sum(x["action"] == "B" for x in self.calls)
            value = "0.8" if self.fixture == "deterministic" else str(1 - index % 2)
        self.calls.append({"action": call.action, "draw_id": call.draw_id, "value": value})
        return value

    async def fork(self, **kwargs):
        raise AssertionError("This stateless fixture must not fork")

    async def get_state(self, **kwargs):
        return {}

    def get_id(self, **kwargs):
        return self.env_id

    async def test(self):
        raise AssertionError("Unexpected test call")

    async def hash(self):
        return "immutable-fixture"


class EmptyBank:
    def get_forked_env(self, **kwargs):
        return None


async def case(fixture, mode):
    server.cache = ImmutableEnvPrefixTreeCache()
    ScriptedEnv.calls = []
    ScriptedEnv.fixture = fixture
    flask_client = server.app.test_client(use_cookies=False)
    http_requests = []

    def transport(request):
        assert request.url.host == "localhost", request.url
        http_requests.append({"method": request.method, "path": request.url.path})
        response = flask_client.open(
            request.url.raw_path.decode("ascii"), method=request.method,
            headers=dict(request.headers), data=request.content)
        return httpx.Response(response.status_code, headers=dict(response.headers),
                              content=response.data, request=request)

    values, counters = [], []
    try:
        for rollout in range(32):
            task = f"case-{fixture}-{mode}"
            if mode == "task_namespace":
                task += f"-{rollout}"
            command = Call("A" if rollout % 2 == 0 else "B",
                           rollout if mode == "draw_identity" else None)
            if mode == "direct":
                values.append(await ScriptedEnv(task_name=task).execute(command))
                continue
            executor = AsyncSemanticStatefulExecutor(ScriptedEnv, Call, task)
            executor.set_fork_bank(EmptyBank())
            executor.client._client = httpx.AsyncClient(transport=httpx.MockTransport(transport))
            try:
                values.append(await executor.execute([command]))
                counters.append({"total_calls": executor.total_calls,
                                 "total_executions": executor.total_executions})
            finally:
                await executor.close()
        expected = []
        for i in range(32):
            if i % 2 == 0:
                expected.append("0.9")
            elif fixture == "deterministic":
                expected.append("0.8")
            elif mode == "shared":
                expected.append("1")
            else:
                expected.append(str(1 - (i // 2) % 2))
        assert values == expected, (fixture, mode, values, expected)
        assert len(ScriptedEnv.calls) == (2 if mode == "shared" else 32)
        return {"fixture": fixture, "mode": mode, "rollouts": 32,
                "returned_values": values, "physical_tool_calls": list(ScriptedEnv.calls),
                "physical_tool_call_count": len(ScriptedEnv.calls),
                "in_process_http_request_count": len(http_requests),
                "executor_total_calls": sum(c["total_calls"] for c in counters),
                "executor_total_executions": sum(c["total_executions"] for c in counters)}
    finally:
        stop_backend(server.cache)


async def main():
    rows = []
    for fixture in ("deterministic", "alternating"):
        for mode in ("direct", "shared", "task_namespace", "draw_identity"):
            rows.append(await case(fixture, mode))
    assert not NETWORK_ATTEMPTS, NETWORK_ATTEMPTS
    report = {"scope": "Unmodified executor, async client, Flask routes and backend; scripted tool; in-process HTTP",
              "revision": source_manifest["revision"], "case_count": len(rows),
              "rollout_count": sum(r["rollouts"] for r in rows),
              "network_attempts": NETWORK_ATTEMPTS, "rows": rows}
    output = ROOT / "results/runtime-002.json"
    serialized = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output.exists() and output.read_text() != serialized:
        raise RuntimeError("Refusing to overwrite different runtime results")
    output.write_text(serialized)
    paths = (ROOT / "docs/protocol-002.md", Path(__file__),
             ROOT / "src/prepare_tvcache.py", ROOT / "results/tvcache-sources.json",
             ROOT / "requirements-runtime.lock")
    manifest = {"python": platform.python_version(),
                "packages": {name: importlib.metadata.version(name) for name in
                             ("Flask", "httpx", "requests")},
                "sources": {str(p.relative_to(ROOT)): digest(p) for p in paths},
                "result_sha256": digest(output)}
    (ROOT / "results/runtime-002-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"cases": len(rows), "rollouts": report["rollout_count"],
                      "network_attempts": len(NETWORK_ATTEMPTS),
                      "physical_calls": [{"fixture": r["fixture"], "mode": r["mode"],
                                           "calls": r["physical_tool_call_count"]} for r in rows]}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
