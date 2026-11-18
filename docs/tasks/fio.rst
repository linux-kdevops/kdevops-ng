.. SPDX-License-Identifier: copyleft-next-0.3.1

===
fio
===

`fio`_ runs a job against a device and reports what it measured. It runs
in a guest that boots the kernel under test
(:doc:`/getting-started/guest`), with fio in its disk. The disk is the
one blktests runs from, with fio beside it, so a guest runs either:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/libguestfs/install --directory ~/.local/state/qemu-system/guest \
       --distribution debian-14 --profile fio
   $ tasks/libguestfs/fio --directory ~/.local/state/qemu-system/guest \
       --copy-in ~/fio

:src:`tasks/libguestfs/fio` builds fio from your tree in the disk, so
the guest runs the commit you have checked out. It configures with
``--prefix=/usr/lib/fio``: fio gets one directory under ``/usr/lib``,
where `UAPI.9`_ keeps what is a package's alone, with ``bin/fio`` in it,
as blktests has ``/usr/lib/blktests``. ``--disable-native`` keeps
configure from tuning the build to the processor of
:cmd:`virt-customize`'s appliance, which is not the guest's. The task
writes the commit as ``/usr/lib/fio/version`` and the address of it on
the first remote of the tree that has the commit and an ``https``
address as ``/usr/lib/fio/url``, for a record to name. The ``fio``
profile holds what fio builds with: a compiler, :cmd:`make`, libaio,
liburing and zlib (:doc:`libguestfs`).

The jobs
========

A job is a file of :src:`tasks/fio/files/jobs`, and every guest gets all
of them, in ``/usr/lib/fio/jobs``: a guest is not made for a job. Each
file says in its first lines what it shows.

``atomic-merge``
   Four sequential atomic writes of 16k, submitted in one batch with
   ``io_uring``, which the block layer can merge into fewer requests
   for the device.

``atomic-verify``
   Ten jobs write random 4k blocks of one range with atomic writes and
   check each block's crc64 as they read it back: a torn write fails
   the check. It is `fio's example`_, sized for a namespace of 1 GiB.

The device is not in a job file. Each names ``filename=${DEVICE}``, which
fio expands from its environment, and the unit gives it ``DEVICE`` from
the machine's config below.

The config and the results
==========================

The guest reads its config from ``/var/lib/fio`` and keeps what fio
prints there. The directory is a share of the host, ``fio/`` of the
machine's state directory, under the tag ``fio``, and the results lie
under the build of the kernel the guest ran, named as blktests'
(:doc:`blktests`): its release, and the first twelve digits of the
sha256 of its ``.config``:

.. code-block:: text

   ~/.local/state/qemu-system/fio-atomic-series/fio/
   ├── config                  the device the jobs run on
   └── 7.3.0-c159a85d968d/     the kernel's release and .config
       ├── machine/            the guest's processors and memory, and fio's commit
       └── atomic-merge/       the job
           ├── fio.json        what fio printed
           └── stderr

:src:`tasks/fio/files/config` is in the form systemd's
``EnvironmentFile=`` reads. It names the first NVMe namespace of the
machine, which a job writes to and overwrites. Change it on the host,
with the guest running or not: the next start reads it. A diff of the
file to run on the second namespace, which has metadata:

.. code-block:: diff
   :caption: ~/.local/state/qemu-system/fio-atomic-series/fio/config

   --- a/config
   +++ b/config
   @@ -4,4 +4,4 @@
    # reads. fio@.service gives it to fio, whose job files name it
    # ${DEVICE}. tasks/fio/config puts this file in the machine's share.
    # A job writes to the device and overwrites what it holds.
   -DEVICE=/dev/nvme0n1
   +DEVICE=/dev/nvme0n2

:src:`tasks/fio/config` puts the file in the machine's share before the
machine starts, and leaves one that is there as it is:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/fio/config --machine fio-atomic-series

Nothing mounts the share as the guest boots. The unit below asks for
it, and on a machine without the share it fails before fio starts.

The guest's unit
================

:src:`tasks/libguestfs/fio` installs the unit
:src:`fio@.service <tasks/libguestfs/files/units/fio@.service>` with
fio. Its instance is the job, and a start runs it once:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ systemctl --host guest start fio@atomic-merge.service
   $ systemctl --host guest status fio@atomic-merge.service

``start`` returns when the job is done, and fails where fio exits with an
error, as a verify does that found a torn block. In the guest the lines
are the same without ``--host guest``. fio prints one JSON document,
``--output-format=json``, which goes to ``fio.json`` under the build, and
its warnings and errors to ``stderr`` there, on the host as they come
and not in the guest's journal, which drops lines of a unit that prints
fast.

