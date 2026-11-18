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

:src:`is-system-running <tasks/qemu-system/is-system-running>` asks
the guest's own systemd whether it has booted: it waits for the boot to
end and prints ``running`` where every unit started. It fails while the
guest takes no connection yet, so a :term:`workflow <Workflow>` repeats
it, and where a unit of the guest failed.

:src:`status <tasks/qemu-system/status>` shows the unit, the command it
runs, and the processor time and memory it has taken.
:src:`journal <tasks/qemu-system/journal>` shows the guest's console
since the machine last started.

:src:`kill <tasks/qemu-system/kill>` ends a machine whose guest does not
stop, and clears the failure that leaves its unit in.

:src:`machine <tasks/qemu-system/machine>` describes a machine of a
family, one of many that share their lines: the family is the first
word of the machine's name, and :src:`tasks/qemu-system/files/families`
has, for each, the directory of what its machines share and the file a
machine's own is written from, with a vsock number no other machine
has, the tree whose kernel it boots, and the root of its
distribution's image.

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/qemu-system/machine --machine blktests-nvme-tcp-series \
       --directory ~/linux --distribution debian-14
   $ tasks/qemu-system/remove --machine blktests-nvme-tcp-series

:src:`remove <tasks/qemu-system/remove>` stops a machine and deletes
its file and its state directory: its disk, and what its guest left in
its shares. A family's lines stay.

:src:`tasks/qemu-system/files/machines` has machines to copy and
change: a guest that boots a tree's kernel, the same with an NVMe
namespace, and the same with a card on a segment guests share
(:doc:`/getting-started/guest`).

qemu-system-generator's `usage pages`_ have the rest: freezing a
machine, starting machines at login, and removing one.

.. _qemu-system-generator: https://github.com/linux-kdevops/qemu-system-generator
.. _usage pages: https://github.com/linux-kdevops/qemu-system-generator/tree/main/docs/usage
