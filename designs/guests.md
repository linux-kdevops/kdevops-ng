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

## 4. One guest profile, and one for a distribution that asks more

`guest` lists what any distribution's userspace boots on. `AUDIT` is
off in it, as `core/systemd.config` sets it. Debian's cloud image
starts no audit daemon. Fedora's does: `auditd.service` and
`audit-rules.service` fail without the option, the boot ends
`degraded`, and a workflow that waits for `running` never goes on.

What one distribution's userspace needs beyond the others goes in a
profile of its own, joined as `guest+fedora+<subsystem>`: the shared
profile stays what every guest needs, and no guest builds another's
options. `fedora` has one fragment, `core/audit.config`. The units are
not masked in the image instead: the guest then runs as Fedora ships
it, and the image's setup has no branch for a distribution. The price
is a build of its own, and so records of its own, for a Fedora guest.

## 5. The disk is set up before the first boot

A cloud image expects cloud-init to name the machine and bring its
keys. `tasks/libguestfs/customize` disables cloud-init and does it with
`virt-customize` on the stopped disk, which takes seconds and needs no
boot.

- Root's `authorized_keys` holds the one key the task is given.
- The developer's home mounts at the path it has on the host, so a
  tree and the checkout are at one path on both sides.
- That home is root's home in the guest. A login lands in the
  developer's files with their shell's settings, and a file either side
  makes there is the developer's on the host, since virtiofsd maps the
  guest's root to them. `/etc/passwd` is edited for it: `usermod`
  refuses a user that runs a process, as root does in the appliance.
- Read-only mounts cover `~/.ssh`, `~/.config/systemd` and
  `~/.local/share/systemd` of that home in the guest. The guest's root
  owns every file of the share, and could otherwise read the
  developer's keys, add a key ssh trusts on the host, or a unit the
  developer's service manager starts at the next login. The rest of
  the home is open to it, which is the price of one path on both sides.
- Over `~/.ssh` the disk's `/root/.ssh` is mounted, with the key. A
  setting of sshd cannot name another place: for a connection over
  vsock systemd starts sshd with `AuthorizedKeysFile` on its command
  line, which a file under `/etc/ssh` does not override.
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

## 6. What a test needs is a profile

A guest that tests a subsystem needs that subsystem's tools. They are
listed where the kernel's options for it are: a profile of the same
name, under `tasks/libguestfs/files/profiles`, joined with `+` as the
kernel's are. The file holds virt-customize's own commands, which
`--commands-from-file` reads, so the task adds no format of its own
and a profile can do whatever virt-customize can. libguestfs has no
name for such a file; "profile" is this project's.

A package's name is its distribution's, and one tool may have three.
The profiles are thus kept for each family, `debian`, `fedora` and
`ubuntu`, and the task picks the directory from the distribution's
name, the part before its release. A profile is repeated where the
three agree: a file that reads the same is clearer than a rule for
when they share one.

## 7. A suite is built in the disk, from the developer's tree

A test suite the distribution does not package, as blktests, is
installed the way libguestfs installs anything built from source:
`virt-customize` installs the build's packages, copies the tree in,
builds and installs it with the guest's own compiler, and deletes the
copy. The packages are a profile of the install task and the build a
task of its own, so a newer tree of the suite is taken without the
package manager running again. The suite is thus built against the guest's
libraries, on any of the three distributions, and the host needs none
of them.

The tree is the developer's, given to the task, so the guest runs the
tests of the commit they have checked out, and a test under review is
tested before it is merged. Running a suite straight from the home
share would save the copy, but it would write the suite's results and
its built files into the developer's tree.

## 8. A suite's task runs where the suite is

`tasks/blktests/check` runs the suite's own command on the machine it
is started on, and opens no connection. How it gets started in the
guest is the developer's, or a workflow's (T5): ssh today, an engine's
own transport later. The home share makes that one command: the
checkout is in the guest at its host path.

The guest's systemd is the second way to start a group:
`blktests@.service`, a unit file of the guest, since it stays there
(principle 3), installed with the suite. `systemctl` starts it, in the
guest or from the host with `--host`, which is systemctl's own option,
so nothing of the project carries the transport here either. The unit
is one-shot: `start` returns the group's verdict, and with `--no-block`
the group outlives the session that started it, which a command over
ssh does not. Blocking or not is the caller's to choose on that line.

Two tasks on the host act on a guest this way, `tasks/blktests/start`
and `tasks/qemu-system/is-system-running`: each runs `systemctl
--host`, so a workflow has a task to call for it and still holds no
command. They cannot run in the guest, where `tasks/blktests/check`
and plain `systemctl` do the same without a connection. The first
fails until the guest takes one, and the workflow repeats it (T5).

A task that ran ssh itself could not run it in a unit. A unit of the
developer's service manager that is sandboxed at all runs in a user
namespace, where the files root owns are nobody's, and ssh refuses a
configuration that neither root nor the developer owns.

## 9. A suite's config and results lie with the guest

