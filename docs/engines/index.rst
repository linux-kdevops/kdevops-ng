.. SPDX-License-Identifier: copyleft-next-0.3.1

=======
Engines
=======

A :term:`workflow <Workflow>` orders :term:`tasks <Task>`: which run,
in what order, on which earlier result, and how often again. It is
written for one :term:`engine <Engine>`, in that engine's language, and
holds no command of a :term:`tool <Tool>`: the tasks have those, so a
workflow for another engine writes the control flow again and nothing
more. The workflows of an engine are under ``engines/``, in a
directory of its name.

.. toctree::
   :maxdepth: 1

   bash
