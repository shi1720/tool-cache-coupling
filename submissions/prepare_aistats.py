"""Prepare a candidate AISTATS 2027 manuscript, not a submission receipt."""
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/cache-coupling"
TEMPLATE = ROOT / "submissions/templates/AISTATS2027PaperPack"
OUT = ROOT / "submissions/aistats"
OUT.mkdir(exist_ok=True)
source = (BASE / "paper/manuscript.tex").read_text()
macros = source[source.index(r"\newtheorem{theorem}"):source.index(r"\title{")]
body = source[source.index(r"\begin{abstract}"):]
body = body.replace("../results/shared-outcome-updates.pdf", "shared-outcome-updates.pdf")
body = body.replace(
    "The public artifact, including source and numerical\nresults, is available at \\url{https://github.com/shi1720/tool-cache-coupling}.",
    "The anonymized supplement contains the code, protocols, numerical results, "
    "and environment manifests. All reported experiments run on a local CPU; "
    "no GPU or cloud service is used.",
)
# Use full-width floats for the comparison tables and three-panel figure.
for env in ("table", "figure"):
    body = body.replace(r"\begin{" + env + "}[ht]", r"\begin{" + env + "*}[t]")
    body = body.replace(r"\end{" + env + "}", r"\end{" + env + "*}")
# The venue requires references in the body font size.
body = body.replace("\\begin{thebibliography}{9}\n\\small", "\\begin{thebibliography}{9}")
body = body.replace(
    r"\texttt{3a4f95a6582eea1e4b7e84a9f3a0c74eaa8fde02}",
    r"\texttt{3a4f95a6582e}\allowbreak\texttt{ea1e4b7e84a9}\allowbreak\texttt{f3a0c74eaa8fde02}",
)
# Break displays at mathematical boundaries without changing their contents.
body = body.replace(
    "J(\\theta)=(1-p)c+p\\mu,\\qquad\nJ'(\\theta)=p(1-p)(\\mu-c).",
    "\\begin{gathered}J(\\theta)=(1-p)c+p\\mu,\\\\\nJ'(\\theta)=p(1-p)(\\mu-c).\\end{gathered}",
)
body = body.replace(
    "w_G(n)=\\frac{\\sqrt{n(G-n)}}{G},\\quad\nh_G(n)=w_G(n)^2,\\quad S_G(p)=\\E[w_G(N)].",
    "\\begin{gathered}w_G(n)=\\frac{\\sqrt{n(G-n)}}{G},\\quad h_G(n)=w_G(n)^2,\\\\\nS_G(p)=\\E[w_G(N)].\\end{gathered}",
)
body = body.replace(
    "U_0=w_G(N)\\sgn(Y-c),\\qquad\n\\E[U_0]=S_G(p)\\bigl(\\Pr(Y>c)-\\Pr(Y<c)\\bigr),",
    "\\begin{gathered}U_0=w_G(N)\\sgn(Y-c),\\\\\n\\E[U_0]=S_G(p)\\bigl(\\Pr(Y>c)-\\Pr(Y<c)\\bigr),\\end{gathered}",
)
body = body.replace(
    "\\Var(U_{0,\\ind})&\\longrightarrow0,\\qquad\n\\Var(U_{0,\\shr})\\longrightarrow4q(1-q)p(1-p).",
    "\\Var(U_{0,\\ind})&\\longrightarrow0,\\nonumber\\\\\n\\Var(U_{0,\\shr})&\\longrightarrow4q(1-q)p(1-p).",
)
body = body.replace(
    "\\Var(U_{0,\\shr})=(1-1/G)p(1-p)-(2q-1)^2S_G(p)^2.",
    "\\begin{aligned}\\Var(U_{0,\\shr})={}&(1-1/G)p(1-p)\\\\\n&-(2q-1)^2S_G(p)^2.\\end{aligned}",
)
body = body.replace(
    "A_\\epsilon=\\E\\!\\left[\\frac{h_G(N)(1-c)}{w_G(N)(1-c)+\\epsilon}\\right],\\qquad\nB_\\epsilon=\\E\\!\\left[\\frac{h_G(N)c}{w_G(N)c+\\epsilon}\\right].",
    "\\begin{aligned}A_\\epsilon&=\\E\\!\\left[\\frac{h_G(N)(1-c)}{w_G(N)(1-c)+\\epsilon}\\right],\\\\\nB_\\epsilon&=\\E\\!\\left[\\frac{h_G(N)c}{w_G(N)c+\\epsilon}\\right].\\end{aligned}",
)

