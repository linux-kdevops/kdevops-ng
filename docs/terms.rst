.. SPDX-License-Identifier: copyleft-next-0.3.1

===========
Terminology
===========

Each term has one meaning across the code, the commits and these pages.
The words under *Avoid* are not used for it.

Actors
======

.. glossary::

   Developer
      A person who runs :term:`tasks <Task>` by hand or starts a
      :term:`workflow <Workflow>`.

      Avoid: *operator*, *user*.

   Host
      The machine a :term:`developer <Developer>` runs tasks on.

      Avoid: *node*, *server*.

   Distribution
      What provides a :term:`host <Host>`'s :term:`tools <Tool>`: `Debian`_,
      `Fedora`_, `Ubuntu`_ or `Nix`_ (:doc:`/getting-started/requirements`).

      Avoid: *distro*, *platform*.

Execution
=========

.. glossary::

   Tool
      A program that does the work: :cmd:`make`, :cmd:`git`, a script of
      the kernel's. A task runs it by its own command line.

      Avoid: *module*, *utility*.

   Task
      A `Bash`_ executable under :src:`tasks`: the commands a developer would
      type to reach one goal (:doc:`/tasks/index`).

      Avoid: *step*, *script*, *action*, *recipe*.

   Option
      What a task is told to work on, ``--option VALUE``, under the name
      the task's tool gives that argument: ``--directory`` is make's.

      Avoid: *parameter*, and *flag*, which is a tool's.

   Workflow
      A file that orders tasks: which run, in what order, for which items
      of a list, and how often again. It is written in the language of one
      :term:`engine <Engine>`. Those of the first, Bash, are under
      ``engines/bash``.

      Avoid: *pipeline*, *playbook*, *flow*, and an engine's own word for
      it, as *DAG*.

   Engine
      A program that runs workflows, such as Bash, `Dagu`_ or
      `Ansible`_. The tasks
      are tied to none.

      Avoid: *orchestrator*, *scheduler*.

   Run
      One execution of a workflow. A :term:`record <Record>` names the run
      it was made in; a task started by hand is in the run ``manual``.

      Avoid: *job*, *build*.

   Transcript
      A task's log: each command after a ``$`` prompt, as it ran, then what
      it printed.

      Avoid: *trace*, *debug log*.

Places
======

.. glossary::

   Checkout
      The directory kdevops-ng is cloned in. Tasks are run from it.

      Avoid: *install*, *workspace*.

   Project
      An upstream whose sources tasks work on, under its source
      directory's name: ``linux``.

      Avoid: *source name*, *repository*.

   Tree
      A directory of a project's sources, a `Git`_ work tree, which a
      developer gives a task with ``--directory``. It is the developer's
      own: a task changes no file it tracks.

      Avoid: *checkout*, *repo*, *source directory*.

   Build
      What `kbuild`_ makes of a tree from one
      :term:`configuration <Configuration>`, for one architecture, with one
      compiler. It is in ``build/`` of the tree (:doc:`/tasks/kernel`).

      Avoid: *build dir*, *output*, *objects*.

   Profile
      A file under :src:`tasks/kernel/files/profiles` that lists `kfragments`_
      fragments, named after the MAINTAINERS entry whose files it configures
      (:ref:`kernel-configuration`).

      Avoid: *config* and *defconfig* for one.

   Configuration
      A :term:`build <Build>`'s ``.config``, under the name of what made it:
      the make target, as ``tinyconfig``, or the :term:`profiles <Profile>`
      the merge_config task merged.

      Avoid: *config* and *defconfig* for a target of another name.

Records
=======

.. glossary::

   Record
      The JSON file a task leaves for one command on one commit and one
      build, in the :term:`kresults` format (:doc:`/records`).

      Avoid: *report*, *result*, *artifact*.

   kresults
      The format of records, and the `repository <kresults_>`_ that
      defines it. A record's own words, as *entry*, *invocation* and
      *verdict*, are defined there.

      Avoid: *results*, *database*.

   Producer
      A program that writes records. kdevops-ng is one.

      Avoid: *engine*, *reporter*.

   Lab
      The name a developer gives the place their records are made, set
      once in Git's configuration. A record carries it, and names no host.
      The format calls it ``origin``.

      Avoid: *site*, *hostname*.

.. _Ansible: https://docs.ansible.com/
.. _Bash: https://www.gnu.org/software/bash/
.. _Dagu: https://github.com/dagucloud/dagu
.. _Debian: https://www.debian.org/releases/testing/
.. _Fedora: https://docs.fedoraproject.org/en-US/releases/rawhide/
.. _Git: https://git-scm.com
.. _kbuild: https://docs.kernel.org/kbuild/index.html
.. _kfragments: https://github.com/linux-kdevops/kfragments
.. _kresults: https://github.com/linux-kdevops/kresults
.. _Nix: https://nixos.org
.. _Ubuntu: https://wiki.ubuntu.com/Releases
