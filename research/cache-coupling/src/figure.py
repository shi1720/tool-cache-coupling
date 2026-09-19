"""Plot only frozen results after validating their protocol and code hashes."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads((ROOT / "results/manifest-001.json").read_text())
source = ROOT / "results/enumeration-001.json"
assert digest(source) == manifest["result_sha256"]
for path, checksum in manifest["sources"].items():
    assert digest(ROOT / path) == checksum, path
report = json.loads(source.read_text())
rows = [r for r in report["rows"] if r["p"] == .5 and r["c"] == .9 and r["q"] == .8]
groups = [r["group"] for r in rows]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "none", "pdf.fonttype": 42})
fig, axes = plt.subplots(1, 2, figsize=(11, 4.9))
for ax, index, title in zip(axes, (1, 0),
                           ("Group-normalized update", "Centered-only control")):
    ax.axhline(0, color="#8d98a4", linewidth=.8)
    for mode, color, marker, label in (
            ("fresh", "#1c6688", "o", "Independent tool outcomes"),
            ("shared", "#bb4e35", "s", "One shared outcome per group")):
        vals = [r["estimators"][index][mode]["expected_update"] for r in rows]
        ax.plot(groups, vals, color=color, marker=marker, linewidth=2,
                markersize=6, label=label,
                linestyle="--" if mode == "shared" else "-")
    ax.set_xscale("log", base=2)
    ax.set_xticks(groups, [str(g) for g in groups])
    ax.set_xlabel("Rollouts per group")
    ax.set_title(title, loc="left", fontweight="bold", pad=12)
    ax.set_ylabel("Expected ascent update to B's logit")
    ax.grid(axis="y", alpha=.15)
axes[0].set_ylim(-.12, .35)
axes[1].set_ylim(-.028, .003)
axes[0].annotate("B has lower expected reward", xy=(32, .23), fontsize=9,
                 ha="center", color="#7a3423")
axes[1].annotate("Both execution modes coincide", xy=(16, -.015), fontsize=9,
                 ha="center", color="#25495b")
fig.suptitle("Sharing stochastic tool results can reverse the update", x=.065,
             ha="left", fontsize=15, fontweight="bold", y=.99)
fig.text(.065, .90, "Constructed bandit: A always returns 0.9; B succeeds with probability 0.8. Initial P(B) = 0.5.",
         fontsize=10)
fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=2,
           frameon=False, bbox_to_anchor=(.5, .04))
fig.text(.065, .015, "Exact finite sums in floating arithmetic. Mean reward is 0.85 in both modes. No language model was trained.",
         fontsize=9, color="#4d5965")
fig.subplots_adjust(left=.075, right=.98, top=.79, bottom=.25, wspace=.30)
paths = []
for extension in ("png", "pdf"):
    output = ROOT / "results" / ("shared-outcome-updates." + extension)
    metadata = {"CreationDate": None, "ModDate": None} if extension == "pdf" else {}
    fig.savefig(output, dpi=180, metadata=metadata)
    paths.append(output)
plt.close(fig)
(ROOT / "results/figure-provenance.json").write_text(json.dumps({
    "input_sha256": digest(source), "script_sha256": digest(Path(__file__)),
    "matplotlib": matplotlib.__version__,
    "outputs": {p.name: digest(p) for p in paths}}, indent=2, sort_keys=True) + "\n")
print("Rendered", ", ".join(p.name for p in paths))
