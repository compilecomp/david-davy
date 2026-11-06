# Repository gates. Order matters: producers, checker, ledger, lint, lean.
PY ?= python3

.PHONY: all check certs lint ledger lean search selftest

all: certs check ledger lint lean

selftest:
        $(PY) analysis/bilin.py

certs: selftest
        $(PY) analysis/make_decomposition_certs.py
        $(PY) analysis/flattenings.py
        $(PY) analysis/sumineq.py
        $(PY) analysis/search_unsat.py

check:
        $(PY) tools/check_certs.py

ledger:
        $(PY) tools/ledger_lint.py
        $(PY) tools/ledger_lint.py

lint:
        $(PY) tools/dep_lint.py

search:
        $(PY) search/enc.py --selftest

lean:
        cd lean && lake build
        mkdir -p dep/out
        cd lean && lake build 2>&1 | grep -oE "'[A-Za-z0-9_.]+' does not depend on any axioms|depends on axioms:.*" > ../dep/out/axioms_checkstrassen.txt || true
