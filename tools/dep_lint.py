"""Repository lint: DEP&CC 2.0 Chapter 33.2 rule subset declared in standards.md section 6.

Annotation:
  ID: tools.dep_lint
  CLASS: DEP-0
  WHAT: Enforces the closed status vocabulary, status contamination over the declared
        dependency graph, banned admitted tokens in Lean artifacts, the banned-phrase
        list over repository prose, gap expiry, certificate existence for verified
        statuses, and certificate-directory occupancy.
  WHY:  Mechanical enforcement substrate (DEP&CC 2.0 Chapter 33); Severity 0 findings
        fail CI.
  STATUS: verified-numeric (rule engine over declared finite inputs)
  COMPLETE: complete (for the declared rule subset; see standards.md section 2 F6)
  HYP: none
  DEPENDS: [dep/claims-ledger.yaml, dep/gaps.yaml, standards.md section 6]
  GAP: none
  OWNER: repo-maintainer
  EVIDENCE: python3 tools/dep_lint.py exits 0 on the seed commit

Scan exclusions (declared, not silent): standard.md and "doc standard.md" are
the canonical upstream normative sources that define the banned phrases and contain
them as data; RESEARCH_PLAN.md is the imported program document of the repository
owner and is scanned, with findings reported, but classified Severity 3 (warn and
educate) until its next revision, because its text predates the adoption of this
standard.
"""

import datetime
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLOSED_STATUSES = {"machine-checked", "proved", "proved-modulo", "conditional",
                   "verified-numeric", "empirical", "sketched", "conjectural",
                   "heuristic", "retracted"}
COMPLETENESS = {"complete", "partial", "sketch", "gap-declared", "placeholder", "retracted"}

BANNED_PHRASES = [
    "clearly", "obviously", "trivially", "evidently", "plainly",
    "it is easy to see", "one sees immediately", "a standard argument",
    "by standard techniques", "routine computation", "after some algebra",
    "it can be shown", "it is well known", "left to the reader",
    "exercise for the reader", "without difficulty", "in conclusion",
    "it is important to note", "as is well known", "of course",
    "seamless", "revolutionary", "ultimate", "best possible", "ruthless",
    "state-of-the-art", "powerful", "elegant", "beautiful", "mutatis mutandis",
    "the obvious map", "it goes without saying",
]

ADMITTED_TOKENS = [
    (re.compile(r"\bsorry\b"), "sorry"),
    (re.compile(r"\badmit\b"), "admit"),
    (re.compile(r"\bnative_decide\b"), "native_decide"),
    (re.compile(r"^\s*axiom\b", re.M), "axiom declaration"),
    (re.compile(r"^\s*postulate\b", re.M), "postulate declaration"),
    (re.compile(r"^\s*partial\s+\w", re.M), "partial declaration"),
    (re.compile(r"^\s*unsafe\s+\w", re.M), "unsafe declaration"),
]

FINDINGS = []


def finding(severity, rule, msg):
    FINDINGS.append((severity, rule, msg))
    print("  [S%d] %s: %s" % (severity, rule, msg))


def phrase_regex():
    parts = [re.escape(p) for p in BANNED_PHRASES]
    return re.compile(r"(?i)\b(" + "|".join(parts) + r")\b")


def scan_prose():
    rx = phrase_regex()
    exclude_dirs = {".git", "node_modules", ".lake"}
    excluded_files = {"standard.md", "doc standard.md"}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            if rel in excluded_files:
                continue
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for m in rx.finditer(text):
                sev = 3 if rel == "RESEARCH_PLAN.md" else 0
                finding(sev, "DEP-LINT-BANNED-PHRASE",
                        "%s: %r" % (rel, m.group(0)))


