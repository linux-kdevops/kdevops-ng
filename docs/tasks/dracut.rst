.. SPDX-License-Identifier: copyleft-next-0.3.1

======
dracut
======

A guest that boots a :term:`tree <Tree>`'s kernel needs an initrd made
for that kernel: one that loads the root file system's module and
mounts the guest's root, then what the root's ``/etc/fstab`` marks for
the initrd, the build's modules over ``/usr/lib/modules``. One
:term:`task <Task>` makes it with `dracut`_, after
:src:`modules_install <tasks/kernel/modules_install>`:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/kernel/modules_install --directory ~/linux
   $ tasks/dracut/initrd --directory ~/linux

:src:`initrd <tasks/dracut/initrd>` writes ``build/initrd``, built for
any machine and not for this host, with no keyboard or font setup. Make
it again after the modules change.

.. _requirements-dracut:

Requirements
============

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install dracut-core

      .. warning::

         Install ``dracut-core``, which holds the program. The
         ``dracut`` package replaces ``initramfs-tools`` and makes the
         host's own initrd again.

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console
         :class: cmd-host

         $ sudo dnf install dracut

   .. tab-item:: Ubuntu
      :sync: ubuntu

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install dracut-core

      .. warning::

         Install ``dracut-core``, which holds the program. The
         ``dracut`` package replaces ``initramfs-tools`` and makes the
         host's own initrd again.

.. _dracut: https://dracut-ng.github.io/dracut-ng/
