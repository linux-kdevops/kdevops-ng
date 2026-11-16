.. SPDX-License-Identifier: copyleft-next-0.3.1

======
sparse
======

Each :term:`distribution <Distribution>` ships `sparse`_, and the kernel
may want a newer one than it ships. Three :term:`tasks <Task>` build
sparse in its :term:`tree <Tree>`, install it for you alone, without
root, and remove it again, as the :doc:`smatch <smatch>` ones do:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ git clone https://git.kernel.org/pub/scm/devel/sparse/sparse.git ~/sparse
   $ git -C ~/sparse worktree add --detach ~/sparse-build
   $ tasks/sparse/build --directory ~/sparse-build
   $ tasks/sparse/install --directory ~/sparse-build
   $ tasks/sparse/uninstall

sparse goes under ``~/.local/lib/sparse``, with ``~/.local/bin/sparse``
linked to it. That one is found before the distribution's on your
``PATH``, and :src:`uninstall <tasks/sparse/uninstall>` gives the
distribution's back.

.. _requirements-sparse:

Requirements
============

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install build-essential git

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console
         :class: cmd-host

         $ sudo dnf install gcc make git

   .. tab-item:: Ubuntu
      :sync: ubuntu

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install build-essential git

.. _sparse: https://git.kernel.org/pub/scm/devel/sparse/sparse.git
