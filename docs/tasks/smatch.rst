.. SPDX-License-Identifier: copyleft-next-0.3.1

======
smatch
======

Debian and Ubuntu ship no `smatch`_, and a distribution that ships one may
ship an old one. Three :term:`tasks <Task>` build smatch in its
:term:`tree <Tree>`, install it for you alone, without root, and remove
it again:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/smatch/build --directory ~/smatch-build
   $ tasks/smatch/install --directory ~/smatch-build
   $ tasks/smatch/uninstall

smatch has no build directory: it builds beside its sources, in the files
its ``.gitignore`` names, and changes no file the tree tracks. Give the
tasks a clone you keep for the build, not one you work in, or a worktree
of one:

.. code-block:: console
   :class: cmd-host

   $ git clone https://github.com/error27/smatch.git ~/smatch
   $ git -C ~/smatch worktree add --detach ~/smatch-build

smatch's own repository is https://repo.or.cz/smatch.git, which does not
answer from every country; the one on GitHub is its author's mirror.

:src:`install <tasks/smatch/install>` puts smatch under
``~/.local/lib/smatch``, a prefix of its own as `UAPI.9`_ sorts a user's
files, and links ``~/.local/bin/smatch`` to it. The tree builds programs
of other names too, a sparse among them, and none of those reaches your
``PATH``. The build takes the prefix as well, for smatch finds its data
by it. :src:`uninstall <tasks/smatch/uninstall>` removes the link and
the prefix, and nothing else.

A :term:`record <Record>` names the smatch that ran by the version it
prints, which is what :cmd:`git` ``describe`` names its commit
(:doc:`/records`).

.. _requirements-smatch:

Requirements
============

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install build-essential git pkgconf libsqlite3-dev \
             libssl-dev

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console
         :class: cmd-host

         $ sudo dnf install gcc make git pkgconf sqlite-devel openssl-devel

   .. tab-item:: Ubuntu
      :sync: ubuntu

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install build-essential git pkgconf libsqlite3-dev \
             libssl-dev

``~/.local/bin`` is on your ``PATH`` on each of them once it exists; log in
again after the first install.

.. _smatch: https://github.com/error27/smatch
.. _UAPI.9: https://uapi-group.org/specifications/specs/linux_file_system_hierarchy/
