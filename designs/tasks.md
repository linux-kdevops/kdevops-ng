<!-- SPDX-License-Identifier: copyleft-next-0.3.1 -->

# Tools, tasks and workflows

A change to a task or a workflow is reviewed against these rules, and a
finding cites one by its number. No workflow exists yet, and of the tasks
named below only `tasks/kernel/kconfig`, `tasks/kernel/build` and
`tasks/kernel/checkpatch` do: the other names show the form.

## 1. Three layers

The tool works, the task binds, the workflow decides.

- A tool does the work: `make`, `git`, `b4`, a script of the kernel's.
- A task binds a tool to a goal. It is a Bash executable under `tasks/`
  that runs the commands a developer would type to reach one goal, with
  the place, the tool's flags and the project's settings filled in.
- A workflow decides which tasks run, in what order, for which items of a
  list, on which earlier result, and how often again. It is written for
  one engine, in that engine's language, and is that engine's own (section
  5).

`docs/terms.rst` defines the words these rules use, and the ones to
avoid. A place is a directory a task works in, such as a worktree or a
build directory. A file or a tree that a task works on is not a place,
whatever its path. An engine's own words name only that engine's things,
as "DAG" and "step" are Dagu's.

[kdevops] is written in Ansible, whose layers map as:

| Ansible                                           | kdevops-ng     |
| ------------------------------------------------- | -------------- |
| playbook, and a task's `when`, `loop`, `register` | workflow       |
| task: a name, a module and its arguments          | task           |
| module: `community.general.make`                  | tool: `make`   |
| role defaults and variables                       | `tasks/common` |

An Ansible task carries its own conditions and loops; here those are the
workflow's (T5). An Ansible module wraps its tool to run it on a managed
host and to report what changed. A task runs where it is started and its
tool reports for itself, so nothing stands between the two (T1).

## 2. The rules

### T1. The tool does the work

A task calls the tool built for the job and copies no logic a tool holds.
It runs the tool by its own command line, and its log is those lines as
Bash traces them, so a developer can run any of them again. Shell that
tasks share, under `tasks/common`, gives a task values, such as a place or
an argument array, and never a function that runs the tool for it.

### T2. A task is named for what a developer asks for

A task is `tasks/<subsystem>/<name>`, the subsystem being what its tasks
work on. The name is a verb where the tool's name does not say what is
asked, `tasks/kernel/build`, and the tool's own name where its verdict is
what is asked, `tasks/kernel/sparse`. No directory is made up to sort
tasks, as `check/` would be.

### T3. A task binds what a developer would have to look up

Its caller says what to work on, never how: no flag of the tool, no place
to work in, no number of jobs. Where a tool runs two ways the task takes
one, as `tasks/kernel/checkpatch` runs `checkpatch.pl` with `--strict`.

### T4. One goal, and it reruns alone

A task is split where a developer would rerun one part and not the other.
After it fails, a developer fixes the cause and runs that task again,
alone, so a task reaches its goal from whatever an earlier run of it left.
A test that makes the second run safe, as adding a worktree only where it
is missing, is no choice of method (T5). A task that checks object files
takes one each time, so each object has its verdict and is checked again
alone.

### T5. The workflow loops, retries and chooses

A task has no loop over work items, no retry and no sleep. It does not
branch on an input or on another task's result to choose how it works, and
it never runs another task. Where a choice needs a fact, a task prints the
fact and the workflow picks the task that runs (O1). Waiting is a task
that fails until its goal is reached, which the workflow repeats.

A work item is what a developer wants a verdict on and would rerun alone:
a commit to build, an object file to check. A loop that computes one value
from data inside a task is not a loop over work items. Nor is a list the
tool takes on one command line, as `make` takes several targets.

### W1. A workflow holds only control flow

It names the tasks, their order and loops, the conditions and retries, and
what runs as the run ends. It carries no command or flag of a tool, and no
place. Everything else about the work is in the tasks, so a workflow
written for another engine writes the control flow again and nothing more.

### W2. A workflow gives a task its inputs in the task's forms

It passes an option on the task's command line and sets a tool's variable
in the task's environment (I1, I2), whatever form its own inputs take in
its engine. An input keeps the name of what it becomes: `ref` for `--ref`,
`ARCH` for kbuild's.

