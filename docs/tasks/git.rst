.. SPDX-License-Identifier: copyleft-next-0.3.1

===
git
===

One :term:`task <Task>` adds the :term:`tree <Tree>` a series is applied
in, or checked at its base, with :cmd:`git worktree`:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/git/worktree --directory ~/linux --path ~/wt/series \
       --commit-ish HEAD

:src:`worktree <tasks/git/worktree>` adds ``--path`` as a detached
worktree of the tree in ``--directory``, at ``--commit-ish``, a full
checkout. Where ``--path`` has a worktree already, it leaves it as it is,
at whatever commit it has, so the task runs again after a failure. It
starts no unit and leaves no :term:`record <Record>`.

.. _requirements-git:

Requirements
============

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install git

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console
         :class: cmd-host

         $ sudo dnf install git

   .. tab-item:: Ubuntu
      :sync: ubuntu

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install git
