.. SPDX-License-Identifier: copyleft-next-0.3.1

=======
Records
=======

A task files what its tool reported as a record of the `kresults`_ format:
the tools with their versions, the command, its environment and
``.config``, the verdict, and the warnings and errors the tool printed. A
build can then be set against the same build of another commit, whoever
ran it. kresults' ``validate`` accepts every record a task leaves.

.. _requirements-records:

Requirements
============

kresults' :cmd:`krecord` writes the record. It needs Python 3.11 or
later, which each distribution's base system has, and a link under its
name somewhere on your ``PATH``:

.. code-block:: console

   $ git clone https://github.com/linux-kdevops/kresults.git
   $ ln --symbolic --verbose "$PWD/kresults/format/record.py" \
       ~/.local/bin/krecord

:cmd:`krecord` reads what the tool printed from your journal
(:ref:`requirements-journal`).

Name your lab once, in lowercase letters, digits and ``-``. A record says
where it was made, and names no host:

.. code-block:: console

   $ git config --global kresults.origin my-lab

Where records go
================

Records lie under ``~/.local/state/krecords``, by commit and by
build:

::

   linux/
   └── v7.3/                          the commit, as git describe names it
       ├── series.json                how the commit came
       └── tinyconfig/x86/gcc/        the build: configuration, ARCH, compiler
           ├── config                 its .config
           └── make/
               ├── tinyconfig.json    tasks/kernel/kconfig
               └── all.json           tasks/kernel/build

A tree with changes not committed is filed apart, under its commit's name
with ``-dirty``. A run again of the same build, with the same tools and
the same output, adds to its record rather than writing over it.

Reading the records
===================

kresults' renderer writes the records as a static site: each build with
its records' verdicts, times and what the runs took, and a series set
against its base. Its units render the site again after every record and
serve it on http://127.0.0.1:8002/. From where you cloned kresults, link
them once and enable the one that serves:

.. code-block:: console

   $ ln --symbolic --verbose "$PWD/kresults/format/render.py" \
       ~/.local/bin/krender
   $ systemctl --user link "$PWD"/kresults/units/user/kresults-*
   $ systemctl --user enable --now kresults-serve.service

When a run leaves a record
==========================

A task runs its tool as a unit of your service manager, and systemd starts
:cmd:`krecord` as the tool exits, pass or fail. The task always does its
work. :cmd:`krecord` leaves a record when the format can file the run, and
otherwise says why in one line of the log:

- The lab is named (:ref:`requirements-records`).
- The directory is a Git work tree, since a record names a commit.
- The build holds a ``.config``.
- The tool exited by itself, and no signal ended it.

On a host without :cmd:`krecord` the log has :cmd:`env`'s line that it is
missing, and the task goes on.

A record holds what the tool printed on its standard error, the warnings
and errors, and none of its progress. A build that compiles nothing again
prints no warning again, so its record holds none.

A build is filed under the architecture kbuild built for, which its
``.config`` names: ``x86`` on an x86_64 host with no ``ARCH`` set.

A record names the run that made it, which by hand is ``manual``.

.. _kresults: https://github.com/linux-kdevops/kresults
