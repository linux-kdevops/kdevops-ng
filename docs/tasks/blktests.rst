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
under the build of the kernel the guest ran: its release, and the first
twelve digits of the sha256 of its ``.config``, which the release does
not tell apart:

.. code-block:: text

   ~/.local/state/qemu-system/guest/blktests/
   ├── config                  what blktests' check sources
   └── 7.3.0-c159a85d968d/     the kernel's release and .config
       ├── machine/            the guest's processors and memory, and blktests' commit
       ├── block-003.stdout    what check printed, and block-003.stderr
       └── block/003/          the group or test asked for
           └── nvme0n1/        the device, or nodev for a test that makes its own
               └── block/
                   └── 003     status, runtime, description, exit status, date

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
namespaces as the devices of the tests that need one, which run once
on each and overwrite it. The second has metadata, which a few tests
ask of their device. Change it on the host, with the guest running or
not: the next run reads it. `blktests' own page`_ lists what else it
can set.

.. literalinclude:: ../../tasks/blktests/files/config
   :language: bash
   :caption: ~/.local/state/qemu-system/guest/blktests/config
   :start-at: # The devices

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
``--host guest``. Which groups of a guest failed is one line:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ systemctl --host guest --failed
     UNIT                   LOAD   ACTIVE SUB    DESCRIPTION
   ● blktests@block.service loaded failed failed blktests block
   ● blktests@nvme.service  loaded failed failed blktests nvme

What blktests prints goes to ``loop.stdout`` and ``loop.stderr`` under
the build, on the host as it comes, and not to the guest's journal:
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
with kresults' :cmd:`krecord` ``blktests``:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/blktests/record --directory ~/linux --machine guest

:src:`record <tasks/blktests/record>` takes the results under the
release and the ``.config`` of the tree's build, so the guest has to
have run that build, and the machine has to be running: the record names its
QEMU. Each test gets a record, named for the device it ran on:

.. code-block:: text

   ~/.local/state/krecords/linux/v7.3/blktests/block-layer/guest/x86_64/gcc/
   └── blktests/
       ├── nodev/loop/001.json
       └── nvme0n1/block/003.json

The record names the machine under test and the commit of blktests,
from ``machine/`` of the results, and the QEMU the machine runs. It
links the commit where a remote of your blktests tree with an
``https`` address has it. A test
that did not run is a skip, with the reason blktests printed. A group
that did not run is one skip, ``nvme0n1/block.json``. A test that runs
once for each condition has a record for each, in the directory
blktests names for it: ``nvme0n1_tr_loop/nvme/035.json``. Run the task
again after another group: what is filed already is left as it is.

Several guests at once
======================

A group runs in one guest, and a host has room for more than one: each
group gets a guest of its own, on the series' kernel and on the base's,
and they run side by side. A machine is named for the suite, the group
and the kernel, with a name of the series after it where two are
tested at once:

.. code-block:: text

   blktests-block-series        blktests-block-base
   blktests-nvme-tcp-series     blktests-nvme-tcp-base
   blktests-nvme-rdma-series    blktests-nvme-rdma-base

The nvme group is the long one, and splits by transport: the config
sets ``NVMET_TRTYPES`` to the transport in the machine's name, so the
machines share one file, and a machine named for none runs all four.

The machines are a family, as qemu-system-generator reads one.
``blktests-.qemu.d`` of ``~/.config/qemu/systemd`` holds what every
machine named ``blktests-*`` has, from two places of
:src:`tasks/qemu-system/files/families`: the share of blktests' results,
in ``blktests/blktests-.qemu.d/05-share.conf``, and ``10-machine.conf``,
the lines every suite's machines share. A machine's own file is written
from ``template.qemu`` there, with its vsock number and its kernel.
The namespaces are sparse files the machine makes empty at each start,
so they take no room until a test writes.

No machine downloads or installs anything. Three
:term:`workflows <Workflow>` of the Bash :term:`engine <Engine>` do
the work, and none needs a file changed by hand. The first makes one
disk of a distribution's image, with the packages and blktests from
your tree in it, which no machine starts:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ engines/bash/blktests-disk --distribution debian-14 --copy-in ~/blktests

