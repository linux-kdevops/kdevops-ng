#!/usr/bin/env bash
# SPDX-License-Identifier: copyleft-next-0.3.1
# The kernel profiles' check, run from the top of the checkout. A profile
# under tasks/kernel/files/profiles names a MAINTAINERS entry on its second
# line and lists fragments of the catalog tasks/kernel/files/fragments, in
# its merge order; the catalog lists every fragment the vendored kfragments
# has, with ${ARCH} in its name standing for the architecture
# (docs/tasks/kernel.rst, "The configuration").
set -o errexit -o nounset -o pipefail

files=tasks/kernel/files
configs=vendor/kfragments/kernel/configs
arches=(x86_64 arm64 riscv)
status=0

# merge_config merges only what files/fragments lists, and a profile's
# second line names its MAINTAINERS entry, or marks it a guest's.
for profile in "$files"/profiles/*; do
	# shellcheck disable=SC2016 # sed's $, the last line
	if [ ! -s "$profile" ] ||
		! sed --quiet '2{/^# \(MAINTAINERS\|Guest\): ./q;q1};$q1' "$profile"; then
		echo "$0: ${profile##*/} names no MAINTAINERS entry or guest on its second line" >&2
		status=1
	fi
	while read -r fragment; do
		echo "$0: ${profile##*/} lists $fragment, which $files/fragments lacks" >&2
		status=1
	done < <(comm -23 <(sed '/^#/d' "$profile" | sort) <(sed '/^#/d' "$files/fragments" | sort))
done

while read -r fragment; do
	[ -f "$configs/$fragment" ] && continue
	echo "$0: $files/fragments lists $fragment, which kfragments lacks" >&2
	status=1
done < <(for arch in "${arches[@]}"; do sed "/^#/d;s/\${ARCH}/$arch/" "$files/fragments"; done | sort --unique)

# every fragment kfragments has, the catalog lists, with ${ARCH} standing
# for each architecture's own file
while read -r fragment; do
	echo "$0: kfragments has $fragment, which $files/fragments lacks" >&2
	status=1
done < <(comm -23 <(cd "$configs" && find . -name '*.config' -printf '%P\n' | sort) \
	<(for arch in "${arches[@]}"; do sed "/^#/d;s/\${ARCH}/$arch/" "$files/fragments"; done | sort --unique))
exit "$status"
