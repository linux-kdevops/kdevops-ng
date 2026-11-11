# SPDX-License-Identifier: copyleft-next-0.3.1
{
  description = "kdevops-ng: Linux kernel development and test automation";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
      # Sphinx with what docs/conf.py loads.
      docsPython =
        pkgs:
        pkgs.python3.withPackages (ps: [
          ps.sphinx
          ps.sphinx-autobuild
          ps.sphinx-copybutton
          ps.sphinx-design
          ps.pydata-sphinx-theme
        ]);
      # Under LLVM=1 kbuild compiles the kernel with -nostdinc, which leaves
      # the wrapper's -nostdlibinc unused, an error with kbuild's -Werror.
      # Clang reports no flag between the two markers as unused.
      clang =
        pkgs:
        pkgs.clang.overrideAttrs (old: {
          postFixup = old.postFixup + ''
            substituteInPlace $out/nix-support/cc-cflags --replace-fail \
              -nostdlibinc \
              "--start-no-unused-arguments -nostdlibinc --end-no-unused-arguments"
          '';
        });
      # What the checks run (docs/contributing/index.rst).
      checkers = pkgs: [
        pkgs.git
        pkgs.python3
        pkgs.shellcheck
        pkgs.shfmt
        pkgs.black
        pkgs.ruff
        pkgs.pyright
        pkgs.python3Packages.doc8
        pkgs.markdownlint-cli2
        (docsPython pkgs)
      ];
    in
    {
      devShells = forAllSystems (pkgs: {
        # Every tool the pages list by another distribution's packages.
        default = pkgs.mkShell {
          packages = checkers pkgs ++ [
            pkgs.gnumake
            pkgs.bc
            pkgs.bison
            pkgs.flex
            pkgs.perl
            # What make runs under LLVM=1.
            (clang pkgs)
            pkgs.lld
            pkgs.llvm
          ];
          # kbuild's host programs link against these.
          buildInputs = [
            pkgs.elfutils
            pkgs.openssl
          ];
          # The kernel sets the flags it is built with itself.
          hardeningDisable = [ "all" ];
        };
      });

      checks = forAllSystems (pkgs: {
        lint =
          pkgs.runCommand "kdevops-ng-lint"
            {
              nativeBuildInputs = checkers pkgs;
            }
            ''
              cd ${./.}
              shellcheck --external-sources --source-path=SCRIPTDIR \
                scripts/check-style.sh scripts/commit-msg scripts/docs scripts/serve \
                tasks/kernel/* tasks/qemu/* tasks/common/*
              shfmt --diff scripts/check-style.sh scripts/commit-msg scripts/docs \
                scripts/serve tasks
              black --check scripts tests docs/conf.py
              ruff check --no-cache scripts tests
              HOME=$TMPDIR pyright
              doc8 docs
              markdownlint-cli2 '**/*.md'
              touch $out
            '';

        tests =
          pkgs.runCommand "kdevops-ng-tests"
            {
              nativeBuildInputs = [
                pkgs.git
                pkgs.python3
              ];
            }
            ''
              cd ${./.}
              python3 -m unittest discover --start-directory tests
              touch $out
            '';

        # Sphinx with its warnings as errors, as scripts/docs runs it.
        docs =
          pkgs.runCommand "kdevops-ng-docs"
            {
              nativeBuildInputs = [ (docsPython pkgs) ];
            }
            ''
              sphinx-build --fail-on-warning --builder html ${./.}/docs $out
            '';
      });

      formatter = forAllSystems (pkgs: pkgs.nixfmt);
    };
}
