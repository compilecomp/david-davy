-- Flattening rank of <2,2,2> over QQ, mirroring analysis/flattenings.py (derivation D1).
-- Run locally: M2 is not in CI (dep/toolchain.lock). Record the output next to this file
-- as a run record; certificates are produced only by the Python pipeline.

A = 4; B = 4; C = 4
-- index conventions (dep/conventions.yaml conv.mm_entry):
--   A-index (i,j) -> i*2+j, B-index (j,k) -> j*2+k, C-index (i,k) -> i*2+k
-- entry T[a, b, c] = 1 iff a == i*2+j, b == j*2+k, c == i*2+k for some (i,j,k) in [2]^3.

consistent = (a, b, c) -> (
    i := a % 2; ja := a // 2;   -- a = i*2 + j  (i = a % 2, j = a // 2)
    jb := b % 2; k := b // 2;   -- b = j*2 + k
    ic := c % 2; kc := c // 2;  -- c = i*2 + k
    ja == jb and i == ic and k == kc
)

T = matrix table(A*B, B*C, (a, bc) -> (
    b := bc // C; c := bc % C;
    if consistent(a, b, c) then 1 else 0
))

rk = rank T
<< "flattening rank of <2,2,2> over QQ: " << rk << endl
-- expected: 4 (matches certs/flattenings/222_Q_rank4.json and C-0003)
-- consequence D1: R_Q(<2,2,2>) >= 4
