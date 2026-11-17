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

Make the guest's disk in its state directory, with the public key of
`ssh`_ below (:doc:`/tasks/libguestfs`):

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ mkdir --parents --verbose ~/.local/state/qemu-system/guest
   $ tasks/libguestfs/download_image \
       --directory ~/.local/state/qemu-system/guest --distribution debian-13
   $ tasks/libguestfs/overlay --directory ~/.local/state/qemu-system/guest \
       --backing-file debian-13-genericcloud-amd64.qcow2
   $ tasks/libguestfs/customize --directory ~/.local/state/qemu-system/guest \
       --hostname guest --ssh-inject ~/.ssh/guests.pub

The machine
===========

The machine is a ``.qemu`` file of yours, named for the guest;
qemu-system-generator documents its keys. Its unit runs in the guest's
state directory, so the disk is named by its file alone:

.. code-block:: ini
   :caption: ~/.config/qemu/systemd/guest.qemu

   [VM]
   SSHPrivateKey=%h/.ssh/guests

   [QEMU]
   machine=q35
   nodefaults=
   accel=kvm
   cpu=host
   m=2G
   smp=4
   nographic=
   serial=mon:stdio
   drive=file=work.qcow2,if=virtio,format=qcow2
   kernel=%h/linux/build/arch/x86_64/boot/bzImage
   initrd=%h/linux/build/initrd
   append=console=ttyS0 root=/dev/vda1 rw
   netdev=user,id=net0
   device=virtio-net-pci-non-transitional,netdev=net0
   device=vhost-vsock-pci-non-transitional,guest-cid=100

   [virtiofsd]
   shared-dir=%h/linux/build/mod-install/lib/modules
   tag=modules
   cache=always
   sandbox=namespace
   uid-map=:0:%U:1:
   gid-map=:0:%G:1:

   [virtiofsd]
   shared-dir=%h
   tag=home
   sandbox=namespace
   uid-map=:0:%U:1:
   gid-map=:0:%G:1:

   [Install]
   WantedBy=machines.target

``root=`` names the root partition of the image: the first on Debian
and Ubuntu. The ``user`` network gives the guest an address and a way
out through the host, with no setup on it. ``guest-cid`` is the guest's
vsock address, a number no other machine of the host has. The two
shares carry the tags the initrd and the guest's ``/etc/fstab`` mount.
``SSHPrivateKey=`` lets the unit power the guest off over :cmd:`ssh`
when it stops.

To run the QEMU a tree of yours built, name it:

.. code-block:: diff
   :caption: ~/.config/qemu/systemd/guest.qemu

   --- a/.config/qemu/systemd/guest.qemu
   +++ b/.config/qemu/systemd/guest.qemu
   @@ -1,4 +1,5 @@
    [VM]
   +QEMUBinary=%h/qemu/build/qemu-system-x86_64
    SSHPrivateKey=%h/.ssh/guests

    [QEMU]

Boot
====

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ systemctl --user start qemu-system-generator.service
   $ systemctl --user start qemu-system@guest.service
   $ ssh guest uname --kernel-release
   7.4.0-rc2-00003-g0123456789ab
   $ ssh guest systemctl is-system-running
   running

A guest answers about 12 seconds after its start. Its console is the
unit's log, where ``--all`` shows the lines that hold the console's
control characters, which :cmd:`journalctl` otherwise prints as blobs:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ journalctl --all --user-unit=qemu-system@guest.service

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
   $ systemctl --user restart qemu-system@guest.service

To start the guest over, stop it and make its disk again with
``overlay`` and ``customize``.

Two guests that reach each other
================================

The ``user`` network is each machine's own, so two guests do not see
each other on it. A second card on a segment the machines share joins
them, as an NFS server and its client need. Each machine takes the same
``netdev=`` line and a card with a MAC address of its own, here from its
vsock number:

.. code-block:: diff
   :caption: ~/.config/qemu/systemd/guest-server.qemu

   --- a/.config/qemu/systemd/guest-server.qemu
   +++ b/.config/qemu/systemd/guest-server.qemu
   @@ -15,4 +15,6 @@
    netdev=user,id=net0
    device=virtio-net-pci-non-transitional,netdev=net0
   +netdev=dgram,id=lan,remote.type=inet,remote.host=239.255.0.1,remote.port=5555,local.type=inet,local.host=127.0.0.1,local.port=0
   +device=virtio-net-pci-non-transitional,netdev=lan,mac=52:54:00:00:00:65
    device=vhost-vsock-pci-non-transitional,guest-cid=101

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

Give each guest a name, a state directory, a ``guest-cid`` and a MAC
address of its own.

.. _network page: https://github.com/linux-kdevops/qemu-system-generator/blob/main/docs/bootstrap/network.rst
.. _QEMU: https://www.qemu.org
.. _qemu-system-generator: https://github.com/linux-kdevops/qemu-system-generator
.. _virtiofs: https://virtio-fs.gitlab.io
