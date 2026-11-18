<!-- SPDX-License-Identifier: copyleft-next-0.3.1 -->

# Mail from lore

`tasks/lorefetch/fetch` keeps the mail of the patches that change one
entry of the kernel's `MAINTAINERS` in a maildir. `docs/tasks/lorefetch.rst`
shows its use. This page holds the decisions behind its query.

## 1. Files of an entry, not a list

A patch for an entry is posted to its list, but also to others (linux-block
for NVMe, linux-kernel for most) and sometimes to none of the entry's
own. A `l:` term would miss those, and one entry's files are what its
maintainers review. The query is thus the entry's `F:` lines, each a
`dfn:` term, which lore matches against the file names in a patch's diff.

- lore indexes a path as its words, so a term is the phrase of the path
  and matches every path that starts with those words. A directory needs
  no wildcard. A pattern is the files it matches in the tree the task
  is given, each a term of its own, so the query names what the entry
  names and nothing beside it. A file a later kernel adds under the
  pattern is found once the tree has it: no term guesses at names.
- `X:` is left out. `NOT dfn:` on an excluded file would drop a series that
  also changes an included one, which the entry still reviews.
- `N:` and `K:` match a patch's text with regular expressions, which lore
  cannot. The maildir holds a little more than the entry's own, never
  less.
- The profile names the entry, as its second line does for
  `tasks/kernel/merge_config`, so no second list of entries exists.

## 2. The noise the query drops

A series that changes the files is not always one to review. Stable's
review series, `[PATCH 6.12 000/670]`, carries hundreds of patches that
change the files, and a `FAILED: patch` mail says a patch did not apply to
a stable tree. For one entry, ten days of a query without these filters
fetched 2272 mails, and with them 231. The query asks for `s:PATCH`, and
not `s:Re`, `s:FAILED` or `t:stable@vger.kernel.org`.

- The stable list is excluded by the To header, not by `tc:`. A patch that
  fixes a bug copies stable on its Cc, and is what the maintainers review.
  The mails sent to stable itself are its own.
- A reply to a patch is no series. `l:` and `s:` match the mail, and lore
  returns the whole thread of each match, so the replies come with the
  patch and a `FAILED:` mail that answers one comes with it too. The
  query cannot stop that.

## 3. The window

`d:30.days.ago..` bounds a first run. Without it the search reaches the
archive's years. A series older than a month was merged or dropped, and
a fetch that wants it is a different job. The window stays inside the
query, as the relative term it is, because lorefetch fetches again from
its last run only when the query text is the same as then: it adds
`dt:` of the last run's time to the query, so the window matters to the
first run alone. A date that changed with each run would make every run
the first.

## 4. The maildir, and the only state

The maildir is `~/.local/state/lore/NAME`: what tasks share lives under
the tool's directory (principle 4), and `NAME` is the profile's, so two
entries never share a maildir or a cache. The task makes `cur`, `new` and
`tmp`, which lorefetch needs.

`.lorefetch-cache.gob` in the maildir is the only state. It holds the
messages written and the last query and time, so nothing of kdevops-ng
records what was fetched, and a maildir removed fetches again from the
start.

## 5. The unit and the record

The tool runs as a unit (U1) with the tree read-only and the maildir and
the task's log the only places it writes. The tool reads no variable, so
the list of `variables` is empty. The network stays open, as lorefetch
needs lore.kernel.org.

The run leaves no record (R1). kresults' `commands.json` has no line for
lorefetch, and nothing of what it fetches says anything about a commit, a
build or a series.
