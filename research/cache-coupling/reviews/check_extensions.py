"""Read-only verification of derived moment and epsilon identities."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "results/enumeration-001.json").read_text())
errors = dict(shared_normalized_variance=0.0, centered_shared_variance=0.0,
              centered_fresh_variance=0.0, centered_variance_gap=0.0,
              epsilon_mean=0.0)


def compare(name, actual, expected):
    errors[name] = max(errors[name], abs(actual - expected))


for row in report["rows"]:
    g, p, c, q = (row[key] for key in ("group", "p", "c", "q"))
    masses = [math.comb(g, n) * p**n * (1-p)**(g-n) for n in range(g+1)]
    h = [n*(g-n)/g**2 for n in range(g+1)]
    eh = math.fsum(m*x for m, x in zip(masses, h))
    eh2 = math.fsum(m*x*x for m, x in zip(masses, h))
    vh = eh2 - eh*eh
    s = math.fsum(m*math.sqrt(x) for m, x in zip(masses, h))
    centered, normalized, stabilized = row["estimators"]
    compare("shared_normalized_variance", normalized["shared"]["update_variance"],
            (1-1/g)*p*(1-p) - (2*q-1)**2*s*s)
    compare("centered_shared_variance", centered["shared"]["update_variance"],
            q*(1-q)*eh2 + (q-c)**2*vh)
    fresh_noise = math.fsum(m*n*(g-n)**2/g**4 for n, m in enumerate(masses))
    compare("centered_fresh_variance", centered["fresh"]["update_variance"],
            q*(1-q)*fresh_noise + (q-c)**2*vh)
    gap = q*(1-q)*math.fsum(
        m*n*(n-1)*(g-n)**2/g**4 for n, m in enumerate(masses))
    compare("centered_variance_gap", centered["shared"]["update_variance"]
            - centered["fresh"]["update_variance"], gap)
    epsilon = stabilized["epsilon"]
    a = math.fsum(m*x*(1-c)/((1-c)*math.sqrt(x)+epsilon)
                 for m, x in zip(masses, h))
    b = math.fsum(m*x*c/(c*math.sqrt(x)+epsilon)
                 for m, x in zip(masses, h))
    compare("epsilon_mean", stabilized["shared"]["expected_update"], q*a-(1-q)*b)
    threshold = b/(a+b)
    assert min(c, 0.5)-1e-14 <= threshold <= max(c, 0.5)+1e-14

assert max(errors.values()) < 1e-12, errors
print(json.dumps({"checked_configurations": len(report["rows"]),
                  "maximum_absolute_errors": errors}, indent=2))
