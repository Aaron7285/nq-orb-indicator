"""Self-tests for tools/lint.py. Run: python -m unittest discover -s tools/tests"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import lint  # noqa: E402

HEADER = "// @module core/x\n// @description test\n\n"


def rules(body: str, header: str = HEADER) -> list[str]:
    return [f.rule for f in lint.lint_text(header + body, "src/core/x.pine", "core/x")]


class CodeRuleTests(unittest.TestCase):
    def test_each_forbidden_pattern_is_caught(self):
        cases = {
            "L001": "varip int ticks = 0",
            "L002": 'h = request.security(syminfo.tickerid, "D", high[1], lookahead = barmerge.lookahead_on)',
            "L003": "plot(close, offset = -2)",
            "L004": "age = timenow - time",
            "L005": "if barstate.isrealtime\n    x := 1",
            "L006": 'd = request.security(syminfo.tickerid, "D", close)',
            "L007": 'indicator("x")',
        }
        for rule, body in cases.items():
            with self.subTest(rule=rule):
                self.assertIn(rule, rules(body))

    def test_lower_tf_request_is_also_caught(self):
        self.assertIn("L006", rules('a = request.security_lower_tf(syminfo.tickerid, "1", close)'))

    def test_positive_offset_is_allowed(self):
        self.assertEqual(rules("plot(close, offset = 2)"), [])

    def test_version_annotation_in_module_is_caught(self):
        self.assertIn("L007", rules("//@version=6\na = 1"))

    def test_tab_indentation_is_caught(self):
        self.assertIn("L009", rules("if true\n\tx = 1"))

    def test_clean_code_passes(self):
        body = ("var float orbHigh = na\n"
                "if barstate.isconfirmed\n"
                "    orbHigh := math.max(nz(orbHigh, high), high)\n")
        self.assertEqual(rules(body), [])


class IgnoredContextTests(unittest.TestCase):
    def test_comments_are_ignored(self):
        self.assertEqual(rules("a = 1  // never use varip or timenow here"), [])
        self.assertEqual(rules("// lookahead_on is forbidden"), [])

    def test_strings_are_ignored(self):
        self.assertEqual(rules('label.new(bar_index, high, "varip timenow lookahead_on")'), [])

    def test_escaped_quote_inside_string(self):
        self.assertEqual(rules('s = "say \\"varip\\" twice"'), [])
        self.assertIn("L001", rules('s = "a \\" b"\nvarip x = 1'))

    def test_comment_marker_inside_string_is_not_a_comment(self):
        self.assertIn("L004", rules('s = "http://x" + str.tostring(timenow)'))

    def test_column_numbers_survive_string_blanking(self):
        findings = lint.lint_text(HEADER + 's = "abc" + str.tostring(timenow)', "src/core/x.pine", "core/x")
        self.assertEqual(findings[0].column, len('s = "abc" + str.tostring(') + 1)


class AllowDirectiveTests(unittest.TestCase):
    def test_allow_with_reason_waives_that_rule_on_that_line(self):
        self.assertEqual(rules("t = timenow  // lint-allow: L004 display-only clock in the dashboard"), [])

    def test_allow_does_not_waive_other_rules(self):
        self.assertIn("L001", rules("varip t = timenow  // lint-allow: L004 display-only clock"))

    def test_allow_without_reason_is_an_error(self):
        self.assertEqual(rules("t = timenow  // lint-allow: L004"), ["L000", "L004"])

    def test_allow_unknown_rule_is_an_error(self):
        self.assertIn("L000", rules("a = 1  // lint-allow: L999 because"))

    def test_malformed_allow_is_an_error(self):
        self.assertIn("L000", rules("a = 1  // lint-allow L004 because"))


class ModuleHeaderTests(unittest.TestCase):
    def test_missing_header_is_caught(self):
        self.assertIn("L008", rules("a = 1\n", header=""))

    def test_wrong_module_id_is_caught(self):
        self.assertIn("L008", rules("a = 1\n", header="// @module core/other\n\n"))


class RealRepoTest(unittest.TestCase):
    def test_repository_modules_are_clean(self):
        self.assertEqual(lint.main([]), 0)


if __name__ == "__main__":
    unittest.main()
