.. SPDX-License-Identifier: copyleft-next-0.3.1

========
blktests
========

`blktests`_ tests the block layer and its drivers. It runs in a guest
that boots the kernel under test (:doc:`/getting-started/guest`), built
with the ``blktests`` :term:`profile <Profile>` and with blktests in
its disk:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/kernel/merge_config --directory ~/linux \
       --profile guest+blktests+block-layer
   $ tasks/libguestfs/install --directory ~/.local/state/qemu-system/guest \
       --distribution debian-13 --profile blktests
   $ tasks/libguestfs/blktests --directory ~/.local/state/qemu-system/guest \
       --copy-in ~/blktests

The results
===========

blktests keeps what it writes of each test in ``/var/lib/blktests`` of
the guest, which is a share of the host: ``blktests/`` of the guest's
state directory, under the tag ``blktests``. The results are of the
guest and of the kernel it ran, so they lie with the guest, under that
kernel's release:

.. code-block:: text

   ~/.local/state/qemu-system/guest/blktests/
   └── 7.3.0-rc5-00135-gc8c68c8ed043/   the kernel's release
       └── block/001/                   the group or test asked for
           └── nodev/                   the device, or nodev for a test that makes its own
               └── block/
                   └── 001              status, runtime, description, exit status, date

A test that failed leaves its output beside it, as ``001.out.bad``,
``001.full`` and ``001.dmesg``. A run starts with the directory of what
it was asked for empty.

The machine's file names the share, as
:src:`tasks/qemu-system/files/machines/guest-blktests.qemu` does, and
the directory is there before the machine starts:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ mkdir --verbose ~/.local/state/qemu-system/guest/blktests

.. literalinclude:: ../../tasks/qemu-system/files/machines/guest-blktests.qemu
   :language: ini
   :caption: ~/.config/qemu/systemd/guest.qemu
   :start-at: # CHANGE: the machine's name. virtiofsd
   :end-at: gid-map

Nothing mounts the share as the guest boots. The unit and the task
below each mount it first, and on a machine without it they fail
before a test runs.

The guest's unit
================

:src:`tasks/libguestfs/blktests` installs the unit
:src:`blktests@.service <tasks/libguestfs/files/units/blktests@.service>`
with blktests. Its instance is the group, or a test with a dash for
the slash:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ systemctl --host guest start blktests@loop.service
   $ systemctl --host guest start blktests@block-001.service
   $ systemctl --host guest status blktests@loop.service
   $ ssh guest journalctl --unit=blktests@loop.service

``start`` returns when the group is done, and fails where a test
failed. With ``--no-block`` it returns at once, the group runs on with
the terminal closed, and ``is-active`` says how it stands:
``activating`` while it runs, ``inactive`` once it has passed,
``failed`` otherwise. In the guest the lines are the same without
``--host guest``.

The task
========

One :term:`task <Task>` does the same on the machine it is started on,
with blktests' lines on your terminal. Start it in the guest, as root:
the guest has your home at its host path, so the checkout is there
under the name it has on the host:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ ssh guest ~/kdevops-ng/tasks/blktests/check --group loop
   $ ssh guest ~/kdevops-ng/tasks/blktests/check --group block/001
   block/001 (stress device hotplugging)                        [passed]
       runtime    ...  31.548s

:src:`check <tasks/blktests/check>` runs blktests' ``check`` from
``/usr/lib/blktests`` and exits with its status, which is not zero
where a test failed. How the command reaches the guest is yours, or a
:term:`workflow <Workflow>`'s: the task opens no connection.

.. _blktests: https://github.com/linux-blktests/blktests
