#!/usr/bin/env python3
"""Deploy OKF v0.1 to a target folder.  Usage: okf_deploy.py <mode> <folder>
Modes:  inventory | frontmatter | indexes
- Adds type/title/description/timestamp frontmatter to concept docs (idempotent:
  skips docs that already have all four non-empty). description via local LM Studio.
- Skips CLAUDE.md/AGENTS.md/GEMINI.md/CODEBUDDY.md (OKF 'schema' layer), reserved
  index.md/log.md, and generated/vendor dirs. Never touches non-.md files.
- Quotes title/description as YAML double-quoted scalars (avoids the colon bug).
Leaves everything uncommitted.
"""
import sys, os, re, json, urllib.request, pathlib, subprocess
import yaml
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from okf_paths import foreign_repo_roots, in_foreign_repo

MODE = sys.argv[1] if len(sys.argv) > 1 else "inventory"
ROOT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(os.environ.get("OKF_ROOT", "."))
ROOT = ROOT.resolve()
REQUIRED = ("type", "title", "description", "timestamp")
EXCLUDE_DIRS = {".git", ".claude", "node_modules", ".venv", "venv", "graphify-out", "dist",
                "build", "__pycache__", ".gstack"}
SKIP_NAMES = {"CLAUDE.md", "AGENTS.md", "GEMINI.md", "CODEBUDDY.md", "COPILOT.md"}
RESERVED = {"index.md", "log.md"}
# Repos owned by someone else are not part of this bundle, see okf_paths. Your
# own projects are almost all git repos and must still be processed, so the test
# is the origin remote's owner, not merely "is a nested repo".
FOREIGN_REPOS = foreign_repo_roots(ROOT, EXCLUDE_DIRS)
LM_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:1234/v1").rstrip("/") + "/chat/completions"
LM_MODEL = os.environ.get("OPENAI_MODEL", "qwen3-coder-next")

def candidates():
    for p in sorted(ROOT.rglob("*.md")):
        if any(part in EXCLUDE_DIRS for part in p.parts): continue
        if p.name in SKIP_NAMES or p.name in RESERVED: continue
        if in_foreign_repo(p, FOREIGN_REPOS): continue
        yield p

