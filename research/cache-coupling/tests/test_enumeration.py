"""Independent ordered-sequence oracle and closed-form controls."""
import itertools
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from enumerate_updates import expectation, shared_closed_form


def literal(actions, rewards, p, epsilon):
    mean = sum(rewards) / len(rewards)
    if max(rewards) == min(rewards):
        return 0.0
    denominator = (math.sqrt(sum((r - mean) ** 2 for r in rewards) / len(rewards))
                   + epsilon) if epsilon is not None else 1.0
    return sum((a - p) * (r - mean) / denominator
               for a, r in zip(actions, rewards)) / len(actions)


def ordered_oracle(group, p, c, q, shared, epsilon):
    total = []
    if shared:
        for y in (0, 1):
            for actions in itertools.product((0, 1), repeat=group):
                mass = (q if y else 1 - q) * math.prod(p if a else 1-p for a in actions)
                rewards = [y if a else c for a in actions]
                total.append(mass * literal(actions, rewards, p, epsilon))
    else:
        # A, B-failure, B-success form the three outcomes for each rollout.
        probabilities = (1-p, p*(1-q), p*q)
        for sequence in itertools.product((0, 1, 2), repeat=group):
            mass = math.prod(probabilities[s] for s in sequence)
            actions = [int(s != 0) for s in sequence]
            rewards = [c if s == 0 else (1 if s == 2 else 0) for s in sequence]
            total.append(mass * literal(actions, rewards, p, epsilon))
    return math.fsum(total)


class EnumerationTests(unittest.TestCase):
    def test_independent_ordered_oracle(self):
        for group, p, c, q, shared, epsilon in itertools.product(
                (2, 3, 4, 5), (0.2, 0.5), (0.3, 0.9), (0.0, 0.6, 1.0),
                (False, True), (None, 0.0, 0.0001)):
            actual = expectation(group, p, c, q, shared, epsilon)["expected_update"]
            expected = ordered_oracle(group, p, c, q, shared, epsilon)
            self.assertAlmostEqual(actual, expected, places=12)

    def test_centered_identity(self):
        for group, p, c, q, shared in itertools.product(
                (2, 8, 64), (0.1, 0.5, 0.9), (0.1, 0.9), (0.2, 0.8), (False, True)):
            result = expectation(group, p, c, q, shared, None)
            self.assertAlmostEqual(result["expected_update"],
                (1-1/group)*p*(1-p)*(q-c), places=12)

    def test_shared_formula(self):
        for group, p, c, q in itertools.product(
                (2, 8, 64), (0.1, 0.5, 0.9), (0.1, 0.9), (0.2, 0.8)):
            self.assertAlmostEqual(expectation(group, p, c, q, True, 0.0)["expected_update"],
                                   shared_closed_form(group, p, q), places=12)

    def test_group_two_mode_equivalence(self):
        for epsilon in (None, 0.0, 0.0001):
            self.assertAlmostEqual(expectation(2, .4, .9, .8, True, epsilon)["expected_update"],
                                   expectation(2, .4, .9, .8, False, epsilon)["expected_update"])

    def test_deterministic_equivalence(self):
        for q, epsilon in itertools.product((0.0, 1.0), (None, 0.0, 0.0001)):
            self.assertEqual(expectation(16, .3, .7, q, True, epsilon),
                             expectation(16, .3, .7, q, False, epsilon))

    def test_marginal_mean_and_mass(self):
        for shared in (False, True):
            result = expectation(64, .5, .9, .8, shared, 0.0)
            self.assertAlmostEqual(result["probability_mass"], 1, places=12)
            self.assertAlmostEqual(result["expected_reward"], .85, places=12)


if __name__ == "__main__":
    unittest.main()
