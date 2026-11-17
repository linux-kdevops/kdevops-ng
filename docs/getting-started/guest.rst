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

The disk
========

Make a key for your guests, then the guest's disk in its state
directory (:doc:`/tasks/libguestfs`):

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ ssh-keygen -t ed25519 -N '' -C guests -f ~/.ssh/guests
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
   $ ssh -i ~/.ssh/guests root@machine/guest uname --kernel-release
   7.4.0-rc2-00003-g0123456789ab
   $ ssh -i ~/.ssh/guests root@machine/guest systemctl is-system-running
   running

:cmd:`ssh` reaches the guest over vsock, by the name of its machine, so
the host opens no port. A guest answers about 12 seconds after its
start. Its console is the unit's log, where ``--all`` shows the lines
that hold the console's control characters, which :cmd:`journalctl`
otherwise prints as blobs:

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

.. _QEMU: https://www.qemu.org
.. _qemu-system-generator: https://github.com/linux-kdevops/qemu-system-generator
.. _virtiofs: https://virtio-fs.gitlab.io
