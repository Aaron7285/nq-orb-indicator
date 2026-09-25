#!/usr/bin/env python3
"""Build NQ.ORB TradingView scripts from module files.

TradingView runs one self-contained file per indicator and cannot include other
files. This tool joins the module files under src/ and tests/ into single
scripts in dist/, in dependency order, below a generated header.

Every module file starts with a metadata block:

    // @module core/levels
    // @requires core/types, core/time
    // @description One line saying what the module does.

Usage:
    python tools/build.py            build every target in build.toml
    python tools/build.py --check    fail if dist/ is not up to date (used by CI)
    python tools/build.py --prune    also delete dist/ files no target produces
    python tools/build.py --list     list modules and targets
"""
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = "build.toml"

MODULE_ID_RE = re.compile(r"^[a-z0-9_]+(/[a-z0-9_]+)*$")
META_RE = re.compile(r"^//\s*@([a-z]+)\b\s*(.*)$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
META_KEYS = {"module", "requires", "description"}
RULE = "// " + "=" * 76


class BuildError(Exception):
    """A problem that stops the build. The message says what to fix."""


@dataclass
class Module:
    id: str
    path: str  # repo-relative, forward slashes
    requires: list[str]
    description: str
    body: str  # source without the metadata block


# --------------------------------------------------------------------------- modules

def expected_module_id(rel_path: Path, prefix: str) -> str:
    """The module id a file must declare, derived from where it lives."""
    return prefix + rel_path.with_suffix("").as_posix()


def parse_module(text: str, display_path: str, expected_id: str) -> Module:
    """Split a module file into its metadata block and body, validating both."""
    lines = text.splitlines()
    meta: dict[str, list[str]] = {}
    i = 0
    while i < len(lines):
        match = META_RE.match(lines[i].strip())
        if not match:
            break
        key, value = match.group(1), match.group(2).strip()
        if key not in META_KEYS:
            raise BuildError(f"{display_path}:{i + 1}: unknown metadata key '@{key}' "
                             f"(allowed: {', '.join(sorted(META_KEYS))})")
        meta.setdefault(key, []).append(value)
        i += 1

    if "module" not in meta:
        raise BuildError(f"{display_path}:1: missing '// @module {expected_id}' header")
    if len(meta["module"]) != 1:
        raise BuildError(f"{display_path}: '@module' appears more than once")
    module_id = meta["module"][0]
    if module_id != expected_id:
        raise BuildError(f"{display_path}: declares '@module {module_id}' but its path "
                         f"means it must be '@module {expected_id}'")
    if not MODULE_ID_RE.match(module_id):
        raise BuildError(f"{display_path}: module id '{module_id}' may only use "
                         "lowercase letters, digits, '_' and '/'")

    requires: list[str] = []
    for value in meta.get("requires", []):
        requires.extend(part for part in re.split(r"[,\s]+", value) if part)
    if module_id in requires:
        raise BuildError(f"{display_path}: module requires itself")

    body = "\n".join(lines[i:]).strip("\n")
    return Module(module_id, display_path, requires,
                  " ".join(meta.get("description", [])), body)


def load_modules(repo: Path, roots: dict[str, str]) -> dict[str, Module]:
    """Read every *.pine file under the configured module roots."""
    modules: dict[str, Module] = {}
    errors: list[str] = []
    for root_name, prefix in roots.items():
        root = repo / root_name
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.pine")):
            rel = path.relative_to(root)
            display = path.relative_to(repo).as_posix()
            try:
                module = parse_module(path.read_text(encoding="utf-8"), display,
                                      expected_module_id(rel, prefix))
            except BuildError as exc:
                errors.append(str(exc))
                continue
            if module.id in modules:
                errors.append(f"{display}: module id '{module.id}' is already used by "
                              f"{modules[module.id].path}")
                continue
            modules[module.id] = module
    for module in modules.values():
        for dep in module.requires:
            if dep not in modules:
                errors.append(f"{module.path}: requires unknown module '{dep}'")
    if errors:
        raise BuildError("\n".join(errors))
    return modules


def resolve_order(wanted: list[str], modules: dict[str, Module]) -> list[Module]:
    """Return the wanted modules plus their dependencies, dependencies first.

    The order is stable: dependencies appear in the order they are listed, and
    top-level modules in the order the target lists them.
    """
    ordered: list[Module] = []
    done: set[str] = set()

    def visit(module_id: str, chain: list[str]) -> None:
        if module_id in done:
            return
        if module_id in chain:
            cycle = " -> ".join(chain[chain.index(module_id):] + [module_id])
            raise BuildError(f"dependency cycle: {cycle}")
        if module_id not in modules:
            raise BuildError(f"unknown module '{module_id}'")
        for dep in modules[module_id].requires:
            visit(dep, chain + [module_id])
        done.add(module_id)
        ordered.append(modules[module_id])

    for module_id in wanted:
        visit(module_id, [])
    return ordered


# --------------------------------------------------------------------------- rendering

def pine_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    raise BuildError(f"unsupported indicator() setting value: {value!r}")


def pine_string(value: str, what: str) -> str:
    if '"' in value or "\\" in value or "\n" in value:
        raise BuildError(f"{what} must not contain quotes, backslashes or newlines: {value!r}")
    return f'"{value}"'


def normalize(text: str) -> str:
    """Strip trailing spaces, collapse runs of blank lines, end with one newline."""
    lines = [line.rstrip() for line in text.splitlines()]
    out: list[str] = []
    for line in lines:
        if line == "" and len(out) >= 2 and out[-1] == "" and out[-2] == "":
            continue
        out.append(line)
    return "\n".join(out).strip("\n") + "\n"


def render_target(name: str, target: dict, ordered: list[Module], version: str,
                  indicator: dict) -> str:
    title = target["title"]
    shorttitle = target.get("shorttitle", title)
    settings = ", ".join(f"{key} = {pine_value(val)}" for key, val in indicator.items())
    parts = [
        RULE,
        f"// {title} · v{version}",
        "// GENERATED FILE. Do not edit by hand: edit the files in src/ and tests/,",
        "// then run `python tools/build.py`.",
        "// Modules: " + ", ".join(m.id for m in ordered),
        RULE,
        "//@version=6",
        f"indicator({pine_string(title, 'title')}, shorttitle = "
        f"{pine_string(shorttitle, 'shorttitle')}, {settings})",
        "",
        "// Build constants (generated)",
        f"NQORB_VERSION = {pine_string(version, 'version')}",
        f"NQORB_TARGET = {pine_string(name, 'target name')}",
    ]
    for module in ordered:
        parts += ["", "", RULE, f"// MODULE {module.id}  ({module.path})"]
        if module.description:
            parts.append(f"// {module.description}")
        parts += [RULE, "", module.body]
    return normalize("\n".join(parts))


# --------------------------------------------------------------------------- config

def load_config(repo: Path) -> dict:
    path = repo / CONFIG_FILE
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise BuildError(f"{CONFIG_FILE} not found in {repo}") from None
    except tomllib.TOMLDecodeError as exc:
        raise BuildError(f"{CONFIG_FILE}: {exc}") from None
    for section in ("project", "indicator", "targets"):
        if section not in config:
            raise BuildError(f"{CONFIG_FILE}: missing [{section}] section")
    for name, target in config["targets"].items():
        for key in ("output", "title", "modules"):
            if key not in target:
                raise BuildError(f"{CONFIG_FILE}: target '{name}' is missing '{key}'")
        if not str(target["output"]).startswith("dist/") or not target["output"].endswith(".pine"):
            raise BuildError(f"{CONFIG_FILE}: target '{name}' output must be dist/*.pine")
    outputs = [t["output"] for t in config["targets"].values()]
    if len(outputs) != len(set(outputs)):
        raise BuildError(f"{CONFIG_FILE}: two targets write the same output file")
    return config


def read_version(repo: Path, project: dict) -> str:
    version = (repo / project.get("version_file", "VERSION")).read_text(encoding="utf-8").strip()
    if not VERSION_RE.match(version):
        raise BuildError(f"VERSION must look like 1.2.3, found {version!r}")
    return version


def build_all(repo: Path) -> dict[str, tuple[dict, list[Module], str]]:
    """Render every target. Returns {target name: (target config, modules, text)}."""
    config = load_config(repo)
    project = config["project"]
    modules = load_modules(repo, project.get("module_roots", {"src": "", "tests": "tests/"}))
    version = read_version(repo, project)
    results = {}
    for name, target in config["targets"].items():
        ordered = resolve_order(target["modules"], modules)
        text = render_target(name, target, ordered, version, config["indicator"])
        results[name] = (target, ordered, text)
    return results


def orphan_outputs(repo: Path, expected: set[str]) -> list[str]:
    dist = repo / "dist"
    if not dist.is_dir():
        return []
    found = {p.relative_to(repo).as_posix() for p in dist.rglob("*.pine")}
    return sorted(found - expected)


# --------------------------------------------------------------------------- main

def main(argv: list[str] | None = None, repo: Path = REPO_ROOT) -> int:
    parser = argparse.ArgumentParser(description="Build NQ.ORB TradingView scripts.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail if dist/ is out of date")
    mode.add_argument("--list", action="store_true", help="list modules and targets")
    parser.add_argument("--prune", action="store_true", help="delete stale files in dist/")
    args = parser.parse_args(argv)

    try:
        results = build_all(repo)
    except BuildError as exc:
        print(f"BUILD FAILED\n{exc}", file=sys.stderr)
        return 1

    if args.list:
        for name, (target, ordered, _) in results.items():
            print(f"{name}: {target['output']}")
            for module in ordered:
                print(f"    {module.id:<32} {module.path}")
        return 0

    problems = 0
    for name, (target, ordered, text) in results.items():
        out = repo / target["output"]
        current = out.read_text(encoding="utf-8") if out.exists() else None
        lines = text.count("\n")
        if args.check:
            if current != text:
                state = "missing" if current is None else "out of date"
                print(f"STALE  {target['output']} is {state}. Run: python tools/build.py")
                problems += 1
            else:
                print(f"ok     {target['output']}  ({lines} lines, {len(ordered)} module(s))")
        else:
            if current != text:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(text, encoding="utf-8", newline="\n")
                print(f"built  {target['output']}  ({lines} lines, {len(ordered)} module(s))")
            else:
                print(f"same   {target['output']}  ({lines} lines, {len(ordered)} module(s))")

    expected = {t["output"] for t, _, _ in results.values()}
    for orphan in orphan_outputs(repo, expected):
        if args.prune and not args.check:
            (repo / orphan).unlink()
            print(f"pruned {orphan}")
        else:
            print(f"STALE  {orphan} is not produced by any target in {CONFIG_FILE}. "
                  "Run: python tools/build.py --prune")
            problems += 1 if args.check else 0

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
