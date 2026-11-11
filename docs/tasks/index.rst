.. SPDX-License-Identifier: copyleft-next-0.3.1

=====
Tasks
=====

A :term:`task <Task>` is a `Bash`_ executable under :src:`tasks`: the commands a
:term:`developer <Developer>` would type to reach one goal. It runs by hand, and
``--help`` prints the one form its arguments take:

.. code-block:: console

   $ tasks/kernel/build --help
   Usage: tasks/kernel/build --directory DIR

   Build the Linux tree in DIR, in its build/, as the .config there says:

     tasks/kernel/build --directory ~/linux

A task's log is a :term:`transcript <Transcript>`: each command after a ``$``
prompt, exactly as it ran, then what it printed. A line copied from it does the
same in a terminal, so a failed run reproduces from its log. An
:term:`option <Option>` keeps the name its :term:`tool <Tool>` gives the
argument, as ``--directory`` is :cmd:`make`'s own.

.. note::

   The line a task logs for its tool names the unit, not the unit's
   settings. Where it runs, what it may write and what files its record
   are the drop-ins under its name (:ref:`tasks-unit`), so the line does
   the same only on a host that has them linked.

.. toctree::
   :maxdepth: 1

   kernel
   qemu

.. _tasks-unit:

The unit a task runs in
=======================

What a task prints
------------------

A task runs its tool as a `unit`_ of your `service manager`_, named for the task
and the directory it works in: ``kernel-build@home-user-linux.service`` builds
``/home/user/linux``. The task shows what the tool prints as it comes, and exits
with the tool's status. Your journal keeps it (:ref:`requirements-journal`),
with the tool's standard error as warnings.

To follow a run from another terminal:

.. code-block:: console

   $ journalctl --user-unit 'kernel-build@*' --follow

Only its warnings and errors:

.. code-block:: console

   $ journalctl --user-unit 'kernel-build@*' --priority warning

What the unit runs, and the processor time and memory it has taken:

.. code-block:: console

   $ systemctl --user status 'kernel-build@*'

.. note::

   The same task is refused a second run on a directory while the first
   lasts.

The unit's settings
-------------------

A unit's settings are `drop-ins`_ under its name, which
kdevops-ng ships in :src:`units/user` (:ref:`requirements-units`). They
have the unit run in the directory it works in, see that directory and
your home read-only, and write only where the task's tool keeps what it
makes, as ``build/`` of a Linux tree, and ``~/.local/state``, where
records go.

A drop-in of your own changes or adds a setting. One under the task's name
holds for every tree, and one under a unit's full name for that tree:

.. code-block:: console

   $ mkdir --parents --verbose ~/.config/systemd/user/kernel-build@.service.d

.. code-block:: ini
   :caption: ~/.config/systemd/user/kernel-build@.service.d/limits.conf

   [Service]
   MemoryHigh=16G
   RuntimeMaxSec=2h

.. code-block:: console

   $ systemctl --user daemon-reload

While a task runs, :cmd:`systemctl` ``--user status`` lists the drop-ins
its unit took. The settings most useful for a build:

.. list-table::
   :header-rows: 1
   :widths: 18 37 45

   * - Setting
     - Example
     - What it does
   * - :cmd:`MemoryHigh=`
     - ``MemoryHigh=16G``
     - Slows the build down above 16G of memory, without killing it.
   * - :cmd:`MemoryMax=`
     - ``MemoryMax=24G``
     - Has the kernel kill a process of the build above 24G.
   * - :cmd:`OOMPolicy=`
     - ``OOMPolicy=kill``
     - Ends the whole build when the kernel kills one of its processes
       for memory, where the default lets make go on.
   * - :cmd:`CPUQuota=`
     - ``CPUQuota=800%``
     - Holds the build to the time of 8 processors.
   * - :cmd:`CPUWeight=`
     - ``CPUWeight=20``
     - Gives the build a fifth of the default share when processors
       are contended, so the desktop stays responsive.
   * - :cmd:`Nice=`
     - ``Nice=10``
     - Lowers the build's scheduling priority.
   * - :cmd:`TasksMax=`
     - ``TasksMax=4096``
     - Caps the number of processes and threads.
   * - :cmd:`RuntimeMaxSec=`
     - ``RuntimeMaxSec=2h``
     - Fails the build after two hours.
   * - :cmd:`ReadWritePaths=`
     - ``ReadWritePaths=%h/.cache/ccache``
     - Lets the build write one more directory, here a compiler cache
       in your home.
   * - :cmd:`Environment=`
     - ``Environment=CCACHE_DIR=%h/.cache/ccache``
     - Sets a variable for make. The unit gets none of your shell's.
   * - :cmd:`Slice=`
     - ``Slice=build.slice``
     - Puts the build in a slice of your own, whose limits then hold
       for every unit in it together.

.. _drop-ins: https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html#Description

.. _Bash: https://www.gnu.org/software/bash/
.. _service manager: https://www.freedesktop.org/software/systemd/man/latest/systemd.html
.. _unit: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
