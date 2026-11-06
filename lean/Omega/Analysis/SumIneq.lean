/-!
# Omega.Analysis.SumIneq

STATUS: placeholder. Owner: repo-maintainer. Ticket: OMEGA-2 / gap G-0002.

Statement draft (transcribed from ext:alman2026speedup, Theorem 1.1, asymptotic sum
inequality, attributing ext:schonhage1981):

  theorem asymptotic_sum_inequality
      (shapes : Fin l -> Nat x Nat x Nat)
      (r : Nat)
      (h : BorderRank (directSum shapes) r)
      (nontrivial : exists i, prod shapes i > 1) :
      exists tau, (sum_i (prod shapes i)^tau = r) /\ omega <= 3 * tau

Uniqueness of tau follows from monotonicity of t -> sum_i prod_i^t on the nonnegative
reals when every prod_i > 1; the certified numeric instances live in
certs/analysis/sumineq_*.json with enclosures verified by tools/check_certs.py.

The laser-method constraint system of workstream WS1 builds on this file.
