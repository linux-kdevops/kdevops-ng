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

kresults' :cmd:`krecord` writes the record. It needs `Python`_ 3.11 or later,
which each :term:`distribution <Distribution>`'s base system has, and a link
under its name somewhere on your ``PATH``:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ git clone https://github.com/linux-kdevops/kresults.git
   $ ln --symbolic --verbose "$PWD/kresults/format/record.py" \
       ~/.local/bin/krecord

:cmd:`krecord` reads what the tool printed from your journal
(:ref:`requirements-journal`).

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

A QEMU commit has no build below it: ``qemu/<commit>/configure.json`` and
``qemu/<commit>/make/all.json``.

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
prints no warning again, so its record holds none.

A build is filed under the machine the kernel built for, which its
``.config`` names: ``x86_64``, or ``i386`` for a tinyconfig on an x86_64
host.

A record names the :term:`run <Run>` that made it, which by hand is ``manual``.

.. _Git: https://git-scm.com
.. _kresults: https://github.com/linux-kdevops/kresults
.. _Python: https://www.python.org
.. _service manager: https://www.freedesktop.org/software/systemd/man/latest/systemd.html
.. _systemd: https://systemd.io
.. _unit: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
