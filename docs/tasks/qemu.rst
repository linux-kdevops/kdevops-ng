.. SPDX-License-Identifier: copyleft-next-0.3.1

====
QEMU
====

The :term:`tasks <Task>` download the subprojects of a `QEMU`_
:term:`tree <Tree>`, configure it, build it, name its series and check
its commits. The tree is yours. They change no file it tracks, and
write only in its ``subprojects/`` and ``build/``.

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/qemu/subprojects --directory ~/qemu
   $ tasks/qemu/configure --directory ~/qemu --target-list x86_64-softmmu
   $ tasks/qemu/build --directory ~/qemu
   $ tasks/qemu/series --directory ~/qemu --range HEAD~3..
   $ tasks/qemu/checkpatch --directory ~/qemu --range HEAD~3..

:src:`subprojects <tasks/qemu/subprojects>` has `Meson`_ download the Git
subprojects the tree's wrap files pin. :src:`configure <tasks/qemu/configure>`
runs ``configure`` in ``build/`` for the targets its ``--target-list``
names, with ``--disable-download``: it fetches nothing, and takes Meson
from the host or from the wheel the tree ships. :src:`build
<tasks/qemu/build>` runs :cmd:`make` there, with a job for each processor.
:src:`series <tasks/qemu/series>` names the commits of a range as the
series the tree's records are of (:ref:`records-series`).
:src:`checkpatch <tasks/qemu/checkpatch>` checks each commit of a range
with the tree's checkpatch.pl, a `Perl`_ program, as `submitting-a-patch.rst`_
asks before a submission.

.. _requirements-qemu:

Requirements
============

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install build-essential git meson ninja-build pkgconf \
             python3-venv flex bison libglib2.0-dev libpixman-1-dev

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console
         :class: cmd-host

         $ sudo dnf install gcc make perl git meson ninja-build pkgconf \
             python3 flex bison glib2-devel pixman-devel

   .. tab-item:: Ubuntu
      :sync: ubuntu

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install build-essential git meson ninja-build pkgconf \
             python3-venv flex bison libglib2.0-dev libpixman-1-dev

``configure`` builds a device or a backend only where it finds the
library for it, so what else is installed decides what the emulator has.

The compiler
============

``CC`` and ``CXX`` come from the environment, and the log shows each one
that is set:

.. code-block:: console
   :class: cmd-host

   $ CC=clang tasks/qemu/configure --directory ~/qemu --target-list x86_64-softmmu
   $ systemd-run --user --unit=qemu-configure@… … --setenv=CC=clang … ../configure …

The unit
========

Each task runs its tool in a unit named for the task, as
``qemu-build-12345.service`` (:ref:`tasks-unit`). In the tree the unit
of ``subprojects`` may write ``subprojects/`` only, and the others
``build/`` only. Meson lists
QEMU's block tests as it configures, and they make a scratch directory:
the task sets their ``TEST_DIR``, which keeps it in ``build/``. Your home
is read-only to the unit, so ``configure``'s :cmd:`pip` runs without its
cache: it installs the tree's own package and downloads nothing. The tasks
take make's line and the variables from :src:`tasks/common/qemu`.

.. _Meson: https://mesonbuild.com
.. _Perl: https://www.perl.org
.. _QEMU: https://www.qemu.org
.. _submitting-a-patch.rst: https://www.qemu.org/docs/master/devel/submitting-a-patch.html
