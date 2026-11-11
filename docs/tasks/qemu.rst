.. SPDX-License-Identifier: copyleft-next-0.3.1

====
QEMU
====

Three :term:`tasks <Task>` download the subprojects of a `QEMU`_
:term:`tree <Tree>`, configure it and build it. The tree is yours. They
change no file it tracks, and write only in its ``subprojects/`` and
``build/``.

.. code-block:: console

   $ tasks/qemu/subprojects --directory ~/qemu
   $ tasks/qemu/configure --directory ~/qemu --target-list x86_64-softmmu
   $ tasks/qemu/build --directory ~/qemu

:src:`subprojects <tasks/qemu/subprojects>` has `Meson`_ download the Git
subprojects the tree's wrap files pin. :src:`configure <tasks/qemu/configure>`
runs ``configure`` in ``build/`` for the targets its ``--target-list``
names, with ``--disable-download``: it fetches nothing, and takes Meson
from the host or from the wheel the tree ships. :src:`build
<tasks/qemu/build>` runs :cmd:`make` there, with a job for each processor.

.. _requirements-qemu:

Requirements
============

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console

         $ sudo apt install build-essential git meson ninja-build pkgconf \
             python3-venv flex bison libglib2.0-dev libpixman-1-dev

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console

         $ sudo dnf install gcc make git meson ninja-build pkgconf python3 \
             flex bison glib2-devel pixman-devel

   .. tab-item:: Ubuntu
      :sync: ubuntu

      .. code-block:: console

         $ sudo apt install build-essential git meson ninja-build pkgconf \
             python3-venv flex bison libglib2.0-dev libpixman-1-dev

``configure`` builds a device or a backend only where it finds the
library for it, so what else is installed decides what the emulator has.

The compiler
============

``CC`` and ``CXX`` come from the environment, and the log shows each one
that is set:

.. code-block:: console

   $ CC=clang tasks/qemu/configure --directory ~/qemu --target-list x86_64-softmmu
   $ systemd-run --user --unit=qemu-configure@… … --setenv=CC=clang … ../configure …

The unit
========

Each task runs its tool in a unit named for the task and the tree:
``qemu-build@home-user-qemu.service`` builds ``/home/user/qemu``
(:ref:`tasks-unit`). In the tree the unit of ``subprojects`` may write
``subprojects/`` only, and the other two ``build/`` only. Meson lists
QEMU's block tests as it configures, and they make a scratch directory:
the task sets their ``TEST_DIR``, which keeps it in ``build/``. Your home
is read-only to the unit, so ``configure``'s :cmd:`pip` runs without its
cache: it installs the tree's own package and downloads nothing. The tasks
take make's line and the variables from :src:`tasks/common/qemu`.

.. _Meson: https://mesonbuild.com
.. _QEMU: https://www.qemu.org
