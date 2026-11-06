"""Ledger lint and generated-artifact emission.

Annotation:
  ID: tools.ledger_lint
  CLASS: DEP-0
  WHAT: Cross-references the claims ledger against the gap register and the
        reference registry, regenerates CLAIMS.md, fails on drift between the
        generated view and the committed file, and emits dep/out/*.json.
  WHY:  CLAIMS.md is a generated view (standards.md section 3.1); Law 10 bans stale
        generated artifacts; DEP&CC 2.0 Chapter 6.6 requires emitted artifacts.
  STATUS: verified-numeric
  COMPLETE: complete
  HYP: none
  DEPENDS: [dep/claims-ledger.yaml, dep/gaps.yaml, dep/references.yaml]
  GAP: none
  OWNER: repo-maintainer
  EVIDENCE: python3 tools/ledger_lint.py exits 0; dep/out/ refreshed per run
"""

import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dep", "out")

FAILURES = []


def fail(msg):
    FAILURES.append(msg)
    print("  FAIL: %s" % msg)


def load(name):
    with open(os.path.join(ROOT, "dep", name)) as fh:
        return yaml.safe_load(fh)


def render_claims_md(claims, gaps, refs):
    lines = []
    lines.append("# Claims Ledger")
    lines.append("")
    lines.append("GENERATED FILE. Source of truth: `dep/claims-ledger.yaml`.")
    lines.append("Regenerate with `python3 tools/ledger_lint.py`; manual edits are")
    lines.append("reverted (standards.md section 3.1, DEP&CC 2.0 Chapter 6.4).")
    lines.append("")
    lines.append("Statuses are the closed set of DEP&CC 2.0 Chapter 5.4. The mapping")
    lines.append("from the RESEARCH_PLAN.md draft vocabulary is fixed in standards.md")
    lines.append("section 3.2. Justification tokens are from DEP&CC 2.0 Appendix F.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| ID | Status | Field | Certificate | Statement |")
    lines.append("|---|---|---|---|---|")
    for c in claims:
        cert = c.get("cert") or "none"
        stmt = c["statement"]
        if len(stmt) > 140:
            stmt = stmt[:137] + "..."
        lines.append("| %s | %s | %s | `%s` | %s |" % (c["id"], c["status"], c.get("field", ""), cert, stmt))
    lines.append("")
    lines.append("## Rows")
    lines.append("")
    for c in claims:
        a = c.get("annotation") or {}
        lines.append("### %s" % c["id"])
        lines.append("")
        lines.append("- **Statement.** %s" % c["statement"])
        lines.append("- **Field.** %s" % c.get("field", "any"))
        lines.append("- **Claim status.** %s" % c["status"])
        lines.append("- **Completeness.** %s" % a.get("COMPLETE", "complete"))
        lines.append("- **Certificate.** %s" % (c.get("cert") or "none"))
        lines.append("- **Checker.** %s" % (c.get("checker") or "none"))
        lines.append("- **Provenance.** %s" % c.get("provenance", "none"))
        lines.append("- **Hypotheses.** %s" % a.get("HYP", "none"))
        lines.append("- **Depends on.** %s" % (", ".join(a.get("DEPENDS") or []) or "nothing"))
        lines.append("- **Gaps.** %s" % (", ".join(c.get("gaps") or []) or "none"))
        lines.append("- **Evidence.** %s" % a.get("EVIDENCE", "none"))
        lines.append("- **Owner.** %s" % a.get("OWNER", "repo-maintainer"))
        lines.append("")
    lines.append("## Gap register (view)")
    lines.append("")
    lines.append("| Gap | Open | Expires | Downgrades | Target |")
    lines.append("|---|---|---|---|---|")
    for g in gaps:
        lines.append("| %s | %s | %s | %s | %s |" % (
            g["id"], g["opened"], g["expires"],
            ", ".join("%s->%s" % (k, v) for k, v in (g.get("downgrades") or {}).items()) or "none",
            g.get("target", "")))
    lines.append("")
    return "\n".join(lines)


def main():
    ledger = load("claims-ledger.yaml")
    claims = ledger["claims"]
    gaps = load("gaps.yaml")["gaps"]
    refs = load("references.yaml")["references"]
    ref_keys = {r["key"] for r in refs}
    gap_ids = {g["id"] for g in gaps}
    claim_ids = [c["id"] for c in claims]

    print("ledger_lint: identifier uniqueness")
    if len(claim_ids) != len(set(claim_ids)):
        fail("duplicate claim ids")

    print("ledger_lint: gap, dependency, and citation resolution")
    ext_rx = re.compile(r"ext:([A-Za-z0-9_]+)")
    for c in claims:
        for gid in c.get("gaps") or []:
            if gid not in gap_ids:
                fail("%s: unknown gap %s" % (c["id"], gid))
        a = c.get("annotation") or {}
        for d in a.get("DEPENDS") or []:
            if isinstance(d, str) and d.startswith("C-") and d not in claim_ids:
                fail("%s: unknown dependency %s" % (c["id"], d))
        for m in ext_rx.finditer(str(c.get("provenance", "")) + " " + str(a.get("EVIDENCE", ""))):
            if m.group(1) not in ref_keys:
                fail("%s: unknown reference key ext:%s" % (c["id"], m.group(1)))

    print("ledger_lint: certificate and checker paths")
    for c in claims:
        cert = c.get("cert")
        if cert and cert != "none" and not os.path.exists(os.path.join(ROOT, cert)):
            fail("%s: cert path does not exist: %s" % (c["id"], cert))
        checker = c.get("checker")
        if checker and checker not in ("none",) and checker.startswith(("tools/", "analysis/", "search/", "lean/")) \
                and not os.path.exists(os.path.join(ROOT, checker)):
            fail("%s: checker path does not exist: %s" % (c["id"], checker))

    print("ledger_lint: regenerating CLAIMS.md and checking drift")
    content = render_claims_md(claims, gaps, refs)
    claims_md = os.path.join(ROOT, "CLAIMS.md")
    if os.path.exists(claims_md):
        with open(claims_md, encoding="utf-8") as fh:
            current = fh.read()
        if current != content:
            fail("CLAIMS.md is stale; run python3 tools/ledger_lint.py and commit")
    with open(claims_md, "w", encoding="utf-8") as fh:
        fh.write(content)

    print("ledger_lint: emitting dep/out artifacts")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "claims.json"), "w") as fh:
        json.dump(claims, fh, indent=2, sort_keys=True, default=str)
    with open(os.path.join(OUT, "gaps.json"), "w") as fh:
        json.dump(gaps, fh, indent=2, sort_keys=True, default=str)
    cert_manifest = []
    for dirpath, _, filenames in os.walk(os.path.join(ROOT, "certs")):
        for fn in sorted(filenames):
            if fn.endswith(".json"):
                rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
                cert_manifest.append(rel)
    with open(os.path.join(OUT, "certificates.json"), "w") as fh:
        json.dump({"generated": "by tools/ledger_lint.py",
                   "certificates": sorted(cert_manifest)}, fh, indent=2, sort_keys=True)

    if FAILURES:
        print("\nledger_lint: %d failures" % len(FAILURES))
        sys.exit(1)
    print("\nledger_lint: clean; %d rows, %d gaps, %d certificates"
          % (len(claims), len(gaps), len(cert_manifest)))


if __name__ == "__main__":
    main()
