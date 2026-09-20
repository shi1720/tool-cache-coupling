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
