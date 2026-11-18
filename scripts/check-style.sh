#!/usr/bin/env bash
# SPDX-License-Identifier: copyleft-next-0.3.1
# Style and commit-message checks, run from the top of the checkout
# (designs/writing.md, "The checks"). LICENSES/ stays byte for byte and the
# images are binary, so both are exempt. vendor/ follows the vendored
# project's own checklist (docs/contributing/vendor.rst).
set -o errexit -o nounset -o pipefail

scope=(-- . ':!LICENSES' ':!*.png' ':!*.ico' ':!vendor')
status=0
here="$(dirname "${BASH_SOURCE[0]}")"

# A message's trailers, matched case-insensitively as the kernel's
# checkpatch.pl matches them. Only the trailer block counts, so a body line
# that quotes a tag is prose, and --no-divider keeps a diff quoted in the
# body from hiding it.
check_trailers() {
	local where="$1" msg="$2" committer="$3" trailers tag last
	trailers="$(printf '%s\n' "$msg" | git interpret-trailers --parse --no-divider)"
	tag="$(printf '%s\n' "$trailers" | grep --ignore-case --only-matching --max-count=1 \
		--extended-regexp '^(assisted-by|generated-by|co-authored-by):' || true)"
	if [ -n "$tag" ]; then
		echo "error: $where: '$tag' is refused: no trailer marks the use of a tool"
		status=1
	fi
	last="$(printf '%s\n' "$trailers" | grep --ignore-case '^Signed-off-by:' |
		tail --lines=1 | sed 's/^[^:]*:[[:space:]]*//' || true)"
	if [ -z "$last" ]; then
		echo "error: $where: missing Signed-off-by trailer"
		status=1
	elif [ "${last,,}" != "${committer,,}" ]; then
		echo "error: $where: the last Signed-off-by must be the committer's ($committer), not: $last"
		status=1
	fi
}

# --commit-msg FILE, for scripts/commit-msg: FILE's trailers and prose only.
# A verbose commit's template carries the diff below git's scissors line,
# which stripspace keeps, so cut there first, as git does.
if [ "${1-}" = "--commit-msg" ]; then
	[ $# -eq 2 ] && [ -r "$2" ] || {
		echo "usage: $0 [--commit-msg FILE]" >&2
		exit 2
	}
	committer="$(git var GIT_COMMITTER_IDENT | sed 's/ [0-9]* [-+][0-9]*$//')"
	msg="$(sed '/^[#;] -* >8 -*$/,$d' "$2" | git stripspace --strip-comments)"
	check_trailers "commit message" "$msg" "$committer"
	printf '%s\n' "$msg" | python3 "$here/check-prose.py" --message - || status=1
	exit "$status"
fi

# 1. Trailing whitespace and carriage returns.
if git grep --line-number --perl-regexp '[ \t]+$|\r' "${scope[@]}" >/dev/null 2>&1; then
	echo "error: trailing whitespace or a carriage return:"
	git grep --line-number --perl-regexp '[ \t]+$|\r' "${scope[@]}"
	status=1
fi

# 2. Missing newline at end of file. A symbolic link is its target's.
while IFS= read -r f; do
	[ -s "$f" ] && [ ! -L "$f" ] || continue
	if [ -n "$(tail --bytes=1 "$f")" ]; then
		echo "error: no newline at end of file: $f"
		status=1
	fi
done < <(git ls-files "${scope[@]}")

# 3. HEAD's trailers, and the prose of its message and of the docs and
#    comments it adds.
msg="$(git log --max-count=1 --format=%B 2>/dev/null || true)"
if [ -n "$msg" ]; then
	check_trailers HEAD "$msg" "$(git log --max-count=1 --format='%cn <%ce>')"
	python3 "$here/check-prose.py" --commit HEAD || status=1
fi

# 4. An SPDX line within the first two lines, so a shebang or the opening
#    of a front matter may come first.
while IFS= read -r f; do
	[ ! -L "$f" ] || continue
	if ! head --lines=2 "$f" | grep --quiet 'SPDX-License-Identifier: '; then
		echo "error: $f: missing 'SPDX-License-Identifier:' in the first two lines"
		status=1
	fi
done < <(git ls-files "${scope[@]}" | grep --extended-regexp '\.(nix|sh|py|md|rst|txt|yaml|yml|toml|jsonc|ini|service|timer)$|(^|/)\.gitignore$|^(scripts|tasks|engines)/(.*/)?[^./]*$' || true)

[ "$status" -eq 0 ] && echo "style: OK"
exit "$status"
