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
it. Beside the binary it leaves two files, ``version`` and ``url``: the
commit the tree is at, as :cmd:`git` ``describe`` names it, and where to
read that commit, which is empty when no remote of the tree with an
https address has it. lorefetch prints no version, so a
:term:`record <Record>` names its build by them.

Fetching the mail of an entry
=============================

:src:`fetch <tasks/lorefetch/fetch>` fetches the mail of the patch
series that change a file of one entry of the kernel's ``MAINTAINERS``
file, in whichever list they were posted. It takes the Linux
tree for its ``MAINTAINERS``, and the name of a kernel
profile (:doc:`kernel`), whose second line names the entry:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ tasks/lorefetch/fetch --directory ~/linux --profile nvm-express-driver
   $ tasks/lorefetch/record --directory ~/linux --profile nvm-express-driver

The task makes one search term of each ``F:`` line of the entry, which
lore matches against the file names a patch changes, and joins them. The
log shows the query on one line; wrapped, it is:

.. code-block:: text

   (dfn:Documentation/ABI/stable/sysfs-nvme OR
    dfn:Documentation/admin-guide/nvme-multipath.rst OR
    dfn:Documentation/fault-injection/nvme-fault-injection.rst OR
    dfn:Documentation/nvme OR dfn:drivers/nvme/common OR
    dfn:drivers/nvme/host OR dfn:include/linux/nvme-auth.h OR
    dfn:include/linux/nvme-fc-driver.h OR dfn:include/linux/nvme-fc.h OR
    dfn:include/linux/nvme-keyring.h OR dfn:include/linux/nvme-rdma.h OR
    dfn:include/linux/nvme-tcp.h OR dfn:include/linux/nvme.h OR
    dfn:include/uapi/linux/nvme_ioctl.h)
   AND s:PATCH AND NOT s:Re AND NOT s:FAILED
   AND NOT t:stable@vger.kernel.org AND d:30.days.ago..

A directory takes in everything below it, and a pattern such as
``include/linux/nvme-*.h`` is the files it matches in the tree today,
each a term: a file a later kernel adds is found once the tree has it. The entry's ``X:``, ``N:`` and ``K:`` lines are
not used: lore cannot say what they say, and the maildir holds a little
more for it. The query keeps patches, and leaves out what stable's
maintainers send to the stable list: their review series and the mails
that say a patch failed to apply. Those are not what the entry's
maintainers review, though they change the same files. A thread that has
such a mail among replies to a patch it keeps comes whole.

A first run looks back 30 days, since an older series was reviewed or
dropped, and the maildir keeps what it fetches. The query never changes
between runs, and lorefetch then asks only for the mail that came since
the last one.

The maildir is ``~/.local/state/lore/NAME``, with ``NAME`` the profile's.
lorefetch's own ``.lorefetch-cache.gob`` in it is the only state, so
removing the maildir starts the fetch over. The task's unit sees
the tree read-only and writes the maildir and its log, which lies in
``build/logs/lorefetch-fetch/`` of the tree. The run leaves no
record: kresults' format has no command for it.

A timer of yours runs the task again, once an hour here, from a checkout
of kdevops-ng in ``~/kdevops-ng``:

.. code-block:: ini
   :caption: ~/.config/systemd/user/lore-fetch.service

   [Service]
   Type=oneshot
   Environment=PATH=%h/.local/bin:/usr/local/bin:/usr/bin
   ExecStart=%h/kdevops-ng/tasks/lorefetch/fetch --directory %h/linux \
       --profile nvm-express-driver

.. code-block:: ini
   :caption: ~/.config/systemd/user/lore-fetch.timer

   [Timer]
   OnCalendar=hourly
   Persistent=true

   [Install]
   WantedBy=timers.target

.. code-block:: console
   :class: cmd-host

   $ systemctl --user daemon-reload
   $ systemctl --user enable --now lore-fetch.timer

:src:`record <tasks/lorefetch/record>` files each series of the
maildir as a :term:`record <Record>` under its Message-ID, with its
thread (:doc:`/records`): the site then lists it as fetched, and
:doc:`b4 <b4>`'s tasks take the Message-ID from there. A series filed
already is left, so the task runs after every fetch.

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
