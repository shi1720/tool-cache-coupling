# Submission preparation

These are preparation tools, not submission receipts. A generated venue header does not mean that the paper has been submitted or accepted. Do not post the anonymous review PDF as the public preprint.

## Build

The reviewed source is `research/cache-coupling/paper/manuscript.tex`.
Download the official TMLR template archive from its author guide into `submissions/templates/tmlr-style.zip` and extract it there. The template used on 20 September 2026 was the official `JmlrOrg/tmlr-style-file` revision `7bf90efe3a0debbba703c05c43f3ff7e4d4a2992`.

```sh
mkdir -p submissions/templates tmp/pdfs/arxiv tmp/pdfs/tmlr
curl -fL https://github.com/JmlrOrg/tmlr-style-file/archive/7bf90efe3a0debbba703c05c43f3ff7e4d4a2992.zip -o submissions/templates/tmlr-style.zip
unzip -q submissions/templates/tmlr-style.zip -d submissions/templates
mv submissions/templates/tmlr-style-file-7bf90efe3a0debbba703c05c43f3ff7e4d4a2992 submissions/templates/tmlr-style-file-main
python3 submissions/prepare_manuscripts.py
tectonic submissions/arxiv/manuscript.tex --outdir tmp/pdfs/arxiv
tectonic submissions/tmlr/manuscript.tex --outdir tmp/pdfs/tmlr
python3 submissions/package_supplement.py
```

The TMLR output uses the official unmodified style and bibliography style, with anonymous metadata and a substantive AI use statement. The arXiv source archive has a bylined manuscript and its figure. arXiv must compile and display its own preview during submission; a successful local build does not replace that check.

The anonymous code package removes an author-specific default local path and updates only that file's matching source hash in the packaged runtime manifest. It does not change result bytes or numerical/runtime experiment logic. Its README records this transformation.

Author-side declarations, account verification, affiliation/conflicts, licensing, venue exclusivity, and any endorsement requirements must be completed accurately through the relevant portal. Generating the package is not equivalent to satisfying those requirements.

## AISTATS 2027 candidate

After the preceding preparation commands, run:

```sh
curl -fL https://aistats.org/aistats2027/AISTATS2027PaperPack.zip -o submissions/templates/AISTATS2027PaperPack.zip
unzip -q submissions/templates/AISTATS2027PaperPack.zip -d submissions/templates
mkdir -p tmp/pdfs/aistats
python3 submissions/prepare_aistats.py
tectonic submissions/aistats/manuscript.tex --outdir tmp/pdfs/aistats
cp submissions/tmlr-code.zip submissions/aistats-code.zip
```

The official archive retrieved on 20 September 2026 has SHA-256 `aac31ecf2e41f5a2b7f21d00094bfc2fc1207c34d9f955e991b66f3dc98fdb9b`. The style files are unmodified. The candidate PDF has six pages containing main text, one references page, one checklist page, and two single-column appendix pages. It includes the mandatory substantive AI Use Statement and all 18 official checklist questions without rewriting them. Numerical citations are permitted for initial submissions; an accepted version must use author-year citations.

This is a backup candidate package, not a concurrent submission. The template prints an automatic review header even before upload. Neither that header nor generation of these files establishes submission or acceptance. Account activation, the author's declarations and review, venue selection, and a justified reciprocal-reviewer exemption if applicable remain pending. The author should confirm the conference's in-person presentation commitment before submission.
