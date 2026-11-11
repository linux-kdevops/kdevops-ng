.. SPDX-License-Identifier: copyleft-next-0.3.1

===========
Quick start
===========

Install `Git`_ (:doc:`requirements`) and what the kernel :term:`tasks <Task>`
run (:ref:`requirements-kernel`), then clone kdevops-ng:

.. code-block:: console

   $ git clone https://github.com/linux-kdevops/kdevops-ng.git
   $ cd kdevops-ng

Configure and build a `Linux`_ :term:`tree <Tree>` of your own. The two tasks
write in ``build/`` of the tree and nowhere else in it:

.. code-block:: console

   $ tasks/kernel/kconfig --directory ~/linux --target tinyconfig
   $ tasks/kernel/build --directory ~/linux

The kernel is in ``build/`` of the tree. :doc:`/tasks/kernel` has the
rest, and :doc:`/records` how the two tasks file what :cmd:`make` reported.

.. _Git: https://git-scm.com
.. _Linux: https://kernel.org