def scan_lean():
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "lean")):
        for fn in filenames:
            if not fn.endswith(".lean"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for rx, name in ADMITTED_TOKENS:
                for m in rx.finditer(text):
                    line = text[:m.start()].count("\n") + 1
                    finding(0, "DEP-LINT-ADMITTED",
                            "%s:%d: banned token %r" % (rel, line, name))


def main():
    with open(os.path.join(ROOT, "dep", "claims-ledger.yaml")) as fh:
        ledger = yaml.safe_load(fh)["claims"]
    with open(os.path.join(ROOT, "dep", "gaps.yaml")) as fh:
        gaps = yaml.safe_load(fh)["gaps"]

    print("dep_lint: closed status vocabulary (DEP-LINT-STATUS-VALUE)")
    ids = set()
    for row in ledger:
        ids.add(row["id"])
        if row["status"] not in CLOSED_STATUSES:
            finding(0, "DEP-LINT-STATUS-VALUE",
                    "%s: status %r not in the closed set" % (row["id"], row["status"]))
        comp = (row.get("annotation") or {}).get("COMPLETE", "complete")
        if comp not in COMPLETENESS:
            finding(0, "DEP-LINT-STATUS-VALUE",
                    "%s: completeness %r not in the closed set" % (row["id"], comp))

    print("dep_lint: status contamination over declared dependencies "
          "(DEP-LINT-STATUS-CONTAMINATION)")
    # transitive closure of DEPENDS
    def closure(cid, seen=None):
        seen = seen or set()
        row = next((r for r in ledger if r["id"] == cid), None)
        if row is None or cid in seen:
            return seen
        seen.add(cid)
        for d in ((row.get("annotation") or {}).get("DEPENDS") or []):
            if isinstance(d, str) and d.startswith("C-"):
                closure(d, seen)
        return seen

    for row in ledger:
        comp = (row.get("annotation") or {}).get("COMPLETE", "complete")
        if comp != "complete":
            continue
        for dep in closure(row["id"]):
            if dep == row["id"]:
                continue
            drow = next((r for r in ledger if r["id"] == dep), None)
            if drow is None:
                finding(0, "DEP-LINT-STATUS-CONTAMINATION",
                        "%s depends on unknown node %s" % (row["id"], dep))
                continue
            dcomp = (drow.get("annotation") or {}).get("COMPLETE", "complete")
            if dcomp != "complete":
                finding(0, "DEP-LINT-STATUS-CONTAMINATION",
                        "%s is complete but depends on %s with completeness %s"
                        % (row["id"], dep, dcomp))

    print("dep_lint: admitted tokens in Lean artifacts (DEP-LINT-ADMITTED)")
    scan_lean()

    print("dep_lint: banned phrases in repository prose (DEP-LINT-BANNED-PHRASE)")
    scan_prose()

    print("dep_lint: gap expiry (DEP-LINT-GAP-EXPIRY)")
    today = datetime.date.today()
    gap_ids = set()
    for g in gaps:
        gap_ids.add(g["id"])
        if g["status"] == "open":
            exp = datetime.date.fromisoformat(str(g["expires"]))
            if exp < today:
                finding(0, "DEP-LINT-GAP-EXPIRY",
                        "%s expired on %s and is still open" % (g["id"], exp))

    print("dep_lint: certificate existence for verified statuses "
          "(DEP-LINT-CLAIM-INFLATION)")
    for row in ledger:
        st = row["status"]
        if st in ("verified-numeric", "machine-checked"):
            cert = row.get("cert")
            checker = row.get("checker")
            if not cert or cert == "none" or not os.path.exists(os.path.join(ROOT, cert)):
                finding(0, "DEP-LINT-CLAIM-INFLATION",
                        "%s: status %s without an existing certificate" % (row["id"], st))
            if not checker or checker == "none":
                finding(0, "DEP-LINT-CLAIM-INFLATION",
                        "%s: status %s without a checker" % (row["id"], st))
        # gap references must resolve
        for gid in row.get("gaps") or []:
            if gid not in gap_ids:
                finding(0, "DEP-LINT-CLAIM-INFLATION",
                        "%s: references unknown gap %s" % (row["id"], gid))

    print("dep_lint: certificate directory occupancy (DEP-LINT-ORPHAN)")
    for d in ("decompositions", "border", "unsat", "analysis", "flattenings"):
        full = os.path.join(ROOT, "certs", d)
        if not os.path.isdir(full):
            continue
        entries = [f for f in os.listdir(full) if not f.startswith(".")]
        if not entries and not os.path.exists(os.path.join(full, "EMPTY.md")):
            finding(2, "DEP-LINT-ORPHAN",
                    "certs/%s is empty and carries no EMPTY.md declaration" % d)

    sev0 = [f for f in FINDINGS if f[0] == 0]
    print("\ndep_lint: %d findings (%d Severity 0)" % (len(FINDINGS), len(sev0)))
    if sev0:
        sys.exit(1)


if __name__ == "__main__":
    main()
