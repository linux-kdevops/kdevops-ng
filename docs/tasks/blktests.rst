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

The config and the results
==========================

blktests reads its config from ``/var/lib/blktests`` of the guest and
keeps what it writes of each test there. The directory is a share of
the host: ``blktests/`` of the guest's state directory, under the tag
``blktests``. Both are of the guest, so they lie with it, the results
under the release of the kernel the guest ran:

.. code-block:: text

   ~/.local/state/qemu-system/guest/blktests/
   ├── config                           what blktests' check sources
   └── 7.3.0-rc5-00135-gc8c68c8ed043/   the kernel's release
       ├── machine/                     the guest's processors and memory, and blktests' commit
       ├── block-003.stdout             what check printed, and block-003.stderr
       └── block/003/                   the group or test asked for
           └── nvme0n1/                 the device, or nodev for a test that makes its own
               └── block/
                   └── 003              status, runtime, description, exit status, date

A test that failed leaves its output beside it, as ``003.out.bad``,
``003.full`` and ``003.dmesg``. A run starts with the directory of what
it was asked for empty.

The machine's file names the share, as
:src:`tasks/qemu-system/files/machines/guest-blktests.qemu` does, and
the directory is there, with the config, before the machine starts:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ mkdir --verbose ~/.local/state/qemu-system/guest/blktests
   $ cp --verbose tasks/blktests/files/config \
       ~/.local/state/qemu-system/guest/blktests/

.. literalinclude:: ../../tasks/qemu-system/files/machines/guest-blktests.qemu
   :language: ini
   :caption: ~/.config/qemu/systemd/guest.qemu
   :start-at: # CHANGE: the machine's name. virtiofsd
   :end-at: gid-map

:src:`config <tasks/blktests/files/config>` names the machine's NVMe
namespace as the device of the tests that need one, which overwrite
it. Change it on the host, with the guest running or not: the next run
reads it. `blktests' own page`_ lists what else it can set.

.. literalinclude:: ../../tasks/blktests/files/config
   :language: bash
   :caption: ~/.local/state/qemu-system/guest/blktests/config
   :start-at: # CHANGE

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
   $ tail --follow \
       ~/.local/state/qemu-system/guest/blktests/*/loop.stdout

``start`` returns when the group is done, and fails where a test
failed. With ``--no-block`` it returns at once, the group runs on with
the terminal closed, and ``is-active`` says how it stands:
``activating`` while it runs, ``inactive`` once it has passed,
``failed`` otherwise. In the guest the lines are the same without
``--host guest``.

What blktests prints goes to ``loop.stdout`` and ``loop.stderr`` under
the release, on the host as it comes, and not to the guest's journal:
it is where blktests says why a test did not run, and a
:term:`record <Record>` reads it there.

The task
========

One :term:`task <Task>` does the same on the machine it is started on,
with blktests' lines on your terminal as well as in the file. Start it
in the guest, as root: the guest has your home at its host path, so
the checkout is there under the name it has on the host:

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

The records
===========

A :term:`record <Record>` of a test lies under the build of the kernel
it ran on, so a series' tests are set against its base's as its build
is (:doc:`/records`). One task on the host files what the guest left,
with kresults' :cmd:`kblktests`:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/blktests/record --directory ~/linux --machine guest

:src:`record <tasks/blktests/record>` takes the results under the
release of the kernel the tree built, so the guest has to have run
that build, and the machine has to be running: the record names its
QEMU. Each test gets a record, named for the device it ran on:

.. code-block:: text

   ~/.local/state/krecords/linux/v7.3/blktests/block-layer/guest/x86_64/gcc/
   └── blktests/
       ├── nodev/loop/001.json
       └── nvme0n1/block/003.json

The record names the machine under test and the commit of blktests,
from ``machine/`` of the results, and the QEMU the machine runs. A test
that did not run is a skip, with the reason blktests printed. Run the
task again after another group: what is filed already is left as it
is.

.. _blktests: https://github.com/linux-blktests/blktests
.. _blktests' own page: https://github.com/linux-blktests/blktests/blob/master/Documentation/running-tests.md
