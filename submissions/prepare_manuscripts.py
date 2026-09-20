"""Build source packages from one reviewed manuscript; no website submission."""
from pathlib import Path
import re, shutil, zipfile
ROOT = Path(__file__).resolve().parents[1]
base = ROOT / 'research/cache-coupling'
source = base / 'paper/manuscript.tex'
s = source.read_text()
for mode in ('arxiv', 'tmlr'):
 out = ROOT / 'submissions' / mode
 out.mkdir(parents=True, exist_ok=True)
 shutil.copy2(base/'results/shared-outcome-updates.pdf', out/'shared-outcome-updates.pdf')
 text = s.replace('../results/shared-outcome-updates.pdf', 'shared-outcome-updates.pdf')
 if mode == 'tmlr':
  macros = text[text.index('\\newtheorem{theorem}'):text.index('\\title{')]
  body = text[text.index('\\begin{abstract}'):]
  body = body.replace('\\cite{', '\\citep{')
  body = body.replace('The public artifact, including source and numerical\nresults, is available at \\url{https://github.com/shi1720/tool-cache-coupling}.', 'The accompanying anonymized supplement contains the code, protocols, and numerical results.')
  body = body.replace('\\clearpage\n\\appendix', '\\appendix')
  statement = r'''\section*{AI use statement}
Generative AI tools assisted with research exploration, literature identification,
model and hypothesis development, mathematical derivation, proof drafting and
checking, experiment design, code implementation, result interpretation, figure
construction, manuscript drafting and editing, and internal critical review.
The reported numerical results were computed by the accompanying programs;
they are not language-model-generated measurements. The runtime fixtures are
scripted controls, not sampled language-model outputs. Automated checks and
internal AI-assisted reviews do not constitute external peer review or certify
novelty. The named human author remains responsible for the final content.

'''
  body = body.replace('\\begin{thebibliography}{9}', statement+'\\begin{thebibliography}{9}')
  bib = {'deepseekmath':'Shao et~al.(2024)', 'drgrpo':'Liu et~al.(2025)', 'che':'Che et~al.(2026)', 'noisecorrected':'El~Mansouri et~al.(2025)', 'xin':'Xin(2026)', 'tvcache':'Kumar et~al.(2026)', 'cacherl':'Islam et~al.(2026)', 'tvcachecode':'TVCache authors(2026)'}
  for key,label in bib.items():
   body=body.replace('\\bibitem{'+key+'}', '\\bibitem['+label+']{'+key+'}')
  refs = (ROOT/'submissions/references.bib').read_text()
  (out/'references.bib').write_text(refs)
  a=body.index('\\begin{thebibliography}')
  b=body.index('\\end{thebibliography}')+len('\\end{thebibliography}')
  body=body[:a]+'\\bibliographystyle{tmlr}\n\\bibliography{references}'+body[b:]
  preamble = r'''\documentclass[10pt]{article}
\usepackage{tmlr}
\usepackage{amsmath,amssymb,amsthm,booktabs,graphicx,array}
\usepackage{hyperref,url}
\hypersetup{hidelinks,pdftitle={Marginally Correct Tool Caches Can Reverse Group-Normalized Policy Updates},pdfauthor={}}
'''
  text = preamble+macros+r'''\title{Marginally Correct Tool Caches Can Reverse\\ Group-Normalized Policy Updates\thanks{Generative AI tools assisted the research and manuscript preparation. Details appear in the AI use statement.}}
\author{Anonymous authors}
\begin{document}
\maketitle
'''+body
  for name in ('tmlr.sty','tmlr.bst','fancyhdr.sty'):
   shutil.copy2(ROOT/'submissions/templates/tmlr-style-file-main'/name,out/name)
 (out/'manuscript.tex').write_text(text)
 if mode=='arxiv':
  with zipfile.ZipFile(ROOT/'submissions/arxiv-source.zip','w',zipfile.ZIP_DEFLATED) as z:
   for name in ('manuscript.tex','shared-outcome-updates.pdf'):
    z.write(out/name,name)
print('Prepared bylined arXiv source and anonymous TMLR source.')
