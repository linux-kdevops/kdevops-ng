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

.. _blktests: https://github.com/linux-blktests/blktests
