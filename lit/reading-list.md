# Reading List

Verification column per RESEARCH_PLAN.md instruction: every entry must be verified against the actual paper before its numbers are imported into the ledger. State as of 2026-11-07.

| # | Entry | Status in program | Verified against source | Ledger impact |
|---|---|---|---|---|
| 1 | Strassen, Gaussian elimination is not optimal, Numer. Math. 13 (1969) | core theory | pending (G-0003) | C-0001, C-0002, C-0004 provenance |
| 2 | Alder, Strassen, On the multiplicative complexity of algebras over finite fields (1981) | core theory | pending (G-0003) | C-0009 |
| 3 | Laderman, A noncommutative algorithm for multiplying 3x3 matrices using 23 multiplications (1976) | core theory | pending (G-0003) | C-0010 |
| 4 | Schoenhage, Partial and total matrix multiplication, SIAM J. Comput. 10 (1981) | core theory | pending (G-0003) | G-0002 chain |
| 5 | Strassen, Relative bilinear complexity and matrix multiplication (1987) | core theory (the spectrum) | pending (G-0003) | Spectrum.lean drafts |
| 6 | Christandl, Vrana, Zuiddam, Barriers for Fast Matrix Multiplication from Irreversibility (2021) | the barrier | pending (G-0003) | Irreversibility.lean draft |
| 7 | Christandl, Vrana, Zuiddam, Universal points in the asymptotic spectrum of tensors | core theory | pending | Spectrum.lean drafts |
| 8 | Landsberg, Geometry and Complexity Theory | flattenings, border rank | pending | flattening references |
| 9 | Blaeser, On the complexity of the multiplication of matrices of small formats | substitution method | pending | lower-bound work |
| 10 | Alman, Limits on the Universal Method for Matrix Multiplication (FOCS 2021) | exact constant and hypothesis | pending | WS1 loss-term list |
| 11 | Vassilevska Williams, Xu, Xu, Zhou, New Bounds for Matrix Multiplication: from Alpha to Omega, arXiv:2307.07970 (SODA 2024) | WS1 entry point | abstract verified 2026-11-07 (v2); PDF pending (G-0003) | C-0012, C-0013 |
| 12 | Duan, Wu, Zhou, Faster Matrix Multiplication via Asymmetric Hashing (FOCS 2023) | prior exponent step | not read; known through entry 11 | C-0013 |
| 13 | Alman, Vassilevska Williams, Xu, Xu, Zhou, More Asymmetry Yields Faster Matrix Multiplication, arXiv:2404.16349 (SODA 2025) | current record analysis | abstract verified 2026-11-07 (v3); PDF pending (G-0003) | C-0011 |
| 14 | Alman, Li, Asymptotic Rank Speedup Theorems, Revisited, arXiv:2605.21738 (CCC 2026) | modern statement of the asymptotic sum inequality | Theorem 1.1 verified 2026-11-07 (v2 HTML); PDF pending (G-0003) | G-0002, C-0007, C-0008 |
| 15 | Heule, Kauers, Seidl, Local search for fast matrix multiplication (SAT 2019) | search methods | pending | WS2 design |
| 16 | Heule, Kauers, Seidl, New ways to multiply 3x3 matrices (J. Symbolic Comput. 2021) | search methods | pending | WS2, C-0010 encoding |
| 17 | Kauers, Moosbauer, flip-graph papers | decomposition files | pending | WS3 |
| 18 | de Moura, Bjorner, Z3: An Efficient SMT Solver (2008) | tooling | tool in use, version pinned | TCB G-0005 |
| 19 | Lean 4 manual (lean-lang.org) | tooling | tool in use, version pinned | lean/ |
| 20 | Kovacs, Voronkov, First-Order Theorem Proving (2013) | ATP background | pending | tooling notes |
| 21 | Wetzler, Heule, Hunt, DRAT-trim (refutation-certificate checking) | planned G-0005 pipeline | pending | certs/unsat/ future format |

Notes discipline: a note per entry goes into `lit/notes/<key>.md` when first read, recording the pinned locator, the exact statement used, and the hypothesis discharge at the point of use (Law 9). The `ext:<key>` tokens in `dep/claims-ledger.yaml` resolve through `dep/references.yaml`.
