# Manuscript

Author: Shivam Gupta. This is a bylined technical note, not a venue-specific anonymous submission or an externally peer-reviewed paper.

## Build the PDF

From the repository root, with Tectonic installed:

```sh
mkdir -p output/pdf
tectonic research/cache-coupling/paper/manuscript.tex --outdir output/pdf
```

The source includes the committed vector figure at `../results/shared-outcome-updates.pdf`. Fonts are embedded. Tectonic may download its TeX support files on its first run. It produces `output/pdf/manuscript.pdf`.

The distributed PDF was visually inspected on all nine pages, checked for out-of-page text and unresolved references, and verified to contain embedded fonts and correct author metadata. The numerical and variance checks pass. These checks do not establish novelty, external peer review, or acceptance at a particular venue.
