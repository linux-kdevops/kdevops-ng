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

One :term:`task <Task>` runs a group of its tests, or one test, on the
machine it is started on. Start it in the guest, as root: the guest has
your home at its host path, so the checkout and the tree are there
under the names they have on the host:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ ssh guest ~/kdevops-ng/tasks/blktests/check --directory ~/linux --group loop
   $ ssh guest ~/kdevops-ng/tasks/blktests/check --directory ~/linux \
       --group block/001
   block/001 (stress device hotplugging)                        [passed]
       runtime    ...  31.548s

:src:`check <tasks/blktests/check>` runs blktests' ``check`` from
``/usr/lib/blktests`` and exits with its status, which is not zero
where a test failed. How the command reaches the guest is yours, or a
:term:`workflow <Workflow>`'s: the task opens no connection. blktests
writes what it keeps of each test into the tree's ``build/``, which the
guest shares with the host:

.. code-block:: text

   build/blktests/
   └── block/001/            the group or test asked for
       └── nodev/            the device, or nodev for a test that makes its own
           └── block/
               └── 001       status, runtime, description, exit status, date

A test that failed leaves its output beside it, as ``001.out.bad``,
``001.full`` and ``001.dmesg``. A run starts with the directory of what
it was asked for empty.

The guest's unit
================

The guest's own systemd runs a group as well, with no session held
open for it. :src:`tasks/libguestfs/blktests` installs the unit
:src:`blktests@.service <tasks/libguestfs/files/units/blktests@.service>`
with blktests, and its instance is the group, or a test with a dash
for the slash:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ systemctl --host guest start blktests@loop.service
   $ systemctl --host guest start blktests@block-001.service
   $ systemctl --host guest status blktests@loop.service
   $ ssh guest journalctl --unit=blktests@loop.service

``start`` returns when the group is done, and fails where a test
failed. With ``--no-block`` it returns at once, and the group runs on
with the terminal closed. In the guest the lines are the same without
``--host guest``.

The unit takes no tree, so it keeps the results in the guest, laid out
as above:

.. code-block:: text

   /var/lib/blktests/
   └── loop/                 the group or test asked for
       └── nodev/
           └── loop/
               └── 001

.. _blktests: https://github.com/linux-blktests/blktests