A start is one sample. It empties the job's directory first, so each
start replaces the files of the one before: the host records a sample
after the run, and one is as good as the last. Two more units do what
the first cannot, since systemd opens a unit's output files before it
runs a command of that unit: ``fio-job@.service`` makes the job's
directory, and ``suite-machine@fio.service``, from the template
blktests uses as ``suite-machine@blktests.service``, makes the
directory of the build and keeps ``machine/`` in it. The mount of the
share is
:src:`var-lib-fio.mount <tasks/libguestfs/files/units/var-lib-fio.mount>`.

The tasks
=========

:src:`tasks/fio/start` starts the unit from the host, with
``systemctl --host``, and returns with its verdict:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/fio/start --machine fio-atomic-series --job atomic-merge

There is no task that runs the job inside the guest, as
:src:`tasks/blktests/check` runs a group: the unit holds the one
command, and ``systemctl start`` in the guest is how a developer runs it
there.

The record
==========

:src:`tasks/fio/record` files the sample that the job left, as a
:term:`record <Record>` of the build the guest ran, with kresults'
:cmd:`krecord` ``sample``. The machine has to be running, since the
record names its QEMU:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/fio/record --directory ~/linux --machine fio-atomic-series \
       --job atomic-merge

The task reads ``fio.json`` with :cmd:`jq`, and writes a ``metrics``
file in ``build/logs/fio-record/`` of the tree: a line for each of these,
tab-separated, with the unit and which way is better:

.. code-block:: text

   iops            34133.333333    1/s     higher
   bw              559240533       B/s     higher
   clat_mean       27320.806641    ns      lower
   clat_p99        38144           ns      lower
   write_ios       257             count   lower
   write_merges    0               count   higher

``iops``, ``bw`` and the two latencies are fio's, of the job's write
direction: the completion latency's mean and its 99th percentile.
``write_ios`` and ``write_merges`` are of the device in fio's
``disk_util``: the writes the device completed and the ones the block
layer merged, so ``atomic-merge`` shows a change in merging as a change
in these two. A job file that starts several jobs sets
``group_reporting``, so fio gives them one entry and the task reads the
first.

The record's exit status is the greatest ``error`` of the jobs in the
JSON, its start is the job's own, and its length runs to the time fio
wrote the document. A pass means the job ran to the end, and says
nothing of the numbers: they are what a record sets against the same
job on another build.

Several samples
===============

One sample is one run of a job, and a number that varies needs several.
Three workflows of the Bash :term:`engine <Engine>` do the work, and
none needs a file changed by hand (:doc:`/engines/bash`). The first
makes the disk of a distribution with fio from your tree in it beside
blktests, which no machine starts. The second makes the machine, from
its name, whose first word picks the family:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ engines/bash/blktests-disk --distribution debian-14 \
       --copy-in ~/blktests --fio ~/fio
   $ engines/bash/blktests-machine --machine fio-atomic-series \
       --directory ~/linux --distribution debian-14

The machines of the family are
:src:`fio-* <tasks/qemu-system/files/families/fio>`: the lines every
suite's machines share
(:doc:`/tasks/qemu-system`), and the share of fio's results. The third
starts the machine, waits for the guest to boot, and runs the job and
records it, three times unless ``--samples`` says another number:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ engines/bash/fio --machine fio-atomic-series --directory ~/linux \
       --job atomic-merge --samples 5

It returns after the last sample, with the status of a run of the job
that failed, and records each run whether it passed or not. To run it
as a unit of your service manager, which returns at once, ``--setenv=PATH``
gives the unit your ``PATH``:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ systemd-run --user --setenv=PATH --unit=fio-atomic-series \
       engines/bash/fio --machine fio-atomic-series --directory ~/linux \
       --job atomic-merge

A machine and the family's lines go as blktests' do:
:src:`remove <tasks/qemu-system/remove>` takes the machine away, and
:src:`remove-family <tasks/qemu-system/remove-family>` with
``--family fio`` the lines the family shares, once no machine of it is
left (:doc:`qemu-system`).

.. _requirements-fio:

Requirements
============

The host needs :cmd:`jq` for the record, and what the
:doc:`libguestfs` tasks list for the disk.

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install jq

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console
         :class: cmd-host

         $ sudo dnf install jq

   .. tab-item:: Ubuntu
      :sync: ubuntu

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install jq

.. _fio: https://github.com/axboe/fio
.. _UAPI.9: https://uapi-group.org/specifications/specs/linux_file_system_hierarchy/
.. _fio's example: https://github.com/axboe/fio/blob/master/examples/atomic-verify.fio
