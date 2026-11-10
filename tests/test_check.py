# SPDX-License-Identifier: copyleft-next-0.3.1
"""Test scripts/check.py on a throwaway repository."""

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from subprocess import PIPE

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check.py"
# A hook's GIT_DIR aims git at the caller's repository, and the caller's
# configuration can sign or refuse a commit: the tests take neither.
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")} | {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}
GIT = ("git", "-c", "user.name=A Tester", "-c", "user.email=tester@example.org")
HASH = re.compile("^[0-9a-f]{12} ", re.MULTILINE)
PASSES = "#!/bin/sh\necho style: OK\n"
FAILS = "#!/bin/sh\ngit log --max-count=1 --format='no tab in %s'\nexit 1\n"


class CheckTest(unittest.TestCase):
    """Each test builds a history and reads the report of a run on it."""

    def setUp(self) -> None:
        self.repo = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.left = self.repo / ".git" / "kdevops-ng-check"
        self.git("init", "--quiet", "--initial-branch=main")

    def git(self, *args: str) -> str:
        command = [*GIT, *args]
        return subprocess.check_output(command, cwd=self.repo, env=ENV, text=True)

    def commit(self, subject: str, style: str = "") -> None:
        if style:
            script = self.repo / "scripts" / "check-style.sh"
            script.parent.mkdir(exist_ok=True)
            script.write_text(style)
            script.chmod(0o755)
            self.git("add", "scripts")
        self.git("commit", "--quiet", "--allow-empty", "--message", subject)

    def series(self) -> None:
        """Commit one of each verdict, and a tip that passes."""
        self.commit("x: one")
        self.commit("x: two", PASSES)
        self.commit("x: bad", FAILS)
        self.commit("x: fix", PASSES)

    def check(self, *args: str, **env: str) -> tuple[int, list[str]]:
        """Run the script under test; return its status and report, less each hash."""
        command = [sys.executable, str(SCRIPT), *args]
        done = subprocess.run(
            command, cwd=self.repo, env=ENV | env, check=False, stdout=PIPE, text=True
        )
        return done.returncode, re.sub(HASH, "", done.stdout).splitlines()

    def test_commit_without_checks_passes(self) -> None:
        self.commit("x: one")
        self.assertEqual(self.check(), (0, ["x: one: no checks"]))

    def test_each_commit_runs_its_own_check(self) -> None:
        self.series()
        status, report = self.check("--jobs", "2")
        self.assertEqual(status, 1)
        self.assertEqual(
            report[:3], ["x: one: no checks", "x: two: ok", "x: bad: FAILED"]
        )
        self.assertEqual(report[3:5], ["no tab in x: bad", "x: fix: ok"])
        self.assertEqual(report[5], f"1 of 4 commits failed; see {self.left}")
        failed = self.git("rev-parse", "HEAD~1").strip()
        self.assertTrue((self.left / failed / "scripts" / "check-style.sh").is_file())
        self.assertEqual(
            (self.left / f"{failed}.log").read_text(), "no tab in x: bad\n"
        )

    def test_passing_run_removes_what_a_failed_run_left(self) -> None:
        self.series()
        self.assertEqual(self.check("HEAD~2..HEAD")[0], 1)
        self.assertEqual(self.check("HEAD~1..HEAD"), (0, ["x: fix: ok"]))
        self.assertFalse(self.left.exists())
        self.assertEqual(self.git("worktree", "list").count("\n"), 1)

    def test_tip_checks_the_last_commit_only(self) -> None:
        self.series()
        self.assertEqual(self.check("--tip"), (0, ["x: fix: ok"]))
        self.assertEqual(self.check("--tip", "HEAD~1")[0], 1)

    def test_default_range_starts_at_the_remote_main(self) -> None:
        self.series()
        self.git("update-ref", "refs/remotes/origin/main", "HEAD~3")
        self.assertEqual(len(self.check()[1]), 5)
        self.git("update-ref", "refs/remotes/upstream/main", "HEAD~1")
        self.assertEqual(self.check(), (0, ["x: fix: ok"]))

    def test_merge_is_skipped(self) -> None:
        self.commit("x: one")
        self.git("switch", "--quiet", "--create", "topic")
        self.commit("x: two")
        self.git("switch", "--quiet", "main")
        self.git("merge", "--quiet", "--no-ff", "--message", "Merge topic", "topic")
        self.assertEqual(self.check()[1], ["x: one: no checks", "x: two: no checks"])

    def test_index_of_the_checkout_is_left_alone(self) -> None:
        self.commit("x: two", PASSES)
        (self.repo / "staged").write_text("kept\n")
        self.git("add", "staged")
        index = str(self.repo / ".git" / "index")
        self.assertEqual(self.check(GIT_INDEX_FILE=index), (0, ["x: two: ok"]))
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "staged\n")