A kernel task works in a tree, on its sources and its build, and its
output goes to that tree's `build/`. A suite works in a guest: its
results are of that machine, its devices and its userspace as much as
of the kernel. They go to the guest's state directory on the host,
`blktests/` there, which the machine's file shares under the tag
`blktests` and the guest mounts at `/var/lib/blktests`.

- The kernel's build is the first directory inside: its release and
  the first twelve digits of the sha256 of its `.config`. The guest
  boots whatever kernel its machine file names, so the name is what
  ties a result to a build, and one build's results outlast the boot
  of another's. The release alone does not: it stays as it is when the
  `.config` changes, and results of the build before were filed as
  this one's. The guest hashes `/proc/config.gz`, which holds the
  build's `.config` byte for byte, and the host the file itself.
- A unit's settings take specifiers and no hash, so
  `blktests-machine.service` links the directory as `/run/blktests`
  and the service's settings name the link.
- Neither the unit nor the task takes a tree. A template's instance
  holds one name, the group, and the task needs nothing more.
- The share is its own, not a path of the home share, which would put
  the host's layout in a unit file of the guest.
- A mount unit, not a line of fstab. It is the suite's file, installed
  and replaced with it, where a line would have each run of the
  install edit a file `customize` owns.
- Nothing mounts it at boot: the service asks for it with
  `RequiresMountsFor=` and the task starts it. A machine without the
  share boots as before, and both fail there before a test runs, so
  no run leaves results in the disk by mistake.
- The directory is not in a tree's `build/`, so `mrproper` leaves the
  machine able to start.
- `machine/` under the build holds what a record of a test names
  and the suite's results lack: the guest's `/proc/cpuinfo`,
  `/proc/meminfo` and arch, and the commit of the suite with the
  address to read it at, which the install wrote into the disk. The
  address is that of the first remote of the developer's tree that has
  the commit and an `https` address, and empty where none has: a
  commit no public tree holds has no link. They are copied as they are, with `cp`,
  before each run. The reader on the host takes what it needs, so the
  guest runs no code of the project and needs none of its tools.
- What the suite prints goes to two files under the build, named for
  what was asked, as a task's output goes to files (`designs/output.md`):
  blktests says why a test did not run nowhere else, and the journal
  drops lines. The unit's settings write them, the task's `tee`. The
  files are on the host as they grow, so a run is followed there.
- A unit of its own, `blktests-machine.service`, makes `machine/` and
  copies the facts. systemd opens a unit's output files before it runs
  any of its commands, and before it makes a `StateDirectory=`: a unit
  whose output lies in a directory it makes itself fails with status
  209. The service requires that unit, which does not stay active and
  so runs again before each group.
- The machine's QEMU is named on the host, by the record task, from
  the machine's running process: nothing in the guest names the build
  of the QEMU it runs on. A record made after the machine has started
  again on another QEMU would name the wrong one.
- The records are made on the host, by a task that takes the tree: the
  commit, the `.config` and the profiles are there, and they name
  which results are that build's. A test's date is the guest's
  local time, which a cloud image keeps in UTC.
- The suite's config is a file of the same directory, read as
  `/var/lib/blktests/config`. It names devices the machine's file
  defines, so the two are kept on the host side by side, and a change
  to it needs no stop of the guest and no write to its disk. The
  project's file is one to copy and change, as a machine's is. The
  unit and the task always name it: a machine has a config, though it
  may set nothing.

## 9a. A suite runs in several guests at once

A group of blktests is the unit a guest runs, so the groups are what
runs side by side: a machine for each, on the series' kernel and on
its base's. Nothing deals tests out and nothing merges results: each
machine's share is recorded by itself, and the records of one build
lie together.

- A machine is named for the suite, the group and the kernel,
  `blktests-nvme-tcp-series`, with a name of the series after it where
  two are tested at once. The suite comes first, so the family's
  drop-in directory, `blktests-.qemu.d`, holds what every machine of
  the suite shares, its share among them: `%i` in a value is the
  machine's name.
- A machine's own file holds what no prefix of its name selects: its
  vsock number, which the generator takes as a number, and its kernel.
  `tasks/qemu-system/machine` writes it from a file with two marks, with
  a number one above the highest in use, and a second run keeps the
  number. The kernel is not a link in the state directory: the
  generator has systemd make a share that lies there, and that would
  reach into the developer's tree.
- The task copies the family's directory where it is missing and
  leaves it otherwise. The family's file runs as it is, with no line
  a developer must change first, so a workflow makes a machine with no
  step by hand. What a series asks of its machines is added, never
  edited in: `tasks/qemu-system/qemu` writes a drop-in of the
  machine's own that names the QEMU a tree built, and a namespace's
  options go in a drop-in of the family, as `set=device.ns0.NAME=VALUE`
  lines, QEMU's own way to set a property of a device by its id. A
  second `device=` line would be a second device, so the family's
  namespaces have ids for it. `tasks/qemu-system/drop-in` copies such
  a file into a machine's own directory, which `remove` deletes with
  the machine, and the ones worth keeping lie in `drop-ins/` of the
  family's files.
