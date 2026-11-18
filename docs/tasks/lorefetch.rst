.. SPDX-License-Identifier: copyleft-next-0.3.1

=========
lorefetch
=========

Watching a list for patches is a search of `lore.kernel.org`_, run
again as new mail arrives. `lorefetch`_ runs it: it fetches the mail a
query matches, answering the archive's anti-bot challenge, into a
maildir, and a second run fetches only the mail the maildir lacks.

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ lorefetch --query 'l:linux-nvme AND s:PATCH AND NOT s:Re AND \
       d:3.days.ago..' --maildir ~/.local/state/lore/nvme

The query is the one :cmd:`lei` takes. `lei-q(1)`_ lists the search
terms in its "SEARCH TERMS" section, and Xapian's `query parser`_
documents the syntax beneath them.

No :term:`distribution <Distribution>` ships lorefetch. Three
:term:`tasks <Task>` build it in its :term:`tree <Tree>`, install it
for you alone, without root, and remove it again, as the
:doc:`sparse <sparse>` ones do. The tree is the ``dagomez/main`` branch
of a fork, which has what the tool's own tree has not taken yet: the
second run that fetches only new mail.

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ git clone --branch dagomez/main \
       https://github.com/dagomez137/lorefetch.git ~/lorefetch
   $ tasks/lorefetch/build --directory ~/lorefetch
   $ tasks/lorefetch/install --directory ~/lorefetch
   $ tasks/lorefetch/uninstall

:src:`build <tasks/lorefetch/build>` runs :cmd:`go build`, which needs
nothing from the network: the tool uses Go's own library alone. The
binary is ``build/lorefetch`` of the tree, and
:src:`install <tasks/lorefetch/install>` puts it under
``~/.local/lib/lorefetch``, with ``~/.local/bin/lorefetch`` linked to
it.

.. _requirements-lorefetch:

Requirements
============

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install golang-go git

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console
         :class: cmd-host

         $ sudo dnf install golang git

   .. tab-item:: Ubuntu
      :sync: ubuntu

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install golang-go git

.. _lei-q(1): https://public-inbox.org/lei-q.html
.. _lore.kernel.org: https://lore.kernel.org
.. _lorefetch: https://github.com/jwdevantier/lorefetch
.. _query parser: https://xapian.org/docs/queryparser.html
