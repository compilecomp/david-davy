# cas/

Computer algebra scripts (Macaulay2) for the flattening pipeline of workstream WS4. Macaulay2 is not part of CI (dep/toolchain.lock); outputs of local runs are committed next to the scripts as run records, not as certificates.

`flattenings.m2` constructs the flattening matrix of a matrix multiplication tensor over QQ and computes its rank; it mirrors `analysis/flattenings.py` at seed stage and is intended to grow the Koszul/Young flattening search that the Python pipeline cannot express.