- The root a kernel command line names differs by distribution, the
  first partition on Debian and Ubuntu, a btrfs subvolume of the third
  on Fedora. The distribution's file under
  `tasks/libguestfs/files/images` says it, beside where its image
  comes from, and `tasks/qemu-system/machine` reads it there, so the
  machine's file has it and no family's file is per distribution.
- `download_image` leaves a link named for the distribution beside
  the image, `debian-14.qcow2`, so a workflow names an image without
  the file name its distribution gave it.
- The disk the machines are overlays of lies with the images,
  `~/.local/state/machines/blktests-<distribution>/`, one for each
  distribution. `engines/bash/blktests-disk` makes it. It is a task of
  `qemu-system`, since a machine is what it works on, and it finds the
  family's files by the first word of the name, under
  `tasks/qemu-system/files/families`; `files/machines` there keeps the
  machines a developer copies and names. What a suite adds to a
  machine is the suite's task, as `tasks/blktests/config`.
- `tasks/qemu-system/remove` takes a machine away: its file and its
  state directory, the disk and the shares with it. The family's
  lines stay for the other machines.
- A long group splits by what its config sets, the transports of nvme.
  The config reads the transport from the machine's name, so every
  machine has the same file and the same disk, any of them can run any
  transport, and the split needs no option of a unit or a task. A
  machine named for no transport runs them all.
- Each machine's disk is an overlay of one disk that has the packages
  and the suite, which no machine starts. A machine is made in
  seconds and downloads nothing.
- The namespaces are raw sparse files the machine's unit removes and
  makes at each start, with `cache=unsafe`, `discard=unmap` and
  `detect-zeroes=unmap`: a test's data is of no use after it, a flush
  that reaches the disk is time lost, and a discard gives the room
  back. They are not `null-co`, which drops what is written: tests
  that make a file system or verify what they wrote, and the metadata
  of a namespace, need it back. QEMU has no block driver that keeps
  its data in memory; a file on tmpfs would, at the price of the
  host's memory for every byte written.
- The fan-out is a workflow's. `engines/bash/blktests-machine` makes
  a machine from its name, and `engines/bash/blktests` starts it, waits
  for the boot, runs the group the name gives and files the records,
  whether the group passed or not. It blocks; the developer runs one
  for each machine under `systemd-run --user`, so each returns at once
  and its lines are in the journal. How many run at once is the host's
  processors and memory over what the family's file gives a machine.
  More guests than processors make tests that measure time fail.
- A machine has 4G: with 2G the kernel killed a test of the block
  group under KASAN. The unit has `OOMPolicy=continue`, so a test
  that is killed fails and the group goes on.

## 10. Where a suite's files go in the guest

The guest's paths follow the UAPI group's file hierarchy
specification, which gives a package these: `/usr/lib/<package>/` for
what is its alone, private programs included, `/etc/<package>/` for
the machine's configuration of it, and `/var/lib/<package>/` for its
persistent data. It does not name `/usr/local`, and advises against
`/opt`.

- blktests is one directory of scripts, tests and helpers that run
  from where they lie, so it is installed as `/usr/lib/blktests`, with
  `prefix=/usr/lib` in place of its Makefile's `/usr/local`.
- Its configuration is given to `check` with `--config`: its own
  default is a `config` file inside its directory, which `/usr` is not
  the place for. `/etc/blktests/config` would be the specification's
  place, in the guest's disk. It is in the share instead (section 9).
- Its results go to `/var/lib/blktests`, given with `--output`
  (section 9). Its own default is `results/` inside its directory.

## 11. The console is a log

A machine's serial console is its unit's log. `TERM=dumb` on the
kernel's command line has systemd write it as plain text. Without it a
boot writes about 570 colour sequences and a handful of queries a
terminal answers: journald stores such lines as binary, and shown
whole they make the reader's terminal type the answers into its shell.

## 12. The image

A distribution is a file under `tasks/libguestfs/files/images`, sourced
by the task: the URLs, and the commands that import the distribution's
key, verify the checksums' signature and check the image. A
distribution that signs nothing leaves the first two empty. The key
goes into a gpg home made for the run, which holds no other, so a good
signature is that key's. The image reaches its directory only when it
has passed.

The images lie in one directory of the host, `~/.local/state/machines`
in the docs, and each guest's disk is an overlay of one by its path: a
distribution is downloaded once however many guests run it. The
directory is the user's `/var/lib/machines`, as `~/.local/state` is a
user's `/var/lib`. It is not under `~/.cache`: an overlay does not
open without its image, and a cache is what may be emptied. The tasks
take the directory and the image as options and name no default.

Debian signs neither its cloud images nor their checksums. Ubuntu and
Fedora sign the checksums, with keys the host's `ubuntu-keyring` and
`distribution-gpg-keys` packages hold.
