.. SPDX-License-Identifier: copyleft-next-0.3.1

===========
qemu-system
===========

`qemu-system-generator`_ makes the unit ``qemu-system@NAME.service`` of
each machine a ``.qemu`` file of yours describes
(:doc:`/getting-started/guest`). These :term:`tasks <Task>` are the
:cmd:`systemctl` and :cmd:`journalctl` lines that run one, by the
machine's name:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/qemu-system/start --machine guest
   $ tasks/qemu-system/status --machine guest
   $ tasks/qemu-system/journal --machine guest
   $ tasks/qemu-system/restart --machine guest
   $ tasks/qemu-system/stop --machine guest
   $ tasks/qemu-system/kill --machine guest

:src:`start <tasks/qemu-system/start>`, :src:`stop <tasks/qemu-system/stop>`
and :src:`restart <tasks/qemu-system/restart>` do what their names say.
A machine that names a key powers its guest off over :cmd:`ssh` when it
stops, and has its power button pressed otherwise. ``restart`` is what a
guest takes a rebuilt kernel with.

:src:`status <tasks/qemu-system/status>` shows the unit, the command it
runs, and the processor time and memory it has taken.
:src:`journal <tasks/qemu-system/journal>` shows the guest's console
since the machine last started.

:src:`kill <tasks/qemu-system/kill>` ends a machine whose guest does not
stop, and clears the failure that leaves its unit in.

:src:`tasks/qemu-system/files/machines` has machines to copy and
change: a guest that boots a tree's kernel, the same with an NVMe
namespace, and the same with a card on a segment guests share
(:doc:`/getting-started/guest`).

qemu-system-generator's `usage pages`_ have the rest: freezing a
machine, starting machines at login, and removing one.

.. _qemu-system-generator: https://github.com/linux-kdevops/qemu-system-generator
.. _usage pages: https://github.com/linux-kdevops/qemu-system-generator/tree/main/docs/usage
