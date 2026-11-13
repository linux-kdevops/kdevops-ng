# SPDX-License-Identifier: copyleft-next-0.3.1
"""Test scripts/check-profiles.sh on a fixture checkout."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check-profiles.sh"
# The script reads the checkout from its working directory, so the tests
# give each one a fixture tree.
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
Result = subprocess.CompletedProcess[str]

CATALOG = """# SPDX-License-Identifier: copyleft-next-0.3.1
core/core.config
arch/${ARCH}.config
storage/block-layer.config
"""
PROFILE = """# SPDX-License-Identifier: copyleft-next-0.3.1
# MAINTAINERS: BLOCK LAYER
core/core.config
arch/${ARCH}.config
storage/block-layer.config
"""


class ProfilesTest(unittest.TestCase):
    """Each test gives the check a fixture checkout and reads its verdict."""

    def setUp(self) -> None:
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.files = self.tmp / "tasks" / "kernel" / "files"
        self.profiles = self.files / "profiles"
        self.configs = self.tmp / "vendor" / "kfragments" / "kernel" / "configs"
        self.profiles.mkdir(parents=True)
        (self.files / "fragments").write_text(CATALOG)
        (self.profiles / "block-layer").write_text(PROFILE)
        self.configs.mkdir(parents=True)
        for name in (
            "core/core.config",
            "storage/block-layer.config",
            "arch/x86_64.config",
            "arch/arm64.config",
            "arch/riscv.config",
        ):
            (self.configs / name).parent.mkdir(parents=True, exist_ok=True)
            (self.configs / name).write_text("CONFIG_FOO=y\n")

    def check(self) -> Result:
        # Through bash: the build sandbox has no /usr/bin/env for the
        # script's shebang, as the flake's lint check has not either.
        return subprocess.run(
            ["bash", SCRIPT],
            cwd=self.tmp,
            env=ENV,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    def test_passes(self) -> None:
        self.assertEqual((self.check().returncode, self.check().stdout), (0, ""))

    def test_profile_lists_an_unknown_fragment(self) -> None:
        (self.profiles / "block-layer").write_text(PROFILE + "fs/xfs.config\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("block-layer lists fs/xfs.config", result.stdout)

    def test_catalog_lists_a_fragment_kfragments_lacks(self) -> None:
        (self.configs / "storage" / "block-layer.config").unlink()
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "storage/block-layer.config, which kfragments lacks", result.stdout
        )

    def test_catalog_lacks_a_fragment_kfragments_has(self) -> None:
        (self.configs / "fs").mkdir()
        (self.configs / "fs" / "xfs.config").write_text("CONFIG_XFS_FS=m\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("kfragments has fs/xfs.config", result.stdout)

    def test_profile_names_no_entry(self) -> None:
        profile = self.profiles / "block-layer"
        profile.write_text(
            "\n".join(
                line for line in PROFILE.splitlines() if "MAINTAINERS" not in line
            )
            + "\n"
        )
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("names no MAINTAINERS entry", result.stdout)


if __name__ == "__main__":
    unittest.main()
