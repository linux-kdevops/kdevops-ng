#!/usr/bin/env python3
# SPDX-License-Identifier: copyleft-next-0.3.1
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the commit checks on each commit of a range.

    check.py [RANGE]    each commit of RANGE, oldest first
    check.py --tip      only the last commit of the range

RANGE defaults to what HEAD has and upstream/main lacks, or origin/main
where no upstream exists, or all of HEAD's history where neither does.
Each commit is checked in a detached worktree of its own, with the scripts
of that commit, so every commit of a series passes and not only its tip.
Merges are skipped. The worktrees and the logs are under the git
directory: a run that passes removes them, and a run that fails leaves
them and prints where.
"""

import argparse
import os
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from subprocess import DEVNULL, STDOUT

# A check is a command line that starts with a file of the commit's tree and
# runs at the top of that tree. A commit without the file skips the check.
CHECKS: tuple[tuple[str, ...], ...] = (("scripts/check-style.sh",),)
BASES = ("refs/remotes/upstream/main", "refs/remotes/origin/main")
# Git does not promise that two worktree commands can run at once.
WORKTREE = threading.Lock()


def git(*args: str) -> str:
    """Return what a git command prints; git reports its own failure."""
    return subprocess.check_output(["git", *args], text=True).strip()


def default_range() -> str:
    """Return what to check when the command line names no range."""
    found = git("for-each-ref", "--format=%(refname)", *BASES).split()
    return next((f"{base}..HEAD" for base in BASES if base in found), "HEAD")


def clean(root: Path) -> None:
    """Remove the worktrees and logs under root, whichever run left them."""
    for line in git("worktree", "list", "--porcelain").splitlines():
        key, _, path = line.partition(" ")
        if key == "worktree" and root in Path(path).resolve().parents:
            git("worktree", "remove", "--force", path)
    shutil.rmtree(root, ignore_errors=True)


def check(root: Path, sha: str) -> tuple[str, str]:
    """Check one commit in a worktree of its own; return the verdict and the log."""
    tree = root / sha
    with WORKTREE:
        git("worktree", "add", "--detach", "--quiet", str(tree), sha)
    commands = [[str(tree / name), *args] for name, *args in CHECKS]
    log = root / f"{sha}.log"
    with log.open("w") as out:
        codes = [
            subprocess.call(command, cwd=tree, stdin=DEVNULL, stdout=out, stderr=STDOUT)
            for command in commands
            if Path(command[0]).is_file()
        ]
    if not codes:
        return "no checks", ""
    return ("FAILED", log.read_text(errors="replace")) if any(codes) else ("ok", "")


def main() -> int:
    """Check the commits the command line names; return the exit status."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").partition("\n")[0])
    parser.add_argument("range", metavar="RANGE", nargs="?", help="as git rev-list")
    parser.add_argument("--tip", action="store_true", help="only the last commit")
    parser.add_argument("--jobs", metavar="N", type=int, default=os.cpu_count())
    args = parser.parse_args()
    # Git exports these to a hook. Inherited, GIT_INDEX_FILE makes a
    # worktree's checkout write the caller's index.
    for name in git("rev-parse", "--local-env-vars").split():
        os.environ.pop(name, None)
    # Without --topo-order, commits of one second can list a child first.
    series = ("--reverse", "--topo-order", "--no-merges", "--no-commit-header")
    revs = args.range or default_range()
    listed = git("rev-list", *series, "--format=%H %s", revs).splitlines()
    commits = [line.partition(" ")[::2] for line in listed]
    if args.tip:
        commits = commits[-1:]
    root = Path(git("rev-parse", "--git-path", "kdevops-ng-check")).resolve()
    clean(root)
    root.mkdir(parents=True)
    failed = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        verdicts = pool.map(partial(check, root), [sha for sha, _ in commits])
        for (sha, subject), (verdict, log) in zip(commits, verdicts, strict=True):
            print(f"{sha[:12]} {subject}: {verdict}", flush=True)
            if verdict == "FAILED":
                print(log.rstrip("\n"))
                failed += 1
    if failed:
        print(f"{failed} of {len(commits)} commits failed; see {root}")
        return 1
    clean(root)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)