It downloads the image to ``~/.local/state/machines`` where none is
there, and runs ``overlay``, ``customize``, ``install`` and
``blktests`` of :doc:`libguestfs` in ``blktests-debian-14`` beside it.
The second makes a machine from its name, its tree and its
distribution, with a disk that is an overlay of that one:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ engines/bash/blktests-machine --machine blktests-nvme-tcp-series \
       --directory ~/linux --distribution debian-14
   $ engines/bash/blktests-machine --machine blktests-nvme-tcp-base \
       --directory ~/linux-base --distribution debian-14

It runs four tasks. :src:`machine <tasks/qemu-system/machine>` of
:doc:`qemu-system` writes the machine's file, with a vsock number no
other machine has and the root of its distribution's image, and copies
the family's directory to ``~/.config/qemu/systemd`` where it is not
there yet. :src:`tasks/blktests/config` puts blktests' config in the
machine's share. ``overlay`` and ``customize`` make the disk, under the
machine's name.

The family's file runs as it is, and what a series asks of its
machines is added beside it. With ``--qemu`` the workflow has a machine
run the QEMU a tree of yours built, through
:src:`qemu <tasks/qemu-system/qemu>` of :doc:`qemu-system`. With
``--drop-in`` the machine takes the lines of a file, through
:src:`drop-in <tasks/qemu-system/drop-in>`: the options a series tests
on a namespace, which the file sets by the device's id, ``ns0`` or
``ns1``. :src:`tasks/qemu-system/files/drop-ins` has
those kept here:

.. literalinclude:: ../../tasks/qemu-system/files/drop-ins/20-nvme-mam.conf
   :language: ini
   :caption: 20-nvme-mam.conf
   :start-at: [QEMU]

:src:`remove <tasks/qemu-system/remove>` takes a machine away again,
with its disk and what its guest left. A workflow takes away all that
these made: every machine of the family, the family's lines, and with
``--distribution`` the disk the machines were overlays of. The images
and the records stay:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ engines/bash/blktests-remove --distribution debian-14

The third runs a machine's group and files its records. It
starts the machine, waits for the guest to boot, runs the group the
machine is named for, and records what it left, whether the group
passed or not:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ engines/bash/blktests --machine blktests-nvme-tcp-series \
       --directory ~/linux

It returns when the group is done, with the group's verdict.
:doc:`/engines/bash` has how to run several side by side, each as a
unit of your service manager.

The workflow's tasks run alone as well:
:src:`tasks/blktests/start` runs a group in a machine's guest from the
host, and :src:`is-active <tasks/qemu-system/is-active>`
of :doc:`qemu-system` says whether a guest has booted. Both reach the
guest as ``systemctl --host`` does.

Size the machines to the host: each takes the processors and memory the
family's file names, and more guests than the host has processors make
the tests that measure time fail. ``systemctl --user stop
machines.target`` stops them all.

The base
========

A series' tests are set against the same tests on its base, so the base
needs them too: a second guest that boots the base's kernel, built with
the same profiles. Make it as the first was made, with a state
directory, a disk with blktests, a share with its config and a vsock
number of its own, and name the base's tree in its machine's file. Give
it the QEMU and the devices of the first, so that the kernel is all
that differs. Then run the same groups and file them with the base's
tree:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ systemctl --host guest-base start blktests@loop.service
   $ tasks/blktests/record --directory ~/linux-base --machine guest-base

The series' page then says of each test how it went on both:
``passes on both``, or what the series changed.

A test that differs
===================

One run of a test is one sample. A test that failed on the series and
passed on its base may fail on either the next time: run that test
alone again, on both kernels, before the difference is believed. The
machines are up, so each run takes the test's own seconds, and its
record joins the earlier ones:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ engines/bash/blktests --machine blktests-nvme-tcp-series \
       --directory ~/linux --group nvme/039
   $ engines/bash/blktests --machine blktests-nvme-tcp-base \
       --directory ~/linux-base --group nvme/039

``--group`` takes one test as it takes a group. The page shows the
last run of each side, and every run under it: a test that passes and
fails on the same kernel is unstable there, whatever the last run of
the two says.

.. _blktests: https://github.com/linux-blktests/blktests
.. _blktests' own page: https://github.com/linux-blktests/blktests/blob/master/Documentation/running-tests.md
