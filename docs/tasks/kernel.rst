.. SPDX-License-Identifier: copyleft-next-0.3.1

======
Kernel
======

Three :term:`tasks <Task>` configure, build and clean a `Linux`_
:term:`tree <Tree>` with :cmd:`make`. The tree is yours. They change no file it
tracks, and write only in its ``build/``.

.. code-block:: console

   $ tasks/kernel/kconfig --directory ~/linux --target tinyconfig
   $ tasks/kernel/build --directory ~/linux
   $ tasks/kernel/mrproper --directory ~/linux

:src:`kconfig <tasks/kernel/kconfig>` makes ``build/.config`` with one of make's
:term:`configuration <Configuration>` targets, such as ``tinyconfig`` or
``defconfig``. :src:`build <tasks/kernel/build>` builds what that ``.config``
says, with a job for each processor. :src:`mrproper <tasks/kernel/mrproper>`
removes what `kbuild`_ made in ``build/``, the ``.config`` with it.

.. _requirements-kernel:

Requirements
============

The tasks run :cmd:`make` with `GCC`_; the second line of each list is for
`Clang`_, under ``LLVM=1`` (:doc:`/getting-started/requirements`):

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console

         $ sudo apt install build-essential bc bison flex libelf-dev libssl-dev
         $ sudo apt install clang lld llvm

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console

         $ sudo dnf install gcc make perl bc bison flex elfutils-libelf-devel \
             openssl-devel
         $ sudo dnf install clang lld llvm

   .. tab-item:: Ubuntu
      :sync: ubuntu

      Clang is in ``universe``:

      .. code-block:: console

         $ sudo apt install build-essential bc bison flex libelf-dev libssl-dev
         $ sudo add-apt-repository universe
         $ sudo apt install clang lld llvm

The build directory
===================

kbuild keeps what it makes in ``build/`` of the tree, its ``O=``, apart
from the sources.

A tree has one build. kbuild can keep several beside one tree, and the
tasks do not: give each build a tree of its own, as :cmd:`git worktree`
adds one. systemd refuses a task a second run on a tree while the first
lasts.

kbuild refuses to build apart from a tree that was built in place, and
the ``mrproper`` task cleans ``build/`` only. Clean such a tree yourself,
with ``make mrproper`` in it: that removes your own ``.config``, which no
task should do for you.

The architecture and the compiler
=================================

``ARCH`` and ``LLVM`` come from the environment, and the log shows each
one that is set:

.. code-block:: console

   $ LLVM=1 tasks/kernel/build --directory ~/linux
   $ systemd-run --user --unit=kernel-build@… … --setenv=LLVM=1 … make O=build --jobs=16

The unit
========

Each task runs :cmd:`make` in a unit named for the task and the tree:
``kernel-build@home-user-linux.service`` builds ``/home/user/linux``
(:ref:`tasks-unit`). In the tree the unit may write ``build/`` only. The
three tasks take make's line and kbuild's variables from
:src:`tasks/common/kbuild`.

.. _Clang: https://clang.llvm.org
.. _GCC: https://gcc.gnu.org
.. _kbuild: https://docs.kernel.org/kbuild/index.html
.. _Linux: https://kernel.org
