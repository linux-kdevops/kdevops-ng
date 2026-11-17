.. SPDX-License-Identifier: copyleft-next-0.3.1

==========
libguestfs
==========

These :term:`tasks <Task>` make a guest that runs a distribution's
cloud image, set up with `libguestfs`_. They work in the guest's state
directory, which you make first: one downloads the image there and one
makes the guest's disk from it:

.. code-block:: console
   :caption: host
   :class: cmd-host

   $ mkdir --parents --verbose ~/.local/state/qemu-system/guest
   $ tasks/libguestfs/download_image \
       --directory ~/.local/state/qemu-system/guest --distribution debian-13
   $ tasks/libguestfs/overlay --directory ~/.local/state/qemu-system/guest \
       --backing-file debian-13-genericcloud-amd64.qcow2

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
             qemu-utils

   .. tab-item:: Fedora
      :sync: fedora

      .. code-block:: console
         :class: cmd-host

         $ sudo dnf install curl gnupg2 ubu-keyring distribution-gpg-keys \
             qemu-img

   .. tab-item:: Ubuntu
      :sync: ubuntu

      .. code-block:: console
         :class: cmd-host

         $ sudo apt install curl gnupg ubuntu-keyring distribution-gpg-keys \
             qemu-utils

.. _libguestfs: https://libguestfs.org