### W3. A workflow started with only what it works on runs

Each of its inputs but that one has a default that works.

## 3. Why the line is here

### Why not a task for each tool

`tasks/make --directory DIR --jobs N TARGET` would be Ansible's module. It
adds nothing to the tool, and what a task knows moves into the workflows.
sparse on one object file is `make C=2 CF=-Wsparse-error init/main.o`:
with a task for each tool those flags are written once for each engine, in
its language, and no developer can run them by hand from there.

### Why not a task for each workflow

One task that fetches, configures and builds:

- cannot be rerun in part, so a failed build fetches and configures again;
- hides its loops and choices from an engine, which cannot retry or
  resume them;
- leaves one log for several goals, where a failure names none.

### Why not functions that run the tool

A function in `tasks/common` that runs `make` puts its own call in the
log, a line no developer can run, and gives the logic T5 keeps out of a
task somewhere to hide. An argument array, `"${make[@]}"`, shares the
arguments and prints as the command.

## 4. A task's inputs and results

A workflow's own inputs are its engine's: how they are declared, given and
checked is that engine's way (section 5).

- I1. A task takes options, `--option VALUE`, each naming what it works
  on. An option keeps the name its tool gives the argument it becomes, as
  `--directory` is make's own, so nothing is translated between a task and
  its tool. Its usage line shows the one form it accepts. `--help` prints
  the usage, and arguments of any other form print it and fail.
- I2. A task takes from the environment only what exists without
  kdevops-ng. One kind is a variable its tool reads
  that says what to build or check, under the tool's name, as kbuild reads
  `ARCH` and `LLVM`. The task sets no default for it: unset, the tool's
  own default holds, as GCC does without `LLVM`, and the log names each
  one that is set. The other kind is what every program is given: `HOME`,
  `TMPDIR` and XDG's directories.
- I3. A task takes nothing else: no JSON, no file of settings, no variable
  of an engine's.
- O1. A task that reports facts prints them as `name=value` lines, to the
  file `--output` names or to standard output without it. A workflow reads
  them there, uses one in a condition or hands it to a later task as an
  option.

### Why not otherwise

- JSON into a task. A task takes a few strings, so JSON would be a second
  form to document and test in every task.
- The environment for a task's own inputs. A variable left set in a shell
  changes the next task with no trace on its command line. A tool's
  variable is one a kernel developer already exports, and the log names it
  (I2).
- Operands without a name. `--ref v7.3` says in the log what `v7.3` is.

## 5. Engines

An engine runs the workflows written for it. kdevops-ng is tied to none,
and any number can be supported at once: the tasks are the same for all.

- E1. An engine's workflows are under `engines/<engine>/`, in the engine's
  own language and layout. Supporting an engine adds that directory and
  changes no task.
- E2. A workflow belongs to its engine. No format defines one for every
  engine: with nothing to translate it into each engine's language, it
  would be a second copy to keep. A workflow wanted under another engine
  is written again there, which W1 keeps cheap.
- E3. An engine can drive the tasks when it can run a command with
  arguments and an environment, read the `name=value` lines a task prints
  and branch on one or pass it on, repeat a task for each item of a list,
  and run a task again until it passes.

The first engine is [Dagu]. Ansible, a Bash script or a CI system can be
another.

## 6. Writing a task

`tasks/kernel/kconfig` shows the form: the header, the prelude, the
inputs and values, then the commands.

- The header is the lines that start with `##`: the usage line, a sentence
  of what the task does, and the command that runs it by hand. `--help`
  prints it, and arguments of another form print it on the standard error
  and exit with status 2 (I1).
- `tasks/common/task` comes first. It sets Bash's strict mode, gives
  `transcript`, and reads the usage line as the one form the task takes:
  each `--option VALUE` of it, in its order, becomes the variable of the
  option's name. No task tests its arguments or assigns them again.
- Above `transcript` are the values the commands need, such as a place
  or an argument array of `tasks/common`. It stays short, and holds
  nothing a developer would type.
