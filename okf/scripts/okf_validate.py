#!/usr/bin/env python3
"""Run Google's OKF reference validation (vendored document.py, unmodified) against a bundle.
Fully local: document.py imports only pyyaml. Supplementary reserved-file checks follow SPEC.md §6/§7.
"""
import sys, pathlib
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import document as D  # Google's actual reference code
from okf_paths import foreign_repo_roots, in_foreign_repo

ROOT = pathlib.Path(sys.argv[1]).resolve()
RESERVED = {"index.md", "log.md"}
concept_pass, concept_fail, reserved_notes = [], [], []

SCHEMA_NAMES = {"CLAUDE.md", "AGENTS.md", "GEMINI.md", "CODEBUDDY.md", "COPILOT.md"}
EXCL = {".git", ".claude", "node_modules", ".venv", "venv", "graphify-out", "dist", "build", "__pycache__", ".gstack"}
# Repos owned by someone else are not part of this bundle — see okf_paths.
FOREIGN_REPOS = foreign_repo_roots(ROOT, EXCL)
for p in sorted(ROOT.rglob("*.md")):
    if any(part in EXCL for part in p.parts):
        continue
    if in_foreign_repo(p, FOREIGN_REPOS):
        continue
    if p.name in SCHEMA_NAMES:      # OKF 'schema' layer, not concept docs — out of scope
        continue
    rel = p.relative_to(ROOT)
    text = p.read_text(encoding="utf-8")
    if p.name in RESERVED:
        has_fm = text.startswith("---\n")
        if p.name == "index.md":
            if not has_fm:
                reserved_notes.append(f"OK   {rel}: no frontmatter (correct)")
            else:
                import yaml as _y
                block, lines = None, text.splitlines()
                for i in range(1, len(lines)):
                    if lines[i].strip() == "---":
                        block = "\n".join(lines[1:i]); break
                try:
                    keys = set((_y.safe_load(block) or {}).keys()) if block is not None else {"__bad__"}
                except Exception:
                    keys = {"__bad__"}
                if keys and keys <= {"okf_version"}:
                    reserved_notes.append(f"OK   {rel}: okf_version-only frontmatter (allowed for bundle root)")
                else:
                    reserved_notes.append(f"FAIL {rel}: index.md frontmatter must be okf_version-only (got {sorted(keys)})")
        else:  # log.md
            import re
            heads = re.findall(r'^## (.+)$', text, re.M)
            bad = [h for h in heads if not re.match(r'^\d{4}-\d{2}-\d{2}$', h.strip())]
            reserved_notes.append(f"{'FAIL' if bad else 'OK  '} {rel}: {len(heads)} date heading(s)"
                                  + (f"; non-ISO: {bad}" if bad else ""))
        continue
    # non-reserved concept doc -> Google's validate()
    try:
        doc = D.OKFDocument.parse(text)
        doc.validate()
        concept_pass.append(str(rel))
    except D.OKFDocumentError as e:
        concept_fail.append(f"{rel}: {e}")

print(f"Google OKF reference validator — required keys: {D.REQUIRED_FRONTMATTER_KEYS}")
print(f"Bundle: {ROOT}\n")
print(f"CONCEPT DOCS: {len(concept_pass)} passed, {len(concept_fail)} failed")
for f in concept_fail: print("  FAIL", f)
print("\nRESERVED FILES (spec §6/§7 supplementary):")
for n in reserved_notes: print("  ", n)
overall = "PASS ✅" if not concept_fail and not any(n.startswith('  FAIL') or 'FAIL' in n for n in reserved_notes) else "FAIL ❌"
print(f"\nRESULT: {overall}")
