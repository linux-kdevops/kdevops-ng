.. SPDX-License-Identifier: copyleft-next-0.3.1

======
Kernel
======

The :term:`tasks <Task>` configure, build and clean a `Linux`_
:term:`tree <Tree>` with :cmd:`make`. The tree is yours. They change no file it
tracks, and write only in its ``build/``.

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/kernel/kconfig --directory ~/linux --target tinyconfig
   $ tasks/kernel/build --directory ~/linux
   $ tasks/kernel/mrproper --directory ~/linux
   $ tasks/kernel/series --directory ~/linux --range v7.3..

:src:`kconfig <tasks/kernel/kconfig>` makes ``build/.config`` with one of make's
:term:`configuration <Configuration>` targets, such as ``tinyconfig`` or
``defconfig``. :src:`build <tasks/kernel/build>` builds what that ``.config``
says, with a job for each processor. :src:`mrproper <tasks/kernel/mrproper>`
removes what `kbuild`_ made in ``build/``, the ``.config`` with it.
:src:`series <tasks/kernel/series>` names the commits of a range as the
series the tree's records are of (:ref:`records-series`).

.. _kernel-configuration:

The configuration
=================

:src:`merge_config <tasks/kernel/merge_config>` makes ``build/.config``
from the `kfragments`_ fragments that the profiles ``--profile`` names
list, with the tree's ``merge_config.sh``. It names them through
``build/kfragments``, a link to the vendored copy, so the command and
what it prints hold no path of your host. The profile names stay in
``build/.config.name`` and the fragments merged in
``build/.config.fragments``, which name the build's configuration and
the command for its :term:`record <Record>`:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/kernel/merge_config --directory ~/linux --profile xfs-filesystem
   $ tasks/kernel/merge_config --directory ~/linux \
       --profile block-layer+nvm-express-driver

A profile is a file under :src:`tasks/kernel/files/profiles`, named
after the MAINTAINERS entry whose files it configures, ``block-layer``
for BLOCK LAYER, and its second line names the entry. ``fstests`` names
none: it configures the guest `fstests`_ runs in, and goes with a
filesystem's profile. The fragments come from the vendored kfragments
copy (:doc:`/contributing/vendor`).

Names joined by ``+`` merge each named profile's fragments, each once,
in the order :src:`tasks/kernel/files/fragments` gives them: the base
first, and a built-in override after the fragment it overrides. A later
value wins, ``=m`` over an earlier ``=y`` included. The catalog holds
every fragment the vendored kfragments has, so a profile may list any of
them. ``${ARCH}`` in a
fragment's name stands for the architecture: ``ARCH`` from the
environment, else the host's machine as kfragments names it, ``arm64``
or ``riscv``.

``merge_config.sh`` reports, for each fragment, the values it redefines
and each requested value the ``.config`` lost, an option whose
dependencies nothing met. It prints both on its standard output, so the
journal has them and the record does not (:doc:`/records`):

.. code-block:: console
   :class: cmd-host

   $ journalctl --user --identifier kernel-merge_config@home-user-linux.service

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
         :class: cmd-host

         $ sudo apt install build-essential bc bison flex libelf-dev libssl-dev
         $ sudo apt install clang lld llvm

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console
         :class: cmd-host

         $ sudo dnf install gcc make perl bc bison flex elfutils-libelf-devel \
             openssl-devel
         $ sudo dnf install clang lld llvm

   .. tab-item:: Ubuntu
      :sync: ubuntu

      Clang is in ``universe``:

      .. code-block:: console
         :class: cmd-host

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
   :class: cmd-host

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
.. _fstests: https://git.kernel.org/pub/scm/fs/xfs/xfstests-dev.git
.. _GCC: https://gcc.gnu.org
.. _kbuild: https://docs.kernel.org/kbuild/index.html
.. _kfragments: https://github.com/linux-kdevops/kfragments
.. _Linux: https://kernel.org
