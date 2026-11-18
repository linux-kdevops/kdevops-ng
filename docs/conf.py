# SPDX-License-Identifier: copyleft-next-0.3.1
import os
import re

from docutils import nodes
from pygments.lexer import bygroups
from pygments.lexers.diff import DiffLexer
from pygments.token import Generic, Whitespace

project = "kdevops-ng"
copyright = "2026, kdevops-ng authors"
author = "kdevops-ng authors"

extensions = [
    "sphinx_copybutton",
    "sphinx_design",
]

# Show the "$ " prompt but strip it, and follow "\" continuations, on copy.
copybutton_prompt_text = r"\$ "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"

exclude_patterns = [
    "_build",
]

html_theme = "pydata_sphinx_theme"
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "/")
html_static_path = ["_static"]
# A caption that names a file gets a button that copies its path.
html_css_files = ["custom.css"]
html_js_files = ["caption-copy.js"]
html_favicon = "_static/favicon.ico"
html_theme_options = {
    "logo": {
        "image_light": "_static/logo.png",
        "image_dark": "_static/logo.png",
        "alt_text": "kdevops-ng",
    },
    "navigation_with_keys": False,
    "navbar_align": "left",
    "header_links_before_dropdown": 8,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/linux-kdevops/kdevops-ng",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "Discord",
            "url": "https://bit.ly/linux-kdevops-chat",
            "icon": "fa-brands fa-discord",
        },
        {
            "name": "IRC: #kdevops on OFTC",
            "url": "https://webchat.oftc.net/?channels=kdevops",
            "icon": "fa-solid fa-comments",
        },
        {
            "name": "Mailing list: kdevops@lists.linux.dev",
            "url": "mailto:kdevops@lists.linux.dev",
            "icon": "fa-solid fa-envelope",
        },
    ],
}
html_context = {
    "default_mode": "light",
}

# ":cmd:`name`" renders ``name`` as a literal linked to its manual. This table
# is the one place a command's URL is written, so every page links a name the
# same way.
cmd_links = {
    "CPUQuota=": "https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html#CPUQuota=",
    "CPUWeight=": "https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html#CPUWeight=weight",
    "Environment=": "https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Environment=",
    "MemoryHigh=": "https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html#MemoryHigh=bytes",
    "MemoryMax=": "https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html#MemoryMax=bytes",
    "Nice=": "https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Nice=",
    "OOMPolicy=": "https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html#OOMPolicy=",
    "ReadWritePaths=": "https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#ReadWritePaths=",
    "RuntimeMaxSec=": "https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html#RuntimeMaxSec=",
    "Slice=": "https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html#Slice=",
    "TasksMax=": "https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html#TasksMax=N",
    "apt": "https://manpages.debian.org/apt",
    "doc8": "https://github.com/PyCQA/doc8",
    "gpg": "https://www.gnupg.org/documentation/manuals/gnupg/Invoking-GPG.html",
    "curl": "https://curl.se/docs/manpage.html",
    "qemu-img": "https://www.qemu.org/docs/master/tools/qemu-img.html",
    "virt-customize": "https://libguestfs.org/virt-customize.1.html",
    "ssh": "https://man.openbsd.org/ssh",
    "journalctl": "https://www.freedesktop.org/software/systemd/man/latest/journalctl.html",
    "systemd-ssh-proxy": "https://www.freedesktop.org/software/systemd/man/latest/systemd-ssh-proxy.html",
    "git": "https://git-scm.com/docs/git",
    "go build": "https://pkg.go.dev/cmd/go#hdr-Compile_packages_and_dependencies",
    "git subrepo": "https://github.com/ingydotnet/git-subrepo",
    "git worktree": "https://git-scm.com/docs/git-worktree",
    "git describe": "https://git-scm.com/docs/git-describe",
    "env": "https://www.gnu.org/software/coreutils/manual/html_node/env-invocation.html",
    "krecord": "https://github.com/linux-kdevops/kresults/blob/main/format/README.md",
    "kblktests": "https://github.com/linux-kdevops/kresults/blob/main/format/README.md",
    "kobjects": "https://github.com/linux-kdevops/kresults/blob/main/docs/deploy.rst",
    "kseries": "https://github.com/linux-kdevops/kresults/blob/main/docs/deploy.rst",
    "lei": "https://public-inbox.org/lei.html",
    "make": "https://www.gnu.org/software/make/manual/make.html",
    "pip": "https://pip.pypa.io/en/stable/",
    "nix": "https://nix.dev/manual/nix/latest/command-ref/new-cli/nix",
    "shellcheck": "https://www.shellcheck.net/",
    "shfmt": "https://github.com/mvdan/sh",
    "sphinx-autobuild": "https://github.com/sphinx-doc/sphinx-autobuild",
    "sphinx-build": "https://www.sphinx-doc.org/en/master/man/sphinx-build.html",
    "systemd.exec": "https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html",
    "systemd.unit": "https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html",
    "systemd.service": "https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html",
    "systemctl": "https://www.freedesktop.org/software/systemd/man/latest/systemctl.html",
    "tail": "https://www.gnu.org/software/coreutils/manual/html_node/tail-invocation.html",
    "systemd-run": "https://www.freedesktop.org/software/systemd/man/latest/systemd-run.html",
    "systemd.resource-control": "https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html",
    "sudo": "https://www.sudo.ws/docs/man/sudo.man/",
}


def _cmd_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    uri = inliner.document.settings.env.config.cmd_links.get(text)
    code = nodes.literal(rawtext, text)
    if uri is None:
        msg = inliner.reporter.error(
            f"cmd: no link registered for {text!r} (add it to cmd_links in "
            f"docs/conf.py)",
            line=lineno,
        )
        return [code], [msg]
    return [nodes.reference(rawtext, "", code, refuri=uri)], []


# ":src:`path`" renders a repository path as a literal linked to its source on
# GitHub, and ":src:`title <path>`" links a short title. A path missing from
# the tree fails the build.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC_BASE = "https://github.com/linux-kdevops/kdevops-ng"
_EXPLICIT_TITLE_RE = re.compile(r"^(.+?)\s*<(.+?)>$", re.DOTALL)


def _src_url(path):
    full = os.path.join(_REPO_ROOT, path)
    if os.path.isdir(full):
        return f"{_SRC_BASE}/tree/main/{path}"
    if os.path.isfile(full):
        return f"{_SRC_BASE}/blob/main/{path}"
    return None


def _src_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    m = _EXPLICIT_TITLE_RE.match(text)
    title, target = (m.group(1), m.group(2)) if m else (text, text)
    uri = _src_url(target)
    code = nodes.literal(rawtext, title)
    if uri is None:
        msg = inliner.reporter.error(
            f"src: no source found for {target!r} under the repository root",
            line=lineno,
        )
        return [code], [msg]
    return [nodes.reference(rawtext, "", code, refuri=uri)], []


# A diff block is git's output from the "--- a/<path>" line on. Pygments'
# diff lexer reads that line as a deletion and "+++ b/<path>" as an
# insertion, which custom.css paints red and green; read them as the
# heading they are.
class _GitDiffLexer(DiffLexer):
    tokens = {
        "root": [
            (
                r"((?:---|\+\+\+) (?:[ab]/|/dev/null).*)(\n)",
                bygroups(Generic.Heading, Whitespace),
            ),
            *DiffLexer.tokens["root"],
        ]
    }


def setup(app):
    app.add_config_value("cmd_links", {}, "env")
    app.add_role("cmd", _cmd_role)
    app.add_role("src", _src_role)
    app.add_lexer("diff", _GitDiffLexer)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
