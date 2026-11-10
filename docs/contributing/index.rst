.. SPDX-License-Identifier: copyleft-next-0.3.1

============
Contributing
============

Patches go to ``kdevops@lists.linux.dev``. The rules a change follows and
is reviewed against are in :src:`designs`: :src:`designs/principles.md`,
:src:`designs/tasks.md` for a task, and :src:`designs/writing.md` for a
commit, a page and a comment.

.. _requirements-contributing:

Requirements
============

The checks are Bash and Python 3.11 or later, linted by :cmd:`shellcheck`,
:cmd:`shfmt`, black, ruff and pyright. The pages are built by Sphinx and
held to 80 columns by :cmd:`doc8` (:doc:`/getting-started/requirements`):

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console

         $ sudo apt install python3 shellcheck shfmt black ruff
         $ sudo apt install python3-sphinx python3-pydata-sphinx-theme \
             python3-sphinx-copybutton python3-sphinx-design \
             python3-sphinx-autobuild python3-doc8

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console

         $ sudo dnf install python3 ShellCheck black ruff
         $ sudo dnf install python3-sphinx python3-pydata-sphinx-theme \
             python3-sphinx-copybutton python3-sphinx-design \
             python3-sphinx-autobuild

   .. tab-item:: Ubuntu
      :sync: ubuntu

      Most of these are in ``universe``:

      .. code-block:: console

         $ sudo add-apt-repository universe
         $ sudo apt install python3 shellcheck shfmt black
         $ sudo apt install python3-sphinx python3-pydata-sphinx-theme \
             python3-sphinx-copybutton python3-sphinx-design \
             python3-sphinx-autobuild python3-doc8

None of the three packages pyright. Fedora has no shfmt and no doc8, and
Ubuntu no ruff.

Checks
======

Three scripts hold a change to those rules:

.. code-block:: console

   $ scripts/check-style.sh       # the tree and the last commit
   $ scripts/check.py             # each commit of a range
   $ python3 -m unittest discover --start-directory tests

:src:`scripts/commit-msg` runs the checks of a message as the commit-msg
hook. Link it once:

.. code-block:: console

   $ ln --symbolic --verbose --relative scripts/commit-msg \
       "$(git rev-parse --git-path hooks)/commit-msg"

Documentation
=============

These pages are reStructuredText, built with :cmd:`sphinx-build`:

.. code-block:: console

   $ scripts/docs                 # render to docs/_build/html
   $ scripts/serve                # serve on 127.0.0.1:8001, and render on save
   $ scripts/serve --port 8002

:src:`scripts/docs` fails on a warning, and :cmd:`doc8` holds the pages to
80 columns:

.. code-block:: console

   $ doc8 docs
