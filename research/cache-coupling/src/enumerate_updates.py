"""Finite-sum experiment. No LLM, sampling, network, or vendor implementation."""
import hashlib
import itertools
import json
import math
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUPS = (2, 4, 8, 16, 32, 64)
PROBS = (0.1, 0.5, 0.9)
CONSTANTS = (0.1, 0.3, 0.5, 0.7, 0.9)
SUCCESS = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
ESTIMATORS = (("centered", None), ("normalized", 0.0), ("normalized", 0.0001))


def binomial(n, k, probability):
    return math.comb(n, k) * probability ** k * (1 - probability) ** (n - k)


def outcomes(group, p, q, shared):
    """Yield (B count, successful B count, probability)."""
    for n in range(group + 1):
        action_mass = binomial(group, n, p)
        if n == 0:
            yield n, 0, action_mass
        elif shared:
            yield n, 0, action_mass * (1 - q)
            yield n, n, action_mass * q
        else:
            for k in range(n + 1):
                yield n, k, action_mass * binomial(n, k, q)


def update(group, n, k, c, epsilon):
    mean = ((group - n) * c + k) / group
    # Center before summing squares to avoid subtracting nearly equal moments.
    variance = ((group - n) * (c - mean) ** 2
                + k * (1 - mean) ** 2 + (n - k) * mean ** 2) / group
    numerator = (group - n) * (k - n * c) / group ** 2
    if epsilon is None:
        return numerator, mean
    if n in (0, group):
        # All scores identical, so the centered numerator is exactly zero.
        return 0.0, mean
    denominator = math.sqrt(variance) + epsilon
    return (numerator / denominator if denominator else 0.0), mean


def expectation(group, p, c, q, shared, epsilon):
    values = [(mass, *update(group, n, k, c, epsilon))
              for n, k, mass in outcomes(group, p, q, shared)]
    expected_update = math.fsum(mass * u for mass, u, _ in values)
    return {
        "probability_mass": math.fsum(mass for mass, _, _ in values),
        "expected_update": expected_update,
        "update_variance": math.fsum(mass * (u - expected_update) ** 2
                                     for mass, u, _ in values),
        "expected_reward": math.fsum(mass * r for mass, _, r in values),
    }


def shared_closed_form(group, p, q):
    return (2 * q - 1) * math.fsum(
        binomial(group, n, p) * math.sqrt(n * (group - n)) / group
        for n in range(group + 1))


def signed(value):
    return 1 if value > 1e-12 else (-1 if value < -1e-12 else 0)


def run():
    rows = []
    max_mass_error = max_reward_error = max_centered_error = 0.0
    max_deterministic_difference = max_g2_difference = max_formula_error = 0.0
    comparisons = {str(e): {"opposite_update_signs": 0,
                           "fresh_opposes_return_gradient": 0,
                           "shared_opposes_return_gradient": 0}
                   for _, e in ESTIMATORS}
    for group, p, c, q in itertools.product(GROUPS, PROBS, CONSTANTS, SUCCESS):
        target = p * (1 - p) * (q - c)
        row = {"group": group, "p": p, "c": c, "q": q,
               "return_gradient": target, "estimators": []}
        for name, epsilon in ESTIMATORS:
            fresh = expectation(group, p, c, q, False, epsilon)
            shared = expectation(group, p, c, q, True, epsilon)
            for result in (fresh, shared):
                max_mass_error = max(max_mass_error, abs(result["probability_mass"] - 1))
                max_reward_error = max(max_reward_error,
                                       abs(result["expected_reward"] - ((1-p)*c+p*q)))
                if epsilon is None:
                    max_centered_error = max(max_centered_error,
                        abs(result["expected_update"] - (1 - 1/group) * target))
            difference = abs(fresh["expected_update"] - shared["expected_update"])
            if q in (0, 1):
                max_deterministic_difference = max(max_deterministic_difference, difference)
            if group == 2:
                max_g2_difference = max(max_g2_difference, difference)
            if epsilon == 0.0:
                max_formula_error = max(max_formula_error,
                    abs(shared["expected_update"] - shared_closed_form(group, p, q)))
            f, s, t = map(signed, (fresh["expected_update"], shared["expected_update"], target))
            counts = comparisons[str(epsilon)]
            counts["opposite_update_signs"] += int(f * s < 0)
            counts["fresh_opposes_return_gradient"] += int(f * t < 0)
            counts["shared_opposes_return_gradient"] += int(s * t < 0)
            row["estimators"].append({"name": name, "epsilon": epsilon,
                                      "fresh": fresh, "shared": shared})
        rows.append(row)
    checks = {
        "max_probability_mass_error": max_mass_error,
        "max_marginal_reward_error": max_reward_error,
        "max_centered_formula_error": max_centered_error,
        "max_deterministic_mode_difference": max_deterministic_difference,
        "max_group_two_mode_difference": max_g2_difference,
        "max_shared_normalized_formula_error": max_formula_error,
    }
    assert all(value < 1e-12 for value in checks.values()), checks
    return {"scope": "Constructed one-step bandit; exhaustive weighted sums, floating arithmetic",
            "configuration_count": len(rows), "estimator_count": len(rows) * 6,
            "checks": checks, "comparisons": comparisons, "rows": rows}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / "results" / "enumeration-001.json"
    output.parent.mkdir(exist_ok=True)
    report = run()
    serialized = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if output.exists() and output.read_text() != serialized:
        raise RuntimeError("Refusing to overwrite a different frozen result")
    output.write_text(serialized)
    manifest = {"protocol": "001", "python": platform.python_version(),
                "sources": {str(path.relative_to(ROOT)): digest(path) for path in (
                    ROOT / "docs/protocol-001.md", Path(__file__),
                    ROOT / "tests/test_enumeration.py")},
                "result_sha256": digest(output)}
    (ROOT / "results/manifest-001.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
