# Proof of Hardin's width-six three-colour one-defect recurrence

Creators, in order: Haobo Ma (ChronoAI Pte Ltd, Singapore); Wenlin Zhang
(National University of Singapore; ChronoAI Pte Ltd, Singapore).

License: Creative Commons Attribution 4.0 International (CC BY 4.0).

## Mathematical coverage

The main theorem proves the empirical recurrence in OEIS A229532, revision 8,
Formula field, for every height n >= 20. Its reduced generating function has
denominator Q(z)^2 of degree eighteen; a polynomial gcd modulo 101 proves that
the eventual recurrence order is minimal. The height-nineteen discrepancy is 864.

The graph has horizontal and both diagonal bonds, without vertical bonds.
Colour names are introduced in row-major first-appearance order.

The note also proves seven smaller-strip recurrences in A229534: fixed widths
two, three, four and five, and fixed heights two, three and four. It supplies
the corresponding empirical generating functions attributed to Colin Barker
(2018) and R. J. Mathar (2026), and identifies the exceptional all-one-colour
two-cell row. The single-row count agrees with Bernhard Wolf's A057711; the width-two count
agrees with the formula credited to Barker in A167682.

Alternate-column colour complementation identifies A269033 with six times
A229532. Adding the zero-defect sector gives A269050. Both sum-two sequences
have minimal eventual order eighteen, the same recurrence for n >= 20, and
discrepancy 5184 at n = 19. The seven smaller-strip recurrences also apply to
their exactly-one and at-most-one sum-two tables A269035 and A269052.

A general formal-power-series identity gives squared-determinant denominator
bounds for every fixed width or height. It does not determine the particular
reduced denominators conjectured for column seven or rows five through seven.
Those specific orders and thresholds are outside this note's coverage.

## Rebuild

Use Tectonic 0.17.0:

```sh
tectonic --untrusted note.tex
```

Or compile twice with a standard LaTeX distribution:

```sh
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error note.tex
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is included in `note.tex`; no separate figures or bibliography
files are needed. The paper uses A4 article typography and Latin Modern fonts.

## Exact finite certificates

Python 3.8 or later is sufficient; no third-party packages are required.

```sh
python3 verify.py --table b229532.txt --output certificate-recomputed.json
cmp certificate.json certificate-recomputed.json
python3 verify_siblings.py --output sibling-certificate-recomputed.json
cmp sibling-certificate.json sibling-certificate-recomputed.json
python3 verify_variants.py --output variant-certificate-recomputed.json
cmp variant-certificate.json variant-certificate-recomputed.json
```

The certificates contain explicit integer matrices, boundary vectors and zero
polynomial residuals. Right multiplication propagates these finite identities
to all heights or widths in the stated ranges. The tabulated comparisons and
direct canonical enumerations are additional finite checks, not extrapolation.

## Mathematical sources and formal scope

- R. H. Hardin, A229532, submitted 25 September 2013, Formula field, revision 8
  (27 April 2021): https://oeis.org/A229532
- R. H. Hardin, A229534, Formula field, revision 11 (13 November 2026), and its
  linked entries A229529–A229531 and A229535–A229537: https://oeis.org/A229534
- R. H. Hardin, A269033, A269035, A269050 and A269052, submitted 18 February
  2016, Name and Formula fields: https://oeis.org/A269033
- Bernhard Wolf, A057711, submitted 24 October 2000, Name, Formula and Author
  fields, revision 163 (5 July 2026): https://oeis.org/A057711
- J. Salas and A. D. Sokal, *Transfer Matrices and Partition-Function Zeros
  for Antiferromagnetic Potts Models I. General Theory and Square-Lattice
  Chromatic Polynomial*, Journal of Statistical Physics 104 (2001), 609–699,
  Section 3.1, equations (3.1)–(3.11): https://arxiv.org/abs/cond-mat/0004330v2

The main pinned Lean declaration states precisely the literal canonical
width-six recurrence for every n >= 20:

https://github.com/the-omega-institute/trureturing/blob/9849c0d81bfe0a953a10ad37400f5b1b61f028b5/D5/S3/StatisticalMechanics/Potts/CrossedStripDefectsWide/HardinA229532Strip.lean

The note links six additional pinned declarations for the smaller-strip
recurrences and states each exact range. These declarations concern the
recurrences. The generating functions, minimality, closed boundary counts,
sum-two equivalence and general resolvent identities have the written proofs
and integer certificates in the note and accompanying files.
