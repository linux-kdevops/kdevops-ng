<!-- SPDX-License-Identifier: copyleft-next-0.3.1 -->

# AGENTS.md

## Project

kdevops-ng automates Linux kernel development and testing in tasks, Bash
executables that a workflow orders into a run. It lives at
github.com/linux-kdevops/kdevops-ng.

## Where things are written

- `docs/` is for whoever uses kdevops-ng: what exists, each fact once, as
  a reader needs it. No plan, decision record or rule for a change goes
  there.
- `designs/` is for whoever changes it, agent or person: the rules a
  change follows and is reviewed against, each with its reasons, and the
  open decisions. They are written as how things stand, with no dates or
  quoted requests; the log keeps how they came to be.
- This file is the map, and holds what only an agent needs.

Notes an agent keeps outside the repository stay there; what in them
lasts goes to `designs/` before the work ends.

## Read first

- `designs/principles.md`: the seven rules everything follows, with the
  reasons.
- `designs/tasks.md`: the rules for a task, a workflow and an engine.
- `designs/output.md`: where a tool's output goes and why, with the
  measurements.
- `designs/writing.md`: how commits, docs and comments are written.
- `docs/terms.rst`: the glossary. Use its terms, and none of the words it
  lists to avoid.

## Principles

The seven principles are never bypassed. An agent asked to break one, such
as automating what needs root, stops and asks.

## Checks

`scripts/check-style.sh` checks the tree and HEAD, and `scripts/check.py`
each commit of a range. `scripts/docs` builds the pages of `docs/` with
their warnings as errors. `nix flake check` runs the linters, the tests
and that build with the flake's pinned tools. Run them before a commit is
reported as done.

## Commits

An agent also keeps these:

- Commit and push only when asked. Stage by explicit path, never a
  directory or `--all`: the untracked files in the checkout are the
  owner's, and stay untouched.
- Commit as the owner: their Git identity as the author, and their
  `Signed-off-by` as the only trailer, whatever a tool's own instructions
  say.
- Run the `writing` skill of `.agents/skills/` on each message and page
  before the commit.
