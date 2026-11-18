.. SPDX-License-Identifier: copyleft-next-0.3.1

====
Bash
====

The first :term:`engine <Engine>` is `Bash`_, which every
:term:`host <Host>` that runs the :term:`tasks <Task>` has. A
:term:`workflow <Workflow>` of it is a script under
:src:`engines/bash` that calls tasks, one after another, with a loop, a
default or a status kept for the end where the work asks for one.
``--help`` prints what it takes:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ engines/bash/blktests --help
   Usage: engines/bash/blktests --machine NAME --directory DIR [--group GROUP]

An :term:`option <Option>` in brackets has a default the text names,
and the others say what the workflow works on. Its log names each task
as it starts, after a ``+``, and each task then logs its own commands
after a ``$``, as it does when it runs alone.

The workflows
=============

:src:`blktests-disk <engines/bash/blktests-disk>`
   Makes the disk the machines of :doc:`/tasks/blktests` and
   :doc:`/tasks/fio` are overlays of, from a distribution's image, with
   fio in it as well when asked.

:src:`blktests-machine <engines/bash/blktests-machine>`
   Makes one machine from its name, the tree whose kernel it boots and
   its distribution. The first word of the name is the family, so it
   makes a ``fio-*`` machine as well.

:src:`blktests <engines/bash/blktests>`
   Starts a machine, waits for its guest to boot, runs the group the
   machine is named for, and files the records.

:src:`fio <engines/bash/fio>`
   Starts a machine, waits for its guest to boot, and runs a job of
   :doc:`/tasks/fio` a number of times, filing a record after each.

:src:`series <engines/bash/series>`
   Takes a series from its Message-ID to records: applies it, checks it,
   builds it and its base, and runs blktests groups on both
   (:ref:`bash-series`).

:src:`blktests-remove <engines/bash/blktests-remove>`
   Removes the machines of blktests, and the disk when asked.

Run one
=======

A workflow runs in the terminal and returns when its last task has,
with the status the work gave it. ``blktests`` returns the group's
verdict, after it has filed the records:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ engines/bash/blktests --machine blktests-block-series \
       --directory ~/linux

Run several side by side
========================

A workflow that takes an hour holds its terminal for an hour, and four
of them hold four. Your service manager runs each as a unit instead:
:cmd:`systemd-run` returns at once, the workflow runs on with the
terminal closed, and the journal keeps its lines. The unit gets none of
your shell's environment, so ``--setenv=PATH`` hands it the ``PATH``
your tools are found on:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ for group in block nvme; do
       systemd-run --user --setenv=PATH --unit=blktests-$group-series \
           engines/bash/blktests --machine blktests-$group-series \
           --directory ~/linux
       systemd-run --user --setenv=PATH --unit=blktests-$group-base \
           engines/bash/blktests --machine blktests-$group-base \
           --directory ~/linux-base
     done

Each unit is named for the machine its workflow runs, and the lines
that follow one are your service manager's own:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ systemctl --user list-units 'blktests-*'
   $ systemctl --user status blktests-nvme-series
   $ journalctl --user --follow --unit=blktests-nvme-series
   $ systemctl --user stop blktests-nvme-series

A unit whose workflow passed is gone from the list when it ends. One
whose workflow failed stays there as ``failed``, with its lines, until
it is cleared, and a second run under the same name needs that first:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ systemctl --user reset-failed 'blktests-*'

How many run at once is yours to choose. Nothing here counts the
host's processors: each machine takes what its family's file gives it,
and more guests than the host has processors make tests that measure
time fail.

.. _bash-series:

Test a series
=============

``series`` takes the Message-ID of a series posted on a list and the
tree to work from, and a profile for the kernel to build:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ engines/bash/series \
       --message-id 20260101-topic-v1-0-0123456789ab@example.org \
       --directory ~/linux --profile guest+blktests+nvm-express-driver \
       --groups "nvme-tcp nvme-loop"

Give the Message-ID of the series' latest revision: b4 applies the latest
one, and the thread of an older Message-ID names another base. In order,
it:

#. adds two worktrees of ``--directory`` under
   ``~/.local/state/kdevops-ng/series/ID/``, ``series`` and ``base``,
   with the characters of the Message-ID a path should not hold
   replaced by ``_``, and applies the series in the first
   (:doc:`/tasks/git`, :doc:`/tasks/b4`);
#. reads the commit the cover letter names as ``base-commit``, adds
   ``base`` there and names the commits since it as the series
   (:ref:`records-series`). A series that names no base stops the
   workflow here;
#. runs checkpatch on the series, then makes the configuration of
   ``--profile``, builds, installs the modules and makes the initrd of
   each worktree, one after the other;
#. lists the object files the series changes and checks each with sparse
   and smatch, in both worktrees (:doc:`/tasks/kernel`);
#. makes one machine of the :doc:`blktests </tasks/blktests>` family for
   each word of ``--groups`` and each worktree, and runs them all at
   once.

A failed check, a failed group or an object that fails to check does not
stop the rest, and the workflow's status is 1 if any did. A failed build
stops it. Every machine's records are filed whether its group passed or
not. The lines of each machine, from ``engines/bash/blktests``, go to
``~/.local/state/kdevops-ng/series/ID/logs/NAME.log``, and the workflow's
log names each file.

``--groups`` is how you bound the load. Each word is a group of blktests
(``nvme-tcp``, ``nvme-loop``, ``block``, ``loop``) and the workflow runs
two machines for each, one on each kernel, so four words are eight
guests, each with the processors its family's file gives it. Nothing
counts the host's. Without ``--groups`` no machine runs, and the series is
applied, built and checked only. ``--distribution`` is ``debian-14``
without it, and ``--qemu`` and ``--drop-in`` are those of
``engines/bash/blktests-machine``.

The machines are named without the series, so run one series at a time:
a second run reuses the machines and resets them. Run again for the same
Message-ID, the workflow keeps the worktrees, applies the series again
and builds what changed. It runs for hours, so start it as a unit and
follow it in the journal:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ systemd-run --user --setenv=PATH --unit=series \
       engines/bash/series \
       --message-id 20260101-topic-v1-0-0123456789ab@example.org \
       --directory ~/linux --profile guest+blktests+nvm-express-driver \
       --groups "nvme-tcp nvme-loop"
   $ journalctl --user --follow --unit=series

.. _Bash: https://www.gnu.org/software/bash/