def split_fm(text):
    """Return (fm_dict, raw_fm_lines, body, had_fm). Mirrors Google's parser leniency.
    raw_fm_lines = the exact lines between the --- delimiters (for lossless insertion)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, [], text, False
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i; break
    if end is None:
        return None, [], text, False
    raw = lines[1:end]
    try:
        fm = yaml.safe_load("\n".join(raw)) or {}
        if not isinstance(fm, dict): fm = {"__unparseable__": True}
    except yaml.YAMLError:
        fm = {"__unparseable__": True}
    body = "\n".join(lines[end+1:]).lstrip("\n")
    return fm, raw, body, True

def is_conformant(fm):
    return isinstance(fm, dict) and all(fm.get(k) for k in REQUIRED) and "__unparseable__" not in fm

def h1_title(body, path):
    for ln in body.splitlines():
        m = re.match(r'^#\s+(.*\S)', ln)
        if m: return re.sub(r'\s+', ' ', m.group(1)).strip()
    return path.stem.replace('-', ' ').replace('_', ' ').strip().title()

def infer_type(path, title):
    n = (path.stem + " " + title).lower()
    table = [("readme","overview"),("pickup","pickup"),("roadmap","roadmap"),
             ("principle","principles"),("architecture","architecture"),("risk","risks"),
             ("thesis","thesis"),("methodology","methodology"),("guide","guide"),
             ("spec","spec"),("plan","plan"),("brief","brief"),("transcript","transcript"),
             ("source","reference"),("content","content-plan"),("funnel","funnel")]
    for kw,t in table:
        if kw in n: return t
    return "note"

def timestamp(path):
    try:
        r = subprocess.run(["git","-C",str(path.parent),"log","-1","--format=%cs","--",path.name],
                           capture_output=True, text=True, timeout=10)
        d = r.stdout.strip()
        if re.match(r'^\d{4}-\d{2}-\d{2}$', d): return d
    except Exception: pass
    import datetime
    return datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()

def first_sentence(body):
    txt = re.sub(r'^#.*$', '', body, flags=re.M)          # drop headings
    txt = re.sub(r'`[^`]*`', '', txt)                       # drop code spans
    txt = re.sub(r'\s+', ' ', txt).strip()
    m = re.match(r'(.{15,200}?[.!?])(\s|$)', txt)
    s = (m.group(1) if m else txt[:160]).strip()
    return s or "Document."

def sanitize_desc(s):
    s = re.sub(r'<think>.*?</think>', '', s, flags=re.S|re.I)
    s = re.sub(r'^\s*(here.?s|summary|description)\s*:?\s*', '', s.strip(), flags=re.I)
    s = re.sub(r'\s+', ' ', s).strip().strip('"').strip()
    s = s.split('\n')[0].strip()
    words = s.split()
    if len(words) > 28: s = ' '.join(words[:28]).rstrip('.,;:') + '.'
    return s

def llm_description(title, body):
    prompt = (f"Write ONE plain sentence (max 22 words) describing this document for a "
              f"docs index. No preamble, no quotes.\n\nTitle: {title}\n\n{body[:1800]}")
    payload = json.dumps({"model": LM_MODEL, "temperature": 0.2, "max_tokens": 80,
        "messages":[{"role":"system","content":"You write terse one-sentence documentation summaries."},
                    {"role":"user","content":prompt}]}).encode()
    try:
        req = urllib.request.Request(LM_URL, data=payload, headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            out = json.load(r)["choices"][0]["message"]["content"]
        d = sanitize_desc(out)
        return d if len(d) >= 12 else None
    except Exception as e:
        return None

def yq(s):  # YAML double-quoted scalar
    return '"' + s.replace('\\','\\\\').replace('"','\\"') + '"'

# ---------------- modes ----------------
def run_inventory():
    total=need=already=skip_partial=0; dirs=set(); by_top={}
    for p in candidates():
        text=p.read_text(encoding="utf-8", errors="replace")
        fm,raw,body,had=split_fm(text)
        total+=1; dirs.add(p.parent)
        top=p.relative_to(ROOT).parts[0]; by_top[top]=by_top.get(top,0)+1
        if is_conformant(fm): already+=1
        elif had: skip_partial+=1; need+=1
        else: need+=1
    print(f"candidate concept docs: {total}")
    print(f"  already conformant (4 keys): {already}  -> skip")
    print(f"  need frontmatter (none/partial): {need}  (of which had partial fm: {skip_partial})")
    print(f"  => local-LLM description calls needed: ~{need}")
    print(f"directories that would get an index.md: {len(dirs)}")
    print("per top-level project (candidate docs):")
    for k,v in sorted(by_top.items(), key=lambda x:-x[1]): print(f"  {v:4d}  {k}")

def run_frontmatter():
    changed=skipped=llm=0
    for p in candidates():
        text=p.read_text(encoding="utf-8", errors="replace")
        fm,raw,body,had=split_fm(text)
        parseable = isinstance(fm,dict) and "__unparseable__" not in fm
        if is_conformant(fm): skipped+=1; continue
        if had and not parseable:   # malformed YAML, never auto-rewrite (would destroy their content)
            print(f"[skip-unparseable] {p.relative_to(ROOT)}, fix by hand"); skipped+=1; continue
        existing = fm if parseable else {}
        # only compute what's MISSING (preserves existing keys; minimizes LLM calls)
        add = {}
        title = existing.get("title")
        if not title: title = h1_title(body, p); add["title"]=title
        if not existing.get("type"): add["type"]=infer_type(p, title)
        if not existing.get("timestamp"): add["timestamp"]=timestamp(p)
        if not existing.get("description"):
            d = llm_description(title, body)
            if d: llm+=1
            add["description"] = d or first_sentence(body)
        order = ["type","title","description","timestamp"]
        add_lines = [f"{k}: {yq(str(add[k]))}" for k in order if k in add]
        if had and parseable:
            new = "---\n" + "\n".join(raw + add_lines) + "\n---\n\n" + body   # lossless: keep existing lines
        else:  # no fm, or unparseable fm we couldn't trust -> fresh block
            allk = {**{k:existing.get(k) for k in order if existing.get(k)}, **add}
            new = "---\n" + "\n".join(f"{k}: {yq(str(allk[k]))}" for k in order) + "\n---\n\n" + body
        if not new.endswith("\n"): new += "\n"
        p.write_text(new, encoding="utf-8")
        changed+=1
        tag = "" if (had and parseable) else " [rebuilt]"
        print(f"[{changed}] {p.relative_to(ROOT)}{tag}")
    print(f"\nDONE: {changed} written ({llm} via local LLM), {skipped} already-conformant skipped")

def _has_content(D):
    for p in D.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in p.parts): continue
        if p.name in SKIP_NAMES or p.name in RESERVED: continue
        if in_foreign_repo(p, FOREIGN_REPOS): continue
        return True
    return False

def _direct_docs(D):
    out=[]
    for p in sorted(D.iterdir()):
        if p.is_file() and p.suffix==".md" and p.name not in SKIP_NAMES and p.name not in RESERVED:
            if in_foreign_repo(p, FOREIGN_REPOS): continue
            out.append(p)
    return out

def _meta(p):
    fm,raw,body,had = split_fm(p.read_text(encoding="utf-8", errors="replace"))
    title = (fm or {}).get("title") or h1_title(body, p)
    desc = (fm or {}).get("description") or ""
    return str(title), str(desc)

def run_indexes():
    top_level = {c for c in ROOT.iterdir() if c.is_dir() and c.name not in EXCLUDE_DIRS}
    dirs={ROOT}
    for p in candidates(): dirs.add(p.parent)
    for d in top_level:
        if _has_content(d): dirs.add(d)
    created=skipped=0
    for D in sorted(dirs):
        if any(part in EXCLUDE_DIRS for part in D.parts): continue
        if in_foreign_repo(D, FOREIGN_REPOS): continue
        idx = D/"index.md"
        if idx.exists(): skipped+=1; continue
        is_root = (D==ROOT) or (D in top_level)
        subs=[c for c in sorted(D.iterdir()) if c.is_dir() and c.name not in EXCLUDE_DIRS and _has_content(c)]
        lines=[f"# {D.name or 'Index'}", ""]
        for c in subs: lines.append(f"* [{c.name}/]({c.name}/)")
        if subs: lines.append("")
        for p in _direct_docs(D):
            title,desc = _meta(p)
            title = title.replace("]"," ").replace("["," ")
            lines.append(f"* [{title}]({p.name})" + (f" - {desc}" if desc else ""))
        content="\n".join(lines).rstrip()+"\n"
        if is_root: content='---\nokf_version: "0.1"\n---\n'+content
        idx.write_text(content, encoding="utf-8"); created+=1
    print(f"indexes: {created} created, {skipped} existing skipped")

if __name__ == "__main__":
    if MODE=="inventory": run_inventory()
    elif MODE=="frontmatter": run_frontmatter()
    elif MODE=="indexes": run_indexes()
    else: print("unknown mode")
