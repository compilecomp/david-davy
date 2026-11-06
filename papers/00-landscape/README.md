# Papers/00: Landscape and Barriers

STATUS: DEP-1 document at seed stage. Owner: repo-maintainer. Every number below resolves to a ledger row in `CLAIMS.md` or is explicitly marked as pending audit (gap G-0003).

## Scope

This note records the state of the matrix multiplication exponent problem as adopted by this repository: the three target formulations, the certified record, the known barrier, and the workstreams. It is the entry point for a new collaborator and the audit trail for the numbers quoted in the repository README.

## Problem

The exponent ω is defined by ω = log_2 RA(⟨2,2,2⟩), with RA the asymptotic rank (convention `dep/conventions.yaml`, `conv.omega` and `conv.asymrank`). Equivalently, ω is the infimum over h such that R(⟨n,n,n⟩) = O(n^h). Three equivalent formulations of ω = 2 are the targets of the program (RESEARCH_PLAN.md):

1. T1 (constructive): a family of decompositions with R(⟨n,n,n⟩) = n^(2+o(1)).
2. T2 (asymptotic subrank): Q(⟨2,2,2⟩) = 4 (ledger row C-0017, status `conjectural`).
3. T3 (spectral): min over the asymptotic spectrum Δ of F(⟨2,2,2⟩) equals 4.

## Certified state of the record

| Bound | Ledger row | Status | Source |
|---|---|---|---|
| R_Q(⟨2,2,2⟩) ≤ 7 and R_F2(⟨2,2,2⟩) ≤ 7 | C-0001, C-0002 | `verified-numeric` | scheme of ext:strassen1969; certificates re-check in CI |
| R_F(⟨2,2,2⟩) ≥ 7 for every field F | C-0009 | `proved-modulo` | ext:alderstrassen1981; audit pending G-0003 |
| R_F(⟨3,3,3⟩) ≤ 23 | C-0010 | `proved-modulo` | ext:laderman1976; audit pending G-0003 |
| ω ≤ log_2(7) ≈ 2.8073549221 | C-0004 | `proved-modulo` | tensor-power chain over C-0001; gap G-0001 |
| ω ≤ 2.371866 | C-0013 | `proved-modulo` | ext:dwz2023 (FOCS 2023), read through ext:wxxz2023alpha |
| ω ≤ 2.371552 | C-0012 | `proved-modulo` | ext:wxxz2023alpha (SODA 2024) |
| ω < 2.371177 | C-0011 | `proved-modulo` | ext:alman2025asymmetry (SODA 2025) with ext:dupont2026 |

Bounds of historical interest whose numbers are not yet imported (Bini-Capovani-Lotti-Romani 1980, Schoenhage 1981, Strassen 1986, Coppersmith-Winograd 1990, Stothers 2010, Vassilevska Williams 2012, Le Gall 2014, Alman-Vassilevska Williams 2021) are listed in `lit/reading-list.md` with verification state "pending"; they will be added to the ledger only with pinpoints, per Law 9.

## The constraint that shapes the program

The irreversibility barrier of Christandl, Vrana, and Zuiddam (ext:cvz2021barriers; definition audit pending G-0003) states, in the wording adopted by RESEARCH_PLAN.md: any method that routes through a fixed intermediate tensor T with irreversibility iota(T) > 1 inherits ω > 2. Consequently ω = 2 requires either a family {T_k} with iota(T_k) going to 1, or a method outside the restriction and degeneration framework. This repository treats the barrier as a theorem to be formalized (`lean/Omega/Barriers/Irreversibility.lean`, placeholder) and not as an opinion; its statement is DEP-2 until the audit gap G-0003 closes.

## Workstreams and what is open

Workstreams WS1 through WS5 and their phasing are fixed in RESEARCH_PLAN.md. At seed stage:

1. WS1 (laser-method optimization): the constraint-system machinery exists in `analysis/` and is certified for small instances (C-0004 through C-0008). Reproducing a published exponent to 4 decimals is the entry ticket and is open.
2. WS2 (border rank over F_2[eps]): the loop search, model, exact re-verification, certificate runs end to end (C-0018); the rank-5 refutation is solver-trusted only (C-0015, G-0005).
3. WS3 (symmetry-adapted search): not started.
4. WS4 (automated flattenings): the flattening and p=1 Koszul pipeline is mechanized at 2x2x2 (C-0003); the Macaulay2 path is local-only (`cas/`).
5. WS5 (spectrum and irreversibility): module drafts under `lean/Omega/Spectrum/` and `lean/Omega/Barriers/`, all placeholders (G-0006, G-0003).

## Limitations

This note states no new theorems. Its numerical claims resolve to ledger rows; its historical claims carry explicit audit gaps. The exponent record is a moving target and is dated 2026-11-07 throughout.
