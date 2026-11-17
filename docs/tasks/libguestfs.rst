.. SPDX-License-Identifier: copyleft-next-0.3.1

==========
libguestfs
==========

These :term:`tasks <Task>` make a guest that runs a distribution's
cloud image, set up with `libguestfs`_. They work in the guest's state
directory, which you make first: one downloads the image there, one
makes the guest's disk from it, one sets the disk up for its first
boot, and one installs packages in it:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ mkdir --parents --verbose ~/.local/state/qemu-system/guest
   $ tasks/libguestfs/download_image \
       --directory ~/.local/state/qemu-system/guest --distribution debian-13
   $ tasks/libguestfs/overlay --directory ~/.local/state/qemu-system/guest \
       --backing-file debian-13-genericcloud-amd64.qcow2
   $ tasks/libguestfs/customize --directory ~/.local/state/qemu-system/guest \
       --hostname guest --ssh-inject ~/.ssh/guests.pub
   $ tasks/libguestfs/install --directory ~/.local/state/qemu-system/guest \
       --distribution debian-13 --profile block-layer+nvm-express-driver
   $ tasks/libguestfs/install --directory ~/.local/state/qemu-system/guest \
       --distribution debian-13 --profile blktests
   $ tasks/libguestfs/blktests --directory ~/.local/state/qemu-system/guest \
       --copy-in ~/blktests

:src:`download_image <tasks/libguestfs/download_image>` takes the image and
its checksums with :cmd:`curl`, checks the one against the other, and
moves the image into the directory only when it passes: until then the
download lies in ``download/`` there. A run leaves a whole image or
none.

A distribution is a file under :src:`tasks/libguestfs/files/images` that
names the image for this host's machine, ``x86_64`` or ``aarch64``, its
checksums, and how they are checked:

``debian-13``, ``debian-14``
   Debian's generic cloud image; 14 is built daily while it is in
   testing. Debian signs neither the image nor the checksums, so they
   are as good as the TLS they come over.

``ubuntu-26.04``
   Ubuntu's server cloud image, of the release with long-term support.
   :cmd:`gpg` verifies the checksums' signature against the key of the
   ``ubuntu-keyring`` package.

``fedora-44``, ``fedora-45``
   Fedora's generic cloud image. :cmd:`gpg` verifies the checksums'
   signature against the release's key, of the
   ``distribution-gpg-keys`` package.

The key goes into a :cmd:`gpg` home made for the run, which holds no
other, so a good signature is that key's.

:src:`overlay <tasks/libguestfs/overlay>` makes ``work.qcow2`` with
:cmd:`qemu-img`, an overlay of the image: what the guest writes stays in
it and the image stays as downloaded. Making it again starts the guest
over. Stop the guest first.

:src:`customize <tasks/libguestfs/customize>` changes the disk with
:cmd:`virt-customize`, which takes seconds and needs the guest stopped:

- the guest's name, new host keys, and the public key that opens root
  over :cmd:`ssh`, the only one;
- cloud-init off, which would write its own name, keys and network over
  these at the first boot;
- DHCP on every Ethernet card, in a file for systemd-networkd, which
  Debian and Ubuntu run. Fedora's NetworkManager asks by itself. A card
  no server answers takes a link-local address, and multicast DNS
  names the guest ``NAME.local`` to the others on its segment;
- an ``/etc/fstab`` line that mounts the modules of the kernel the
  guest boots, a share of the host, over ``/usr/lib/modules``. It is
  marked ``x-initrd.mount``, so the initrd mounts it before the guest's
  own systemd starts;
- ``/etc/fstab`` lines that mount your home, which the host shares, at
  the path it has on the host, so a tree is at the same path on both
  sides. Three more lines put a read-only tmpfs over ``~/.ssh``,
  ``~/.config/systemd`` and ``~/.local/share/systemd`` in the guest: its
  root could otherwise add a key your :cmd:`ssh` trusts, or a unit your
  service manager starts.

The machine that boots the disk is in :doc:`/getting-started/guest`.
Run the task again after a change: it takes its earlier lines and key out
first.

:src:`install <tasks/libguestfs/install>` puts what a test needs in the
disk before the guest boots. A profile is a file named as the kernel
:term:`profile <Profile>` of what it tests, and holds
:cmd:`virt-customize` commands, one a line, as ``--commands-from-file``
reads them: ``block-layer`` installs fio and blktrace, and
``nvm-express-driver`` nvme-cli. ``install`` runs the guest's own
package manager in the disk, and a package's name is its
distribution's, so the profiles are kept for each family of
distributions, under :src:`tasks/libguestfs/files/profiles`:
``debian``, ``fedora`` and ``ubuntu``. ``--distribution`` takes the name
``download_image`` took and picks the family. Names joined by ``+`` run
each profile in turn. The guest must be stopped.

:src:`blktests <tasks/libguestfs/blktests>` installs `blktests`_ from a
tree of yours, so the guest runs the tests you have checked out. The
``blktests`` profile of ``install`` comes first, once: it holds what the
suite builds with and what its test groups call. The task then copies
the tree into the disk, builds it there with the guest's own compiler,
installs it as ``/usr/lib/blktests``, and deletes the copy. Run it alone
to take a newer blktests, which takes 6 seconds on a Debian 13 disk:
the packages are in the disk already.

With blktests the task installs
:src:`blktests@.service <tasks/libguestfs/files/units/blktests@.service>`
in the disk, the unit that runs a group of its tests, and the mount
unit of the share it keeps their results in (:doc:`/tasks/blktests`).

.. _requirements-libguestfs:

Requirements
============

.. tab-set::
   :sync-group: distro

   .. tab-item:: Debian
      :sync: debian

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install curl gnupg ubuntu-keyring distribution-gpg-keys \
             qemu-utils guestfs-tools openssh-client

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console
         :class: cmd-host

         $ sudo dnf install curl gnupg2 ubu-keyring distribution-gpg-keys \
             qemu-img guestfs-tools openssh-clients

   .. tab-item:: Ubuntu
      :sync: ubuntu

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install curl gnupg ubuntu-keyring distribution-gpg-keys \
             qemu-utils guestfs-tools openssh-client

.. _libguestfs: https://libguestfs.org
.. _blktests: https://github.com/linux-blktests/blktests
