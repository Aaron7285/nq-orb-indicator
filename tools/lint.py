#!/usr/bin/env python3
"""Repaint and safety checks for NQ.ORB Pine Script modules.

Enforces docs/PLAN.md §8: every pattern below can make an indicator behave
differently on history than it did live, or breaks the module contract.
Matches inside comments and string literals are ignored.

A rule can be waived on one line only with a written reason, for example:
    x = foo()  // lint-allow: L002 approved higher-timeframe helper, see docs/rules/...

Usage:
    python tools/lint.py              lint every module under src/ and tests/
    python tools/lint.py FILE...      lint specific files
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import (REPO_ROOT, BuildError, expected_module_id, load_config,  # noqa: E402
                   parse_module)

ALLOW_RE = re.compile(r"lint-allow:\s*(L\d{3}(?:\s*,\s*L\d{3})*)(?:\s+(\S.*))?")

# (rule id, pattern applied to code with comments/strings removed, explanation)
CODE_RULES: list[tuple[str, re.Pattern[str], str]] = [
    ("L001", re.compile(r"\bvarip\b"),
     "`varip` keeps values across live ticks, so history and live can differ (PLAN §8.5)"),
    ("L002", re.compile(r"\blookahead_on\b"),
     "`lookahead_on` can read future data on historical bars (PLAN §8.4)"),
    ("L003", re.compile(r"\boffset\s*=\s*-"),
     "a negative plot offset draws values earlier than they were known (PLAN §8.4)"),
    ("L004", re.compile(r"\btimenow\b"),
     "`timenow` differs between history and live; use bar time instead (PLAN §8.9)"),
    ("L005", re.compile(r"\bbarstate\.isrealtime\b"),
     "logic that branches on `barstate.isrealtime` behaves differently on history (PLAN §8.9)"),
    ("L006", re.compile(r"\brequest\.security(?:_lower_tf)?\b"),
     "v1 uses no data from other timeframes; all levels come from chart candles (PLAN §8.4)"),
    ("L007", re.compile(r"\b(?:indicator|strategy|library)\s*\("),
     "modules must not declare indicator()/strategy()/library(); the build writes the header"),
]
RULE_IDS = {rule for rule, _, _ in CODE_RULES} | {"L007", "L008", "L009"}


@dataclass
class Finding:
    path: str
    line: int
    column: int
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}:{self.column}: {self.rule} {self.message}"


def split_code_comment(line: str) -> tuple[str, str]:
    """Return (code, comment). String literal contents in the code are blanked
    with spaces, so column numbers stay correct and text in strings never matches."""
    code: list[str] = []
    quote: str | None = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == "\\" and i + 1 < len(line):
                code.append("  ")
                i += 2
                continue
            if ch == quote:
                quote = None
                code.append(ch)
            else:
                code.append(" ")
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            code.append(ch)
        elif line.startswith("//", i):
            return "".join(code), line[i + 2:]
        else:
            code.append(ch)
        i += 1
    return "".join(code), ""


def lint_text(text: str, display_path: str, expected_id: str | None) -> list[Finding]:
    findings: list[Finding] = []

    if expected_id is not None:
        try:
            parse_module(text, display_path, expected_id)
        except BuildError as exc:
            findings.append(Finding(display_path, 1, 1, "L008", f"module header: {exc}"))

    for number, raw in enumerate(text.splitlines(), start=1):
        code, comment = split_code_comment(raw)

        allowed: set[str] = set()
        allow = ALLOW_RE.search(comment)
        if allow:
            rules = {r.strip() for r in allow.group(1).split(",")}
            unknown = rules - RULE_IDS
            if not allow.group(2):
                findings.append(Finding(display_path, number, 1, "L000",
                                        "lint-allow needs a written reason after the rule id"))
            elif unknown:
                findings.append(Finding(display_path, number, 1, "L000",
                                        f"lint-allow names unknown rule(s): {', '.join(sorted(unknown))}"))
            else:
                allowed = rules
        elif "lint-allow" in comment:
            findings.append(Finding(display_path, number, 1, "L000",
                                    "malformed lint-allow; use '// lint-allow: L00X reason'"))

        for rule, pattern, message in CODE_RULES:
            for match in pattern.finditer(code):
                if rule not in allowed:
                    findings.append(Finding(display_path, number, match.start() + 1, rule, message))

        if raw.lstrip().startswith("//@version") and "L007" not in allowed:
            findings.append(Finding(display_path, number, 1, "L007",
                                    "modules must not contain //@version; the build writes the header"))
        tab = raw.find("\t")
        if tab >= 0 and "L009" not in allowed:
            findings.append(Finding(display_path, number, tab + 1, "L009",
                                    "tab character; indent with 4 spaces"))
    return findings


def module_files(repo: Path) -> list[tuple[Path, str]]:
    """Every module file with the id its path requires."""
    roots = load_config(repo)["project"].get("module_roots", {"src": "", "tests": "tests/"})
    files = []
    for root_name, prefix in roots.items():
        root = repo / root_name
        if root.is_dir():
            for path in sorted(root.rglob("*.pine")):
                files.append((path, expected_module_id(path.relative_to(root), prefix)))
    return files


def main(argv: list[str] | None = None, repo: Path = REPO_ROOT) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        targets = module_files(repo)
    except BuildError as exc:
        print(f"LINT FAILED\n{exc}", file=sys.stderr)
        return 1
    if argv:
        wanted = {Path(a).resolve() for a in argv}
        known = {p.resolve(): mid for p, mid in targets}
        targets = [(p, known.get(p)) for p in sorted(wanted)]

    findings: list[Finding] = []
    for path, expected_id in targets:
        display = path.relative_to(repo).as_posix() if path.is_relative_to(repo) else str(path)
        findings += lint_text(path.read_text(encoding="utf-8"), display, expected_id)

    for finding in findings:
        print(finding)
    print(f"lint: {len(targets)} file(s) checked, {len(findings)} problem(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
