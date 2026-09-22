"""Portable checks must reject scientific or structural changes, not just roundoff."""
import importlib.util
import math
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("reproduce_portable", Path(__file__).resolve().parents[1] / "src/reproduce.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PortableComparisonTests(unittest.TestCase):
    def test_libm_roundoff_is_reported(self):
        expected = {"rows": [{"expected_update": 0.3, "count": 54}], "scope": "fixed"}
        actual = {"rows": [{"expected_update": math.nextafter(0.3, 1.0), "count": 54}], "scope": "fixed"}
        report = module.compare_numerical(expected, actual)
        self.assertEqual(report["rounded_values"], 1)
        self.assertGreater(report["max_absolute_difference"], 0)

    def test_structure_and_discrete_results_are_exact(self):
        for expected, actual in [
            ({"count": 54}, {"count": 55}),
            ({"count": 54}, {"count": 54.0}),
            ({"count": 1}, {"count": True}),
            ({"count": 54}, {"count": 54, "extra": 0}),
            ([1, 2], [2, 1]), ([1], [1, 2]), ("scope", "other"),
        ]:
            with self.subTest(expected=expected, actual=actual), self.assertRaises(RuntimeError):
                module.compare_numerical(expected, actual)

    def test_substantive_numeric_differences_and_nonfinite_values_fail(self):
        for actual in [0.301, float("nan"), float("inf")]:
            with self.subTest(actual=actual), self.assertRaises(RuntimeError):
                module.compare_numerical({"expected_update": 0.3}, {"expected_update": actual})
        with self.assertRaises(RuntimeError):
            module.compare_numerical(float("nan"), float("nan"))

    def test_even_roundoff_cannot_cross_the_studys_sign_boundary(self):
        for field in ["expected_update", "return_gradient"]:
            for a, b in [(1e-12, 1.0000001e-12), (-1e-12, -1.0000001e-12)]:
                with self.subTest(field=field, a=a), self.assertRaises(RuntimeError):
                    module.compare_numerical({field: a}, {field: b})

    def test_runtime_cannot_use_portable_comparison(self):
        with self.assertRaises(ValueError):
            module.reproduce("runtime", portable=True)


if __name__ == "__main__":
    unittest.main()
