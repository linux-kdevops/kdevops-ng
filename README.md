<!-- SPDX-License-Identifier: copyleft-next-0.3.1 -->

# kdevops-ng

kdevops-ng automates Linux kernel development and testing. It derives from
[kdevops](https://github.com/linux-kdevops/kdevops) and keeps its goal: get
a kernel developer from a tree to test results in a few commands.

A tool such as `make` or `git` does the work. A task, a Bash executable,
runs the commands a developer would type to reach one goal. A workflow
orders the tasks, in the language of the engine that runs it; the tasks are
tied to no engine.
[designs/principles.md](designs/principles.md) holds the seven rules
everything follows, and [designs/tasks.md](designs/tasks.md) draws the
lines between a tool, a task and a workflow.

## Tasks

A task runs by hand, and `--help` prints what it takes:

```sh
tasks/kernel/kconfig --directory ~/linux --target tinyconfig
```

It configures a Linux tree with the host's `make` and compiler, in
`build/` of the tree, and changes no file the tree tracks. `ARCH` and
`LLVM` are kbuild's own and come from the environment.

## Contributing

Patches go to <kdevops@lists.linux.dev>, written as
[designs/writing.md](designs/writing.md) asks. `AGENTS.md` is the map for
agents.

kdevops-ng is written with coding assistants; a person reviews and signs off
every commit.

License: copyleft-next-0.3.1.
