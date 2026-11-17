<!-- SPDX-License-Identifier: copyleft-next-0.3.1 -->

# Guests

A guest boots the kernel a tree built on a distribution's own
userspace. This page holds why its parts are as they are, so a change
starts from the reasons. The tasks are in `tasks/libguestfs`,
`tasks/dracut` and `tasks/kernel`, and `docs/tasks/` says how to run
them.

## 1. A directory for each method

`tasks/libguestfs` makes a guest from a distribution's cloud image:
it downloads the image, makes the guest's disk as an overlay of it,
and sets the disk up with `virt-customize`. The directory is named for
the method, so another way to make a guest gets a directory beside it
and the two share no task.

## 2. The kernel comes from the build

QEMU loads `build/arch/<arch>/boot/bzImage` itself, so a rebuild
reaches the guest at its next start, with nothing installed in its
disk. The modules come the same way: `tasks/kernel/modules_install`
puts them in `build/mod-install/`, the host shares that directory over
virtiofs, and the guest mounts it over `/usr/lib/modules`. The mount
point is `/usr/lib/modules`, not `/lib/modules`: `/lib` is a link on a
merged-usr root, and systemd refuses a mount whose path runs through a
link.

Two things are built in, since the guest uses them before it can load
a module (`tasks/kernel/files/profiles/guest`):

- virtiofs, which mounts the share that holds the modules;
- vsock, which systemd's ssh generator has sshd listen on early in the
  boot.

## 3. The initrd, and why dracut makes it

The kernel builds its root file system's driver as a module, so it
cannot mount the guest's root itself. An initrd made for that kernel
loads the driver and mounts the root, then the modules share.

The share is a line of the guest's own `/etc/fstab`, marked
`x-initrd.mount`, which the initrd's systemd reads from the root it
has mounted. A `dracut --mount` line in the initrd's own fstab did the
same on most boots and hung some: systemd found an ordering cycle
between that mount and `local-fs.target`, broke it by dropping a job,
and at times the job it dropped was the root's mount. With the line in
the guest's fstab no cycle is reported.

`dracut` makes it on every distribution the project supports, Debian
included, where the distribution's own tool is `mkinitramfs` of
initramfs-tools. That one cannot do it:

- It reads the modules from `/lib/modules/<release>` of the host and
  takes no option for another directory (`MODULESDIR` in
  `/usr/sbin/mkinitramfs`). The build's modules would have to be
  installed in the host's root, which needs root and leaves a kernel's
  modules on a host that never boots it (principles 1 and 4).
- It has no option for a mount of its own. The modules share would
  need a hook under `/etc/initramfs-tools`, again the host's.

`dracut --kmoddir` reads the modules where the build put them, and it
runs without root. Its keyboard and font
modules, `i18n` and `console-setup`, write under `/var/lib` and fail
without root, and a guest on a serial console and ssh needs neither, so
the task leaves them out.

On Debian and Ubuntu the program is in `dracut-core`. The `dracut`
package replaces initramfs-tools and makes the host's own initrd again,
which is not ours to change.

## 4. One guest profile, for now

`guest` lists what any distribution's userspace boots on. `AUDIT` is
off in it, as `core/systemd.config` sets it. Debian's cloud image
starts no audit daemon. Fedora's does, and it fails without the option.

What one distribution's userspace needs beyond the others goes in a
profile of its own, joined as `guest+fedora+<subsystem>`, when that
distribution boots: the shared profile stays what every guest needs,
and no guest builds another's options.

## 5. The disk is set up before the first boot

A cloud image expects cloud-init to name the machine and bring its
keys. `tasks/libguestfs/customize` disables cloud-init and does it with
`virt-customize` on the stopped disk, which takes seconds and needs no
boot.

- Root's `authorized_keys` holds the one key the task is given.
- The developer's home mounts at the path it has on the host, so a
  tree and the checkout are at one path on both sides.
- Read-only tmpfs mounts cover `~/.ssh`, `~/.config/systemd` and
  `~/.local/share/systemd` of that home in the guest. The guest's root
  owns every file of the share, and could otherwise add a key ssh
  trusts on the host, or a unit the developer's service manager starts
  at the next login.
- A file for systemd-networkd asks for DHCP on every Ethernet card.
  Debian's and Ubuntu's images run networkd with no configuration once
  cloud-init is off. Fedora's runs NetworkManager, which asks by itself,
  and its networkd is off, so the one file serves all three and the
  task has no branch for a distribution.
- A card no DHCP server answers, as one on a segment guests share,
  takes a link-local address, and multicast DNS, which
  systemd-resolved leaves off, names each guest `NAME.local`. Guests
  thus reach each other by name with no address written for any of
  them, and no task has to know which guests share a segment.
- Each fstab line the task adds carries the option `x-kdevops-ng`,
  which mount ignores, so a second run finds and removes the lines of
  the first.

## 6. The console is a log

A machine's serial console is its unit's log. `TERM=dumb` on the
kernel's command line has systemd write it as plain text. Without it a
boot writes about 570 colour sequences and a handful of queries a
terminal answers: journald stores such lines as binary, and shown
whole they make the reader's terminal type the answers into its shell.

## 7. The image

A distribution is a file under `tasks/libguestfs/files/images`, sourced
by the task: the URLs, and the commands that import the distribution's
key, verify the checksums' signature and check the image. A
distribution that signs nothing leaves the first two empty. The key
goes into a gpg home made for the run, which holds no other, so a good
signature is that key's. The image reaches the guest's directory only
when it has passed.

Debian signs neither its cloud images nor their checksums. Ubuntu and
Fedora sign the checksums, with keys the host's `ubuntu-keyring` and
`distribution-gpg-keys` packages hold.
