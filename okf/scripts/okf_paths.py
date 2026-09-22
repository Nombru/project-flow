"""Shared path filtering for the OKF scripts.

An OKF bundle is the docs *you* own. Almost every project under a bundle is a
git repo of your own, and those must be processed normally, so "is a nested
git repo" is NOT the test. The test is ownership: a repo cloned from someone
else (a vendored dependency, an upstream checkout kept for reference) is their
source tree. Enriching it writes frontmatter into files you do not own, dirties
that repo's working tree, and contaminates any diff against its upstream.

A nested repo is treated as FOREIGN when its `origin` remote resolves to an
owner outside `owned_owners()`. A repo with no remote is treated as yours,
local-only projects are common and must keep working.

Set OKF_OWNERS to override detection, e.g. `OKF_OWNERS=Nombru,my-org`.
"""
import os
import pathlib
import re
import subprocess
from functools import lru_cache

_OWNER_RE = re.compile(r"[:/]([^/:]+)/[^/]+?(?:\.git)?/?$")


def _remote_owner(repo_dir):
    """Owner segment of a repo's origin URL, lowercased, or None."""
    try:
        url = subprocess.run(
            ["git", "-C", str(repo_dir), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    if not url:
        return None
    m = _OWNER_RE.search(url)
    return m.group(1).lower() if m else None


@lru_cache(maxsize=1)
def owned_owners():
    """Account names whose repos count as yours.

    OKF_OWNERS wins. Otherwise fall back to the gh CLI's authenticated login,
    then git's `github.user`. If none resolve, returns an empty set, callers
    then treat every repo as owned, preserving the previous behaviour rather
    than silently skipping content.
    """
    env = os.environ.get("OKF_OWNERS", "")
    if env.strip():
        return frozenset(o.strip().lower() for o in env.split(",") if o.strip())
    for cmd in (["gh", "api", "user", "-q", ".login"],
                ["git", "config", "--get", "github.user"]):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=15).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            continue
        if out:
            return frozenset({out.lower()})
    return frozenset()


def foreign_repo_roots(root, exclude_dirs=frozenset()):
    """Directories below `root` that are git repos belonging to someone else.

    Detects a `.git` directory (clone) or `.git` file (submodule/worktree).
    The bundle root itself is never foreign. Returns an empty set when
    ownership cannot be determined, so nothing is skipped by accident.
    """
    root = pathlib.Path(root).resolve()
    owners = owned_owners()
    if not owners:
        return frozenset()
    foreign = set()
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        here = pathlib.Path(dirpath)
        is_repo = ".git" in dirnames or ".git" in filenames
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        if here == root or not is_repo:
            continue
        owner = _remote_owner(here)
        if owner is not None and owner not in owners:
            foreign.add(here)
            dirnames[:] = []  # everything below belongs to that repo
    return frozenset(foreign)


def in_foreign_repo(path, foreign_roots):
    """True if `path` lives inside one of `foreign_roots`."""
    if not foreign_roots:
        return False
    p = pathlib.Path(path).resolve()
    return any(r == p or r in p.parents for r in foreign_roots)