# Reuse the audited disclosure. Do not assert an unverified human review.
tmlr = (ROOT / "submissions/tmlr/manuscript.tex").read_text()
statement = tmlr[tmlr.index(r"\section*{AI use statement}"):tmlr.index(r"\bibliographystyle")]
statement = statement.replace(r"\section*{AI use statement}", r"\subsection*{AI Use Statement}")
statement = statement.replace(
    "The runtime fixtures are\nscripted controls, not sampled language-model outputs.",
    "AI assistance also covered construction of the scripted synthetic runtime "
    "fixtures. These controls are not sampled language-model outputs. "
    "Translation, data cleaning, qualitative data analysis, surveys, interviews, "
    "and transcription are not part of this study.",
)
body = body.replace(r"\begin{thebibliography}{9}", statement + r"\begin{thebibliography}{9}")

# Preserve every official checklist question verbatim, supplying candid answers.
sample = (TEMPLATE / "sample_paper.tex").read_text()
checklist = sample[sample.index(r"\begin{enumerate}", sample.index(r"\section*{Checklist}")):]
checklist = checklist[:checklist.index(r"\clearpage")].strip()
answers = [
    "Yes. Sections 3 and 4 define the laws, independence assumptions, and estimators.",
    "No. Physical call counts and finite sums are given, but no general time or space complexity analysis is claimed.",
    "Yes. The anonymized code supplement includes exact runtime dependencies and reproduction instructions.",
    "Yes. Section 4 states the hypotheses for each result.",
    "Yes. Section 4 and Appendices A--C contain the proofs and endpoint arguments.",
    "Yes. Sections 3 and 7 discuss independence, cache lifetime, and the model's scope.",
    "Yes. The supplement includes the finite-sum outputs, runtime traces, code, and protocols.",
    "Not Applicable. No model is trained; Section 5 specifies all enumeration parameters.",
    "Yes. Sections 3 and 5 define the statistics. Exhaustive sums and scripted traces have no sampling error bars.",
    "Yes. Section 7 identifies local CPU execution; environment manifests specify the runtime and platform.",
    "Yes. Section 6 and the references identify TVCache and its pinned source revision.",
    "Yes. Original artifact code and documentation use the MIT license. The retrieved TVCache package is Apache-2.0 licensed and is not redistributed in the supplement.",
    "Yes. The anonymized supplement includes the new code and generated results.",
    "Not Applicable. No participant or private third-party dataset is used.",
    "Not Applicable. The experiments contain no personal or offensive content.",
    "Not Applicable. No crowdsourcing or human-subject study was conducted.",
    "Not Applicable. No human-subject study was conducted.",
    "Not Applicable. No participants were recruited or compensated.",
]
assert checklist.count("[Yes/No/Not Applicable]") == len(answers)
for answer in answers:
    checklist = checklist.replace("[Yes/No/Not Applicable]", "[" + answer + "]", 1)
appendix = r"""\clearpage
\section*{Checklist}
""" + checklist + r"""
\clearpage
\appendix
\onecolumn
\aistatstitle{Marginally Correct Tool Caches Can Reverse\\ Group-Normalized Policy Updates: Supplementary Material}
"""
body = body.replace("\\clearpage\n\\appendix", appendix)

preamble = r"""\documentclass[twoside]{article}
\usepackage{aistats2027}
\usepackage{amsmath,amssymb,amsthm,booktabs,graphicx,array}
\usepackage{hyperref,url}
\hypersetup{hidelinks,pdftitle={Marginally Correct Tool Caches Can Reverse Group-Normalized Policy Updates},pdfauthor={}}
\setlength{\emergencystretch}{1em}
\setlength{\pdfpageheight}{11in}
\setlength{\pdfpagewidth}{8.5in}
"""
text = preamble + macros + r"""\begin{document}
\twocolumn[
\aistatstitle{Marginally Correct Tool Caches Can Reverse\\ Group-Normalized Policy Updates}
\aistatsauthor{Anonymous authors}
\aistatsaddress{Anonymous institution}]
""" + body
assert not re.search("Shivam|shivam|shi1720|/Users/|\u2014", text)
(OUT / "manuscript.tex").write_text(text)
for name in ("aistats2027.sty", "fancyhdr.sty"):
    shutil.copy2(TEMPLATE / name, OUT / name)
shutil.copy2(BASE / "results/shared-outcome-updates.pdf", OUT / "shared-outcome-updates.pdf")
print("Prepared anonymous AISTATS 2027 source with official checklist.")
