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
      A person who runs tasks by hand or starts a workflow.

      Avoid: *operator*, *user*.

   Host
      The machine a developer runs tasks on.

      Avoid: *node*, *server*.

   Distribution
      What provides a host's tools: Debian, Fedora, Ubuntu or Nix
      (:doc:`/getting-started/requirements`).

      Avoid: *distro*, *platform*.

Execution
=========

.. glossary::

   Tool
      A program that does the work: :cmd:`make`, :cmd:`git`, a script of
      the kernel's. A task runs it by its own command line.

      Avoid: *module*, *utility*.

   Task
      A Bash executable under :src:`tasks`: the commands a developer would
      type to reach one goal (:doc:`/tasks/index`).

      Avoid: *step*, *script*, *action*, *recipe*.

   Option
      What a task is told to work on, ``--option VALUE``, under the name
      the task's tool gives that argument: ``--directory`` is make's.

      Avoid: *parameter*, and *flag*, which is a tool's.

   Workflow
      A file that orders tasks: which run, in what order, for which items
      of a list, and how often again. It is written in the language of one
      :term:`engine <Engine>`. None exists yet.

      Avoid: *pipeline*, *playbook*, *flow*, and an engine's own word for
      it, as *DAG*.

   Engine
      A program that runs workflows, such as `Dagu`_ or Ansible. The tasks
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
      A directory of a project's sources, a Git work tree, which a
      developer gives a task with ``--directory``. It is the developer's
      own: a task changes no file it tracks.

      Avoid: *checkout*, *repo*, *source directory*.

   Build
      What kbuild makes of a tree from one :term:`configuration
      <Configuration>`, for one architecture, with one compiler. It is in
      ``build/`` of the tree (:doc:`/tasks/kernel`).

      Avoid: *build dir*, *output*, *objects*.

   Configuration
      A build's ``.config``, under the name of the make target that made
      it, as ``tinyconfig``.

      Avoid: *config*, *profile*, and *defconfig* for a target of another
      name.

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

.. _Dagu: https://github.com/dagucloud/dagu
.. _kresults: https://github.com/linux-kdevops/kresults
