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
   Makes the disk the machines of :doc:`/tasks/blktests` are overlays
   of, from a distribution's image.

:src:`blktests-machine <engines/bash/blktests-machine>`
   Makes one machine from its name, the tree whose kernel it boots and
   its distribution.

:src:`blktests <engines/bash/blktests>`
   Starts a machine, waits for its guest to boot, runs the group the
   machine is named for, and files the records.

:src:`blktests-remove <engines/bash/blktests-remove>`
   Removes the machines, and the disk when asked.

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

.. _Bash: https://www.gnu.org/software/bash/
