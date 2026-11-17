<!-- SPDX-License-Identifier: copyleft-next-0.3.1 -->

# Where a tool's output goes

A task's unit writes what its tool prints to two files, and everything
that reads the output reads those files. `tasks/common/unit` is the
code, rules U1 and U2 of `designs/tasks.md` the short form. This page
holds the reasons and the measurements, so a change to it starts from
them.

## 1. The files

```text
build/logs/<subsystem>-<task>/stdout
build/logs/<subsystem>-<task>/stderr
build/logs/<subsystem>-<task>/<object>/stdout    a task that checks one object
```

- They are in `build/` of the tree a task is given, which is the one
  place in a tree a unit may write (principle 4). A tree with no build
  of its own gets a `build/` for them.
- No directory is named for the commit. A run empties its two files
  first, so nothing grows and nothing needs removing, and the record
  says which commit a run was on. `build/logs/` sits beside kbuild's own
  directories, so no task could tell which others to delete.
- A task that checks one object has a directory for each, so two checks
  of one tree do not share a file.
- A file a later task reads, as a series' cover mail, goes in the
  directory of the task that wrote it.

## 2. Why not the journal

The journal drops lines of a unit that prints fast. A unit that printed
30,001 lines gave back 24,991, and an empty line was gone. The same unit
writing to a file kept 30,002 of 30,002. A record or a task that reads a
tool's output back must get all of it, so neither reads the journal.

The journal also needed setup on the host: storage on disk for a user's
journal, and the identifier trick, since journald names a line's unit
only while the process that wrote it lives.

## 3. Why systemd writes them

`StandardOutput=append:FILE` and `StandardError=append:FILE` are
settings on the logged `systemd-run` line. No task captures output with
shell of its own, and the files are complete when `ExecStopPost=` runs
`krecord`.

- Two files, not one. A record holds a tool's warnings and errors, its
  standard error (R2). The order between a line of one file and a line
  of the other is lost, which costs a record nothing: a compiler's
  warning names its own file.
- `append:`, with the files emptied before the run. `truncate:` empties
  them again as each command of the unit starts, `ExecStopPost=`
  included, and `krecord` would read nothing.
- No `tee`. `systemd-run --pipe` hands the unit the task's own streams
  and overrides `StandardError=`, so a file would need a pipeline in the
  task, and `krecord` could run before `tee` had written the last
  lines. A setting takes one target: systemd has no file-and-terminal
  form.
- What `krecord` prints lands in the same files, after it has read
  them, and is in no record.

## 4. Why tail, and the sleep

With the output in files the terminal shows nothing, so `tail --follow`
shows the two files as they grow. `tail --pid=PID` reads what is left
and exits once PID is gone. The task cannot be that process, or tail
would print after the task returned, and killing tail outright can lose
the last lines. So the task starts a `sleep infinity` for tail to
watch, and ends it when the unit is done.

Showing nothing while the tool runs and printing the files at the end
would drop both lines. A build then looks hung for minutes.

## 5. The unit's name

`<subsystem>-<task>-<pid>.service`, the pid being the task's.

- A name the task knows. `systemd-run --wait` leaves its unit running
  when it is interrupted, and the task stops it by name (U6).
- No directory in it. Whether two runs may work on one tree at a time
  is a workflow's to say (T5), and the name refuses nothing.
- The dashes are systemd's own prefix form: a drop-in in
  `kernel-build-.service.d/` reaches every run of the task (U5).

## 6. Why the task changes to the tree

`systemd-run` looks up a tool named by a relative path, as
`scripts/checkpatch.pl`, from the directory it is started in, not from
`--working-directory`. The task changes to the tree first, as a
developer would, and the paths of its log are relative to it.
