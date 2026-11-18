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

:src:`is-active <tasks/qemu-system/is-active>` asks the guest's own
systemd whether it has booted, by the target it boots to. It fails
while the guest takes no connection yet, so a
:term:`workflow <Workflow>` repeats it. A unit of the guest that
failed does not fail it: a suite's tests leave such units, as
nvme-cli's connection unit after a test of a fabric.

:src:`status <tasks/qemu-system/status>` shows the unit, the command it
runs, and the processor time and memory it has taken.
:src:`journal <tasks/qemu-system/journal>` shows the guest's console
since the machine last started.

:src:`kill <tasks/qemu-system/kill>` ends a machine whose guest does not
stop, and clears the failure that leaves its unit in.

:src:`machine <tasks/qemu-system/machine>` describes a machine of a
family, one of many that share their lines: the family is the first
word of the machine's name. :src:`tasks/qemu-system/files/families`
has the lines every family's machines share, ``10-machine.conf``, the
file a machine's own is written from, ``template.qemu``, with a vsock
number no other machine has, the tree whose kernel it boots, and the
root of its distribution's image, and for each family a directory with
what its machines have beside the others': the share of its suite. The
task copies the family's lines to ``~/.config/qemu/systemd`` once.

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/qemu-system/machine --machine blktests-nvme-tcp-series \
       --directory ~/linux --distribution debian-14
   $ tasks/qemu-system/remove --machine blktests-nvme-tcp-series

:src:`qemu <tasks/qemu-system/qemu>` has a machine run the QEMU a tree
of yours built, ``tasks/qemu-system/qemu --machine NAME --directory
~/qemu``: it writes a file of the machine's own that names the binary
in the tree's ``build/``.

:src:`drop-in <tasks/qemu-system/drop-in>` gives a machine the lines
of a file beside its own, a copy in the machine's ``.qemu.d``
directory: a property of one of its devices, as ``set=`` lines.

:src:`remove <tasks/qemu-system/remove>` stops a machine and deletes
its file and its state directory: its disk, and what its guest left in
its shares. A family's lines stay, since its other machines read them;
:src:`remove-family <tasks/qemu-system/remove-family>` deletes those
once the machines are gone.

:src:`tasks/qemu-system/files/machines` has machines to copy and
change: a guest that boots a tree's kernel, the same with an NVMe
namespace, and the same with a card on a segment guests share
(:doc:`/getting-started/guest`).

qemu-system-generator's `usage pages`_ have the rest: freezing a
machine, starting machines at login, and removing one.

.. _qemu-system-generator: https://github.com/linux-kdevops/qemu-system-generator
.. _usage pages: https://github.com/linux-kdevops/qemu-system-generator/tree/main/docs/usage
