# analysis/

Producer code for certificates. Modules:

1. `bilin.py` — exact tensor arithmetic over Q and F_p; the Strassen scheme; direct sums. Self-tests in `__main__`.
2. `make_decomposition_certs.py` — writes `certs/decompositions/*.json` behind a producer gate.
3. `flattenings.py` — ordinary and p=1 Koszul flattening, exact ranks, in-module derivations D1 and D2; writes `certs/flattenings/222_Q_rank4.json`.
4. `sumineq.py` — certified tau enclosures and the log_2(7) enclosure; writes `certs/analysis/*.json`.
5. `search_unsat.py` — exhaustive enumeration refutation; writes `certs/unsat/222_F2_rank_ge3.json`.

Independence contract (standards.md section 5.3): `tools/check_certs.py` re-verifies everything with its own arithmetic and imports nothing from this directory.
