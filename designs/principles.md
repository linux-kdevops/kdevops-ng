<!-- SPDX-License-Identifier: copyleft-next-0.3.1 -->

# Principles

Seven rules hold everywhere in kdevops-ng, and a change that breaks one is
reworked rather than merged.

## 1. User mode only

kdevops-ng runs everything as the developer, without root, and drives the
developer's own service manager (`systemctl --user`), never the system
one. What needs root the developer does once, by hand, from the list in
the documentation. No task or script runs, wraps or prints it, and a task
that finds it missing points to that list. A run thus never changes the
host behind the developer's back. In a guest that a run boots, a machine
the run made for itself, tasks act as root over SSH.

## 2. The host provides the tools

A task runs each tool by its name, from `PATH`, and never fetches one or
installs a package. The host's distribution provides the tools, and the
developer installs them from the list the documentation gives for it.
[Nix] is one of the distributions and the preferred one, for
reproducibility: it pins every tool, so two hosts given the same inputs
run the same tools and a bug found on one reproduces on the other. The
others ship what they ship that day.

What only one distribution can do, such as adding a build to the Nix
store, is a task of its own, which a workflow runs only there. No host
takes a tool from a container or from a language's package manager.

A developer who wants a tool newer than the distribution's gives its
tree to the tasks that build it and install it for that user alone,
under `~/.local` as [UAPI.9] sorts a user's files. That needs no root,
and the tool is then one more on `PATH`.

## 3. systemd first

Anything that runs for a while is a [systemd] unit of the developer's
service manager, so restarts, timeouts, dependencies, logging, scheduling
and resource limits come from the service manager, not from custom
daemons, PID files, polling loops or cron jobs. A unit a task starts for
its tool takes its settings on the command line that starts it, so the log
shows them and nothing is installed for it. A unit that stays, as a timer
or a server, is a unit file with specifiers and drop-ins, and an upstream
template comes before a new one. A developer's own limit on either is a
drop-in of theirs.

## 4. Everything runs in a sandbox

A task changes no file that a tree a person works in tracks. In a tree it
is given, it writes only where its tool keeps what it makes apart from the
sources, as kbuild keeps a build in `build/`. A tool with no build
directory, as smatch, builds beside its sources in the files its
`.gitignore` names, in a clone the developer keeps for the build. A
task that applies a series commits it in a worktree the developer adds
for that series. What
tasks share lives in the directory of the tool that owns it, under
`~/.local/state` or `~/.cache` as [UAPI.9] sorts a user's files, and a
tool a task installs under `~/.local/lib` and `~/.local/bin`. Beyond
those places a task writes only scratch under `$TMPDIR`, never a
configuration file of the developer's. A task's unit enforces what it
can: a kernel task's make sees the tree and the developer's home
read-only.

## 5. Commands a developer can run

Whatever kdevops-ng does, a developer can do by hand. A task's log is a
transcript of the commands it ran, and names every file it writes. Nothing
hides behind a module, as [Ansible]'s do: if a task starts a unit, the log
shows the `systemctl` line. A shell string handed to `sh -c` is a last
resort, printed whole. A failed run thus reproduces from its log alone.

## 6. Simple tasks

A task runs the commands a developer would type, plainly, with no code for
a case that has not happened. Work goes to what is built for it: the tool
does the work, the host provides the tools, systemd runs what lasts, and an
engine orders, repeats and chooses. A task holds only what none of them
can, so it does not loop over work, retry, choose how to work or run
another task, and it copies no logic another task holds. KISS, DRY, YAGNI
and SRP are the measure, and `designs/tasks.md` turns them into the rules
a change is reviewed against.

## 7. The engine is replaceable

The work is in the tasks, which run by hand with no engine and read no
variable of one. A workflow is its engine's own: a file in that engine's
language that holds the control flow and nothing else. Any engine can thus
drive the tasks, and several can be supported side by side. Bash is the
first, and whoever wants [Dagu], Ansible or a CI system writes the
workflow there. No format defines a workflow for every engine, so one is
written again for each, which stays cheap while it holds only control
flow.

[Ansible]: https://docs.ansible.com/
[Dagu]: https://github.com/dagucloud/dagu
[Nix]: https://nixos.org
[systemd]: https://systemd.io
[UAPI.9]: https://uapi-group.org/specifications/specs/linux_file_system_hierarchy/
