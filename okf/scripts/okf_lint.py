#!/usr/bin/env python3
"""OKF lint (READ-ONLY): health check for an OKF bundle. Fixes nothing.
Usage: okf_lint.py <folder> [--stale-days N]
Checks: non-conformant frontmatter, broken internal links (OKF treats these as
'not yet written', informational), orphan docs (not linked from any index.md),
and stale docs (timestamp older than N days, default 180).
"""
import sys, re, pathlib, datetime
import yaml
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from okf_paths import foreign_repo_roots, in_foreign_repo

argv = sys.argv[1:]
pos = [a for a in argv if not a.startswith("--")]
ROOT = pathlib.Path(pos[0] if pos else ".").resolve()
STALE_DAYS = 180
if "--stale-days" in argv:
    try: STALE_DAYS = int(argv[argv.index("--stale-days") + 1])
    except Exception: pass

EXCLUDE_DIRS = {".git",".claude","node_modules",".venv","venv","graphify-out","dist","build","__pycache__",".gstack"}
SCHEMA_NAMES = {"CLAUDE.md","AGENTS.md","GEMINI.md","CODEBUDDY.md","COPILOT.md"}
RESERVED = {"index.md","log.md"}
REQUIRED = ("type","title","description","timestamp")
LINK = re.compile(r'\]\(([^)]+)\)')
# Repos owned by someone else are not part of this bundle, see okf_paths.
FOREIGN_REPOS = foreign_repo_roots(ROOT, EXCLUDE_DIRS)

def all_md():
    for p in sorted(ROOT.rglob("*.md")):
        if any(x in EXCLUDE_DIRS for x in p.parts): continue
        if in_foreign_repo(p, FOREIGN_REPOS): continue
        yield p

def concept_docs():
    for p in all_md():
        if p.name not in SCHEMA_NAMES and p.name not in RESERVED:
            yield p

def split_fm(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---": return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            try:
                fm = yaml.safe_load("\n".join(lines[1:i])) or {}
            except yaml.YAMLError:
                return {"__bad__": True}
            return fm if isinstance(fm, dict) else {}
    return None

# 1. frontmatter conformance
missing = []
for p in concept_docs():
    fm = split_fm(p.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(fm, dict) or "__bad__" in fm or not all(fm.get(k) for k in REQUIRED):
        if isinstance(fm, dict) and "__bad__" in fm: why = "unparseable YAML frontmatter"
        elif not isinstance(fm, dict): why = "no frontmatter"
        else: why = "missing " + ",".join(k for k in REQUIRED if not fm.get(k))
        missing.append((p, why))

# 2. broken internal links
broken = []
for p in all_md():
    for m in LINK.finditer(p.read_text(encoding="utf-8", errors="replace")):
        u = m.group(1).strip()
        if u.startswith(("http://","https://","mailto:","#")): continue
        tgt = u.split("#")[0]
        if not tgt: continue
        if not (p.parent / tgt).exists():
            broken.append((p, u))

# 3. orphan concept docs (not linked from any index.md)
linked = set()
for p in all_md():
    if p.name != "index.md": continue
    for m in LINK.finditer(p.read_text(encoding="utf-8", errors="replace")):
        u = m.group(1).split("#")[0].strip()
        if not u or u.startswith(("http","mailto:")): continue
        try: linked.add((p.parent / u).resolve())
        except Exception: pass
orphans = [p for p in concept_docs() if p.name != "README.md" and p.resolve() not in linked]

# 4. stale docs
today = datetime.date.today()
stale = []
for p in concept_docs():
    fm = split_fm(p.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(fm, dict): continue
    ts = fm.get("timestamp")
    if not ts: continue
    try: d = datetime.date.fromisoformat(str(ts)[:10])
    except Exception: continue
    age = (today - d).days
    if age > STALE_DAYS: stale.append((p, age))

rel = lambda p: p.relative_to(ROOT)
print(f"OKF lint, {ROOT}  (stale threshold: {STALE_DAYS} days)\n")
print(f"[frontmatter] {len(missing)} concept doc(s) not conformant" + (", run enrich" if missing else "  ✓"))
for p, why in missing[:50]: print(f"   - {rel(p)}: {why}")
print(f"\n[links] {len(broken)} broken internal link(s)  (OKF: 'not yet written', informational)")
for p, u in broken[:50]: print(f"   - {rel(p)} -> {u}")
print(f"\n[orphans] {len(orphans)} concept doc(s) not linked from any index.md" + (", run indexes" if orphans else "  ✓"))
for p in orphans[:50]: print(f"   - {rel(p)}")
print(f"\n[stale] {len(stale)} doc(s) older than {STALE_DAYS} days")
for p, age in sorted(stale, key=lambda x: -x[1])[:50]: print(f"   - {rel(p)}  ({age}d)")
print(f"\nTOTAL findings: {len(missing)+len(broken)+len(orphans)+len(stale)}")
