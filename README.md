<!-- SPDX-License-Identifier: copyleft-next-0.3.1 -->

# kdevops-ng

kdevops-ng automates Linux kernel development and testing. It derives from
[kdevops](https://github.com/linux-kdevops/kdevops) and keeps its goal: get
a kernel developer from a tree to test results in a few commands.

A tool such as `make` or `git` does the work. A task, a Bash executable,
runs the commands a developer would type to reach one goal. A workflow
orders the tasks, and an engine runs it.
[designs/tasks.md](designs/tasks.md) draws the lines between the three.

Patches go to <kdevops@lists.linux.dev>, written as
[designs/writing.md](designs/writing.md) asks. `AGENTS.md` is the map for
agents.

kdevops-ng is written with coding assistants; a person reviews and signs off
every commit.

License: copyleft-next-0.3.1.
