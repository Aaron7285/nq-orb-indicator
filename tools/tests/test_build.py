"""Self-tests for tools/build.py. Run: python -m unittest discover -s tools/tests"""
from __future__ import annotations

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build  # noqa: E402

CONFIG = """
[project]
name = "NQ.ORB"
version_file = "VERSION"
module_roots = { src = "", tests = "tests/" }

[indicator]
overlay = true
max_lines_count = 500

[targets.main]
output = "dist/NQ_ORB.pine"
title = "NQ.ORB"
modules = {modules}
"""


class RepoFixture:
    """A throwaway repository with a build.toml, VERSION and module files."""

    def __init__(self, modules: dict[str, str], target_modules: list[str], version: str = "1.2.3"):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "build.toml").write_text(
            CONFIG.replace("{modules}", str(target_modules).replace("'", '"')), encoding="utf-8")
        (self.root / "VERSION").write_text(version + "\n", encoding="utf-8")
        for rel, text in modules.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")

    def build(self, *args: str) -> int:
        return build.main(list(args), repo=self.root)

    def output(self) -> str:
        return (self.root / "dist/NQ_ORB.pine").read_text(encoding="utf-8")

    def close(self) -> None:
        self._tmp.cleanup()


def module(module_id: str, body: str, requires: str = "") -> str:
    header = f"// @module {module_id}\n"
    if requires:
        header += f"// @requires {requires}\n"
    return header + "// @description test module\n\n" + body + "\n"


class BuildTests(unittest.TestCase):
    def repo(self, modules, target_modules, **kw) -> RepoFixture:
        fixture = RepoFixture(modules, target_modules, **kw)
        self.addCleanup(fixture.close)
        return fixture

    def test_dependencies_come_first_in_listed_order(self):
        repo = self.repo({
            "src/core/a.pine": module("core/a", "a = 1"),
            "src/core/b.pine": module("core/b", "b = 2", requires="core/a"),
            "src/modules/c.pine": module("modules/c", "c = a + b", requires="core/b, core/a"),
        }, ["modules/c"])
        self.assertEqual(repo.build(), 0)
        text = repo.output()
        self.assertLess(text.index("a = 1"), text.index("b = 2"))
        self.assertLess(text.index("b = 2"), text.index("c = a + b"))
        self.assertIn("// Modules: core/a, core/b, modules/c", text)

    def test_header_has_version_title_and_indicator_settings(self):
        repo = self.repo({"src/core/a.pine": module("core/a", "a = 1")}, ["core/a"], version="0.4.0")
        repo.build()
        text = repo.output()
        self.assertIn("//@version=6", text)
        self.assertIn('indicator("NQ.ORB", shorttitle = "NQ.ORB", overlay = true, max_lines_count = 500)', text)
        self.assertIn('NQORB_VERSION = "0.4.0"', text)
        self.assertIn('NQORB_TARGET = "main"', text)
        self.assertNotIn("@module", text, "metadata lines must not be copied into the output")

    def test_version_line_comes_before_any_code(self):
        repo = self.repo({"src/core/a.pine": module("core/a", "a = 1")}, ["core/a"])
        repo.build()
        lines = repo.output().splitlines()
        first_code = next(i for i, line in enumerate(lines) if line and not line.startswith("//"))
        self.assertLess(lines.index("//@version=6"), first_code)

    def test_cycle_is_reported(self):
        repo = self.repo({
            "src/core/a.pine": module("core/a", "a = 1", requires="core/b"),
            "src/core/b.pine": module("core/b", "b = 1", requires="core/a"),
        }, ["core/a"])
        with self.assertRaisesRegex(build.BuildError, "dependency cycle: core/a -> core/b -> core/a"):
            build.build_all(repo.root)

    def test_unknown_dependency_is_reported(self):
        repo = self.repo({"src/core/a.pine": module("core/a", "a = 1", requires="core/missing")}, ["core/a"])
        with self.assertRaisesRegex(build.BuildError, "requires unknown module 'core/missing'"):
            build.build_all(repo.root)

    def test_module_id_must_match_path(self):
        repo = self.repo({"src/core/a.pine": module("core/wrong", "a = 1")}, ["core/a"])
        with self.assertRaisesRegex(build.BuildError, "must be '@module core/a'"):
            build.build_all(repo.root)

    def test_missing_module_header_is_reported(self):
        repo = self.repo({"src/core/a.pine": "a = 1\n"}, ["core/a"])
        with self.assertRaisesRegex(build.BuildError, "missing '// @module core/a' header"):
            build.build_all(repo.root)

    def test_tests_folder_modules_get_tests_prefix(self):
        repo = self.repo({
            "src/core/a.pine": module("core/a", "a = 1"),
            "tests/core_selftest.pine": module("tests/core_selftest", "t = a", requires="core/a"),
        }, ["tests/core_selftest"])
        self.assertEqual(repo.build(), 0)
        self.assertIn("MODULE tests/core_selftest", repo.output())

    def test_check_mode_detects_missing_and_stale_output(self):
        repo = self.repo({"src/core/a.pine": module("core/a", "a = 1")}, ["core/a"])
        self.assertEqual(repo.build("--check"), 1, "missing output must fail --check")
        self.assertEqual(repo.build(), 0)
        self.assertEqual(repo.build("--check"), 0)
        (repo.root / "src/core/a.pine").write_text(module("core/a", "a = 2"), encoding="utf-8")
        self.assertEqual(repo.build("--check"), 1, "changed source must fail --check")

    def test_orphan_output_fails_check_and_can_be_pruned(self):
        repo = self.repo({"src/core/a.pine": module("core/a", "a = 1")}, ["core/a"])
        repo.build()
        orphan = repo.root / "dist/test/old_test.pine"
        orphan.parent.mkdir(parents=True)
        orphan.write_text("old", encoding="utf-8")
        self.assertEqual(repo.build("--check"), 1)
        self.assertEqual(repo.build("--prune"), 0)
        self.assertFalse(orphan.exists())
        self.assertEqual(repo.build("--check"), 0)

    def test_output_is_normalized(self):
        repo = self.repo({"src/core/a.pine": module("core/a", "a = 1   \n\n\n\n\nb = 2")}, ["core/a"])
        repo.build()
        text = repo.output()
        self.assertNotIn("   \n", text)
        self.assertNotIn("\n\n\n\n", text)
        self.assertTrue(text.endswith("b = 2\n"))

    def test_bad_version_is_rejected(self):
        repo = self.repo({"src/core/a.pine": module("core/a", "a = 1")}, ["core/a"], version="v1")
        with self.assertRaisesRegex(build.BuildError, "VERSION must look like 1.2.3"):
            build.build_all(repo.root)


class RealRepoTest(unittest.TestCase):
    def test_repository_builds_cleanly(self):
        """The real build.toml and modules must load and render without errors."""
        results = build.build_all(build.REPO_ROOT)
        self.assertIn("main", results)


if __name__ == "__main__":
    unittest.main()