- Below `transcript` are the commands. The log shows each after a `$`
  prompt, as it ran. A command that makes or removes a file or a
  directory, as `mkdir`, `ln` or `rm`, takes `--verbose`, so the log
  shows what changed. A task that fails ends it with its name and the
  exit status of the last command shown.
- A task changes no file that a tree it is given tracks. It writes there
  only where its tool keeps what it makes apart from the sources, as
  kbuild's `O=` keeps a build in `build/` of the tree.

## 7. The unit a task runs in

- U1. A task runs its tool as a transient unit of the developer's service
  manager: `"${unit[@]}"` of `tasks/common/unit`, before the tool's
  command. `systemd-cat` sends the tool's standard output to the journal
  as it is and its standard error as warnings, each line under the
  unit's name as its identifier. `tasks/common/unit` follows that
  identifier with `journalctl` and shows the lines as they come, and the
  tool's exit status is the task's. No task captures,
  times or stores a tool's output itself: the journal does (principle 3).
- U2. The unit is named for the task and the directory it works in, as
  `kernel-build@home-user-linux.service`. A task thus runs once on a
  directory at a time, and `journalctl --user --identifier` with that
  name finds its lines. A match on the unit misses some: journald reads
  a line's unit from the cgroup of the process that wrote it, and a
  process that has exited has none. It trusts the unit a stream names
  only from root, so a developer's units have no other source.
- U3. The unit gets none of the caller's environment. `tasks/common/unit`
  names `PATH` and each of the tool's variables that is set with
  `--setenv`, which puts them in the log (I2). Nothing of kdevops-ng's
  own goes through the unit's environment.
- U4. The unit's settings are options of `systemd-run` on the logged
  line: the directory it runs in, what it sees read-only (principle 4),
  what it may write. `tasks/common/unit` holds the ones every unit takes
  and a task or its `tasks/common` file adds its own in `settings`.
  Nothing is installed on the host for a task to run, and the line
  reproduces the run on any host (principle 5).
- U5. A limit, a timeout or one more writable path is a drop-in under
  the unit's name, the developer's or a workflow's to write under
  `~/.config/systemd/user/`. No task takes an option or a variable for
  one.
- U6. A task that is interrupted stops its unit, with the `systemctl`
  line in the log. `systemd-run` leaves the unit running when a signal
  ends it, and the next run of the task would be refused.

## 8. Records

kdevops-ng is a producer of [kresults] records, in version 1 of the
format: its `validate` accepts every file a task leaves.

- R1. A task that leaves a record names `krecord`'s options in
  `record`, with the command as a developer types it at the top of the
  tree, and `tasks/common/unit` makes them the unit's `ExecStopPost=`.
  `krecord` takes the record's name and the variables to record from
  kresults' `commands.json`, where a command gets its line before a task
  records it. No shell of a task builds the record.
- R2. systemd runs `krecord` as the tool exits, pass or fail, with the
  exit status. `krecord` reads the unit's warnings from the journal and
  writes the record. A tool whose standard output is its report and
  holds no progress, as `checkpatch.pl`'s, is recorded whole: its task
  asks `krecord` for no `--priority`. What else a record holds, when two
  runs are equal and how a tree with changes not committed is filed are
  kresults' to say, and no task repeats them.
- R3. Records go to `~/.local/state/krecords`, `krecord`'s own default
  and the unit's `StateDirectory=`, a plain directory. Nothing commits or
  sends them yet.
- R4. A run that leaves no record still does its work. `krecord` says why
  in one line of the log, and a host without `krecord` gets env's line
  that it is missing. No task tests for either.

- R5. A commit's records are a base's until kresults' `kseries` says
  what series the commit is the tip of. A task gives it the range and
  nothing else: the base, the commits and the files they change are
  `kseries`'s to read from the tree. Nothing guesses the range from the
  tree's remotes, which keep a base such as a `for-next` for a day.

## 9. Review

Check each changed task against T1 to T5, I1 to I3, O1, U1 to U6 and R1,
and each changed workflow against W1 to W3 and E1. A finding names the
rule, the file and line, what fails, and the smaller design.

[Dagu]: https://github.com/dagucloud/dagu
[kdevops]: https://github.com/linux-kdevops/kdevops
[kresults]: https://github.com/linux-kdevops/kresults
