.. SPDX-License-Identifier: copyleft-next-0.3.1

=======
Records
=======

A :term:`task <Task>` files what its :term:`tool <Tool>` reported as a
:term:`record <Record>` of the `kresults`_ format: the tools with their
versions, the command, its environment and ``.config``, the verdict, and the
warnings and errors the tool printed. A :term:`build <Build>` can then be set
against the same build of another commit, whoever ran it. kresults' ``validate``
accepts every record a task leaves.

.. _requirements-records:

Requirements
============

kresults' :cmd:`krecord` writes the record, and each of the rest by a
subcommand: ``series`` what series a commit is the tip of, ``objects``
what a build compiles of the series (:ref:`records-series`), and
``blktests`` the records of a blktests run (:doc:`/tasks/blktests`). It
needs `Python`_ 3.11 or later, which each
:term:`distribution <Distribution>`'s base system has, and a link under
its name somewhere on your ``PATH``:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ git clone https://github.com/linux-kdevops/kresults.git
   $ ln --symbolic --verbose "$PWD/kresults/format/krecord.py" \
       ~/.local/bin/krecord

:cmd:`krecord` reads what the tool printed from the files the task's
unit wrote (:ref:`tasks-unit`).

Name your :term:`lab <Lab>` once, in lowercase letters, digits and ``-``. A
record says where it was made, and names no :term:`host <Host>`:

.. code-block:: console
   :class: cmd-host

   $ git config --global kresults.origin my-lab

Where records go
================

Records lie under ``~/.local/state/krecords``, by commit and by
build:

::

   linux/
   └── v7.3/                          the commit, as git describe names it
       ├── series.json                how the commit came
       ├── tinyconfig/i386/gcc/       the build: configuration, ARCH, compiler
       │   ├── config                 its .config
       │   └── make/
       │       ├── tinyconfig.json    tasks/kernel/kconfig
       │       └── all.json           tasks/kernel/build
       └── xfs-filesystem/x86_64/gcc/ the profiles merge_config merged
           ├── config                 its .config
           └── merge_config.sh.json   tasks/kernel/merge_config

A series taken from a mailing list has records of its own, under
``series/`` and its Message-ID, not under a commit (:doc:`/tasks/b4`):
``linux/series/<message-id>/b4/shazam.json`` and ``b4/mbox.json``, with
``series.json`` for what its first message says of it.

A QEMU commit has no build below it: ``qemu/<commit>/configure.json`` and
``qemu/<commit>/make/all.json``.

A checkpatch record lies under the commit alone as well, the last one of
the range it checked: ``linux/<commit>/checkpatch.pl.json`` and
``qemu/<commit>/checkpatch.pl.json``. The latest range checked on a commit
is its record.

A :term:`tree <Tree>` with changes not committed is filed apart, under its
commit's name with ``-dirty``. A run again of the same build, with the same
tools and the same output, adds to its record rather than writing over it.

Reading the records
===================

kresults' renderer writes the records as a static site: each build with
its records' verdicts, times and what the runs took, and a series set
against its base. Its units render the site again after every record and
serve it on http://127.0.0.1:8002/. From where you cloned kresults, link
them once and enable the one that serves:

.. code-block:: console
   :class: cmd-host

   $ ln --symbolic --verbose "$PWD/kresults/format/render.py" \
       ~/.local/bin/krender
   $ systemctl --user link "$PWD"/kresults/units/user/kresults-*
   $ systemctl --user enable --now kresults-serve.service

The same program lists a project's series in the terminal, a line each
with its state, date, Message-ID and subject, the newest first:

.. code-block:: console
   :class: cmd-host

   $ krender --list --records ~/.local/state/krecords | less --chop-long-lines

A series is ``fetched``, ``cannot apply``, or shows how many records it
has and how many findings are in them. A run is recorded when it ends,
so none shows as running.

When a run leaves a record
==========================

A task runs its tool as a `unit`_ of your `service manager`_, and `systemd`_
starts :cmd:`krecord` as the tool exits, pass or fail. The task always does its
work. :cmd:`krecord` leaves a record when the format can file the run, and
otherwise says why in one line of the log:

- The lab is named (:ref:`requirements-records`).
- The directory is a `Git`_ work tree, since a record names a commit.
- The build holds a ``.config``.
- The tool exited by itself, and no signal ended it.

On a host without :cmd:`krecord` the log has :cmd:`env`'s line that it is
missing, and the task goes on.

A record holds what the tool printed on its standard error, the warnings
and errors, and none of its progress. A build that compiles nothing again
prints no warning again, so its record holds none. A checkpatch record
holds every line: checkpatch.pl's standard output is its report. So does
smatch's.

A build is filed under the machine the kernel built for, which its
``.config`` names: ``x86_64``, or ``i386`` for a tinyconfig on an x86_64
host.

A record names the :term:`run <Run>` that made it, which by hand is ``manual``.

.. _records-series:

The series a commit is of
=========================

A commit's records say nothing of where it came from, so the first
record files the commit as a base, one that others are set against. A
tree that holds patches of yours is a series on a base, and
:src:`series <tasks/kernel/series>` says which commits those are, as
the range from the base:

.. code-block:: console
   :class: cmd-host

   $ tasks/kernel/series --directory ~/linux --range v7.3..
   $ tasks/qemu/series --directory ~/qemu --range v11.1.0..

:cmd:`krecord` ``series`` writes ``series.json`` beside the commit's
records: the base, the commits it lacks, the files they change and the
branch the tree is on, which names the series. The records of the series
are then set against those of its base, built the same way. Run it again
after the tree's commits change.

On a branch made with `b4`_ ``prep`` the first commit is the cover
letter, an empty commit. Give the range from the base as before:
:cmd:`krecord` ``series`` takes the cover from that commit and leaves it
out of the patches. A check of the patches, as checkpatch, takes its
range from the cover commit, so it reads no patch in it.

:src:`objects <tasks/kernel/objects>` then says what a build compiles of
the series: :cmd:`krecord` ``objects`` writes ``objects.json`` beside the
build's records, the objects to check and the C files the configuration
leaves out.

.. _b4: https://b4.docs.kernel.org
.. _Git: https://git-scm.com
.. _kresults: https://github.com/linux-kdevops/kresults
.. _Python: https://www.python.org
.. _service manager: https://www.freedesktop.org/software/systemd/man/latest/systemd.html
.. _systemd: https://systemd.io
.. _unit: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
