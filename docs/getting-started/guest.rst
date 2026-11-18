.. SPDX-License-Identifier: copyleft-next-0.3.1

=======
A guest
=======

A guest boots the kernel a :term:`tree <Tree>` built, on a distribution's
own userspace. `QEMU`_ loads the kernel and its initrd from the tree's
``build/``, the guest's disk is an overlay of the distribution's cloud
image, and the host shares two directories with it over `virtiofs`_: the
build's modules and your home. A rebuild reaches the guest at its next
start, with nothing installed in its disk.

It needs `qemu-system-generator`_ running (:doc:`qemu-system-generator`),
a host with KVM and ``/dev/vhost-vsock``, and what the tasks below
list on their pages.

The kernel
==========

Join the ``guest`` :term:`profile <Profile>` with the one of what you
test, build, and install the modules and the initrd in ``build/``
(:doc:`/tasks/kernel`, :doc:`/tasks/dracut`):

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/kernel/merge_config --directory ~/linux --profile guest+block-layer
   $ tasks/kernel/build --directory ~/linux
   $ tasks/kernel/modules_install --directory ~/linux
   $ tasks/dracut/initrd --directory ~/linux

ssh
===

The guests take one key for root, so make one for them alone:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ ssh-keygen -t ed25519 -N '' -C guests -f ~/.ssh/guests

One file tells :cmd:`ssh` how to reach every guest by its machine's
name, with that key:

.. code-block:: text
   :caption: ~/.ssh/guests.conf

   Host guest guest-*
       ProxyCommand /usr/lib/systemd/systemd-ssh-proxy machine/%n %p
       ProxyUseFdpass yes
       User root
       IdentityFile ~/.ssh/guests
       IdentitiesOnly yes
       CheckHostIP no
       StrictHostKeyChecking no
       UserKnownHostsFile /dev/null

:cmd:`systemd-ssh-proxy` asks your service manager for the machine of
that name and connects to it over vsock, so the host opens no port and
the file names no address. The host keys are not kept: a guest gets new
ones each time its disk is made. Name your guests ``guest`` or
``guest-...``, or add their names to the ``Host`` line. Include the file
from your own configuration:

.. code-block:: diff
   :caption: ~/.ssh/config

   --- a/.ssh/config
   +++ b/.ssh/config
   @@ -1 +1,2 @@
   +Include ~/.ssh/guests.conf
    Host *

The disk
========

Download the distribution's image once, to a directory every guest of
the host makes its disk from, and make the guest's disk in its state
directory, with the public half of that key (:doc:`/tasks/libguestfs`):

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/libguestfs/download_image \
       --directory ~/.local/state/machines --distribution debian-13
   $ mkdir --parents --verbose ~/.local/state/qemu-system/guest
   $ tasks/libguestfs/overlay --directory ~/.local/state/qemu-system/guest \
       --backing-file ~/.local/state/machines/debian-13-genericcloud-amd64.qcow2
   $ tasks/libguestfs/customize --directory ~/.local/state/qemu-system/guest \
       --hostname guest --ssh-inject ~/.ssh/guests.pub

The machine
===========

The machine is a ``.qemu`` file of yours, named for the guest;
qemu-system-generator documents its keys.
:src:`tasks/qemu-system/files/machines` has machines that are ready but
for what only you know. Copy one and change the lines it marks
``CHANGE``: your Linux tree, and a vsock number no other machine of the
host has:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ cp --verbose tasks/qemu-system/files/machines/guest.qemu \
       ~/.config/qemu/systemd/guest.qemu

.. literalinclude:: ../../tasks/qemu-system/files/machines/guest.qemu
   :language: ini
   :caption: ~/.config/qemu/systemd/guest.qemu
   :lines: 6-

The unit runs in the guest's state directory, so the disk is named by
its file alone. ``TERM=dumb`` has the guest write its console as plain
text: the console is the unit's log, and colours and the queries a
terminal answers do not belong in one. The ``user`` network gives the
guest an address and a way out through the host, with no setup on it.
The two shares carry the tags the guest's ``/etc/fstab`` mounts.

``guest.qemu``
   The guest alone.

``guest-nvme.qemu``
   With an NVMe controller and one namespace, for a test of the NVMe
   driver or of the block layer on it. The file says how to make the
   namespace's file.

``guest-blktests.qemu``
   ``guest-nvme.qemu`` with the share blktests keeps its results in
   (:doc:`/tasks/blktests`).

``guest-lan.qemu``
   With a second card on a segment the guests share, for a test two
   guests take part in (`Two guests that reach each other`_).

Boot
====

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ systemctl --user start qemu-system-generator.service
   $ tasks/qemu-system/start --machine guest
   $ ssh guest uname --kernel-release
   7.4.0-rc2-00003-g0123456789ab
   $ systemctl --host guest is-system-running
   running

A guest answers about 12 seconds after its start. :cmd:`systemctl`
``--host`` takes the same name as :cmd:`ssh`, and runs in the guest. Its
console is the unit's log:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/qemu-system/journal --machine guest

:doc:`/tasks/qemu-system` has the tasks that stop, restart and kill a
machine.

After a rebuild
===============

Install the modules and make the initrd again, then start the guest
again:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/kernel/build --directory ~/linux
   $ tasks/kernel/modules_install --directory ~/linux
   $ tasks/dracut/initrd --directory ~/linux
   $ tasks/qemu-system/restart --machine guest

To start the guest over, stop it and make its disk again with
``overlay`` and ``customize``.

Two guests that reach each other
================================

The ``user`` network is each machine's own, so two guests do not see
each other on it. A second card on a segment the machines share joins
them, as an NFS server and its client need.
:src:`guest-lan.qemu <tasks/qemu-system/files/machines/guest-lan.qemu>`
has it. Copy it once for each guest, and give each a name, a state
directory, a vsock number and a MAC address of its own:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ cp --verbose tasks/qemu-system/files/machines/guest-lan.qemu \
       ~/.config/qemu/systemd/guest-server.qemu
   $ cp --verbose tasks/qemu-system/files/machines/guest-lan.qemu \
       ~/.config/qemu/systemd/guest-client.qemu

Every QEMU that names the same multicast group and port is on the
segment, which stays on the host's loopback and needs no root, as
qemu-system-generator's `network page`_ explains. Nothing on it hands
out addresses: each card takes a link-local one, and a guest answers to
its name with ``.local`` after it:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ ssh guest-client ping -c 2 guest-server.local
   2 packets transmitted, 2 received, 0% packet loss, time 1001ms

.. _network page: https://github.com/linux-kdevops/qemu-system-generator/blob/main/docs/bootstrap/network.rst
.. _QEMU: https://www.qemu.org
.. _qemu-system-generator: https://github.com/linux-kdevops/qemu-system-generator
.. _virtiofs: https://virtio-fs.gitlab.io
