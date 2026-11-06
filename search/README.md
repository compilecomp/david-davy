# search/

SMT and SAT encodings for rank and border-rank search (workstream WS2, Tier B of RESEARCH_PLAN.md).

1. `enc.py` — the constraint system sum_r u_r (x) v_r (x) w_r = eps^h T + O(eps^(h+1)) over F_2[eps]/(eps^2) and the exact-rank system over F_2, solved by z3 under declared timeouts. Satisfying models are re-verified by exact independent arithmetic before any use; a re-verified border model becomes `certs/border/222_F2_border7_d2h1.json` (ledger row C-0018). UNSAT answers are solver-trusted only (TCB entry, gap G-0005) and stay at status `empirical`.

2. `results/` — run records with solver version, declared timeout, wall time, status, and models. These are evidence trails, not certificates.

Known limitations: no symmetry breaking, no XOR-CNF export, no DRAT pipeline yet; sizes are laptop-scale by design.
