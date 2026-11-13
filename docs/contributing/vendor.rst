.. SPDX-License-Identifier: copyleft-next-0.3.1

=================
Vendored projects
=================

:src:`vendor/kfragments` is a copy of `kfragments`_, kept with `git-subrepo`_
so a fix can be made and tested in this repository, as an ordinary commit,
before upstream takes it. kfragments holds fragments of a Linux
configuration, one file per feature. No :term:`task <Task>` reads them yet.

``vendor/<name>/.gitrepo`` records the upstream ``remote``, its ``branch``, the
``commit`` the copy was last synced with, and the pull ``method``. A change
under ``vendor/<name>/`` is a commit kept to that directory and written to that
project's rules, in its ``AGENTS.md``, which share this project's commit rules
(:src:`designs/writing.md`). Only the commit that adds a project also wires
the copy into this one. :cmd:`git subrepo` ``pull`` takes upstream's new
commits and commits the files and ``.gitrepo`` as one commit:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ git subrepo clone <remote> vendor/<name> --branch main   # add a copy
   $ git subrepo status                      # each subrepo and its pin
   $ git subrepo pull vendor/kfragments      # take upstream's new commits
   $ git subrepo push vendor/kfragments      # send the local ones upstream
   $ git format-patch --relative=vendor/kfragments \
       <commit>..HEAD -- vendor/kfragments   # or mail them instead

The :ref:`checks <contributing-checks>` skip ``vendor/``, which follows its
project's own checklist: kfragments'
:src:`vendor/kfragments/docs/verification.md`.

.. _requirements-vendor:

Requirements
============

Adding a project to ``vendor/``, and keeping it in step with its upstream,
runs git-subrepo:

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install git-subrepo

   .. tab-item:: Fedora
      :sync: fedora

      `Fedora`_ ships no git-subrepo. Clone it and source its ``.rc`` from your
      shell's startup file:

      .. code-block:: console
         :class: cmd-host

         $ git clone https://github.com/ingydotnet/git-subrepo.git \
             ~/src/git-subrepo

      .. code-block:: diff
         :caption: ~/.bashrc

         --- a/.bashrc
         +++ b/.bashrc
         +source ~/src/git-subrepo/.rc

   .. tab-item:: Ubuntu
      :sync: ubuntu

      git-subrepo is in ``universe``:

      .. code-block:: console
         :class: cmd-host

         $ sudo add-apt-repository universe
         $ sudo apt install git-subrepo

The `Nix`_ shell has it.

.. _Fedora: https://docs.fedoraproject.org/en-US/releases/rawhide/
.. _git-subrepo: https://github.com/ingydotnet/git-subrepo
.. _kfragments: https://github.com/linux-kdevops/kfragments
.. _Nix: https://nixos.org
