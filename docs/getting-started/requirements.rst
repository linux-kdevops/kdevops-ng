.. SPDX-License-Identifier: copyleft-next-0.3.1

============
Requirements
============

kdevops-ng needs `Linux`_ with `systemd`_ 258 or later, and `Git`_ to clone it.
A :term:`task <Task>` calls every other :term:`tool <Tool>` by its name, and the
:term:`host <Host>`'s :term:`distribution <Distribution>` provides it.

Distributions
=============

Four are supported: `Debian`_ testing, `Fedora`_ Rawhide, the development
release of `Ubuntu`_, and `Nix`_ with `nixpkgs`_' unstable branch. Nix is the
preferred one, for reproducibility: it pins every tool, so two hosts run the
same build of each, and a :doc:`record </records>` names that build.

Nix
---

The flake stands for every package list of these pages. In the
:term:`checkout <Checkout>`, one command opens a shell with all the tools:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ nix develop

It needs the :cmd:`nix` command and flakes enabled, once:

.. code-block:: console
   :class: cmd-host

   $ mkdir --parents --verbose ~/.config/nix

.. code-block:: ini
   :caption: ~/.config/nix/nix.conf

   experimental-features = nix-command flakes

Debian, Fedora and Ubuntu
-------------------------

Root installs the packages, once. Nothing in kdevops-ng runs :cmd:`sudo`:
each list is a command for you to run.

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

.. _requirements-journal:

The journal
===========

A task runs its tool as a unit of your service manager, and what the tool
printed is read back from your own journal. `journald`_ keeps a journal for each
user only while it stores on disk, under ``/var/log/journal``. Every
distribution here sets that up, so most hosts need nothing. Check that yours has
the file:

.. code-block:: console
   :class: cmd-host

   $ ls /var/log/journal/*/user-"$(id --user)".journal

If it is missing, the journal is still in memory, under ``/run``. Root
moves it to disk, once there is room on ``/var``:

.. code-block:: console
   :class: cmd-host

   $ sudo mkdir --parents --verbose /var/log/journal
   $ sudo journalctl --flush

Your own journal needs no group. To read the system's too, as
:cmd:`journalctl` does without ``--user``, join ``systemd-journal`` and log
in again:

.. code-block:: console
   :class: cmd-host

   $ sudo usermod --append --groups systemd-journal "$(whoami)"

.. _requirements-io:

I/O accounting
==============

A :doc:`record </records>` says how much a run read and wrote where your
service manager accounts for I/O. systemd gives a user's service manager
the ``cpu``, ``memory`` and ``pids`` controllers only. Root adds ``io``,
once, and it holds from your next login:

.. code-block:: console
   :class: cmd-host

   $ sudo mkdir --parents --verbose /etc/systemd/system/user@.service.d

.. code-block:: ini
   :caption: /etc/systemd/system/user@.service.d/delegate.conf

   [Service]
   Delegate=pids memory cpu io

.. code-block:: console
   :class: cmd-host

   $ sudo systemctl daemon-reload

Check that your service manager has it:

.. code-block:: console
   :class: cmd-host

   $ cat "/sys/fs/cgroup/user.slice/user-$UID.slice/user@$UID.service/cgroup.controllers"
   cpu io memory pids

Without it a record leaves those figures out. systemd accounts for
network traffic in system services only, so no record has it.

What each part needs
====================

Each part of kdevops-ng lists its own tools, on its page:

- :ref:`The kernel tasks <requirements-kernel>`: :cmd:`make`, a compiler
  and `Perl`_.
- :ref:`The QEMU tasks <requirements-qemu>`: `Meson`_, :cmd:`make`, a
  compiler and `Perl`_.
- :ref:`The smatch tasks <requirements-smatch>`: :cmd:`make`, a compiler
  and two libraries.
- :ref:`The sparse tasks <requirements-sparse>`: :cmd:`make` and a
  compiler.
- :ref:`Records <requirements-records>`: `kresults`_' :cmd:`krecord`, and a name
  for your :term:`lab <Lab>`.
- :ref:`A change to kdevops-ng <requirements-contributing>`: the checks, and
  `Sphinx`_ for these pages.
- :ref:`Vendored projects <requirements-vendor>`: `git-subrepo`_.

.. _Debian: https://www.debian.org/releases/testing/
.. _Fedora: https://docs.fedoraproject.org/en-US/releases/rawhide/
.. _Git: https://git-scm.com
.. _git-subrepo: https://github.com/ingydotnet/git-subrepo
.. _journald: https://www.freedesktop.org/software/systemd/man/latest/systemd-journald.service.html
.. _kresults: https://github.com/linux-kdevops/kresults
.. _Linux: https://kernel.org
.. _Meson: https://mesonbuild.com
.. _Nix: https://nixos.org
.. _nixpkgs: https://github.com/NixOS/nixpkgs
.. _Perl: https://www.perl.org
.. _service manager: https://www.freedesktop.org/software/systemd/man/latest/systemd.html
.. _Sphinx: https://www.sphinx-doc.org
.. _systemd: https://systemd.io
.. _Ubuntu: https://wiki.ubuntu.com/Releases
.. _unit: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
