"""
Tests for AGENT_OS_SYNTHESIS.md (repo root).

This PR adds a pure-documentation file with no executable code, so there is
nothing to unit-test in the traditional sense. Instead, these tests validate
the structural integrity and factual self-consistency of the document itself:

- required sections exist and appear in the expected order
- fenced code blocks are balanced (every ``` open has a matching close)
- the "Reconciled" audit callouts exist where the doc claims they do
- specific corrected facts (kali-mcp line/tool counts, tmux status, empty
  placeholder repos, repo count) are stated consistently across the doc
- cross-references between prose and the Phase 2 findings table resolve to
  an actual finding, catching drift if the doc is edited later

Run with: python3 -m unittest tests/test_agent_os_synthesis.py -v
(or pytest, if installed: pytest tests/test_agent_os_synthesis.py)
"""

import re
import unittest
from pathlib import Path

DOC_PATH = Path(__file__).resolve().parent.parent / "AGENT_OS_SYNTHESIS.md"


class AgentOsSynthesisDocTests(unittest.TestCase):
    """Structural + content-consistency checks for AGENT_OS_SYNTHESIS.md."""

    @classmethod
    def setUpClass(cls):
        cls.text = DOC_PATH.read_text(encoding="utf-8")
        cls.lines = cls.text.splitlines()

    # ------------------------------------------------------------------
    # Basic existence / sanity
    # ------------------------------------------------------------------

    def test_file_exists(self):
        self.assertTrue(DOC_PATH.is_file(), f"{DOC_PATH} should exist")

    def test_file_is_nonempty(self):
        self.assertGreater(len(self.text.strip()), 0)

    def test_title_is_expected(self):
        self.assertEqual(
            self.lines[0],
            "# AutoBoros Agent OS — Repo Synthesis + Build Prompts",
        )

    def test_no_leftover_placeholder_markers(self):
        # A finished doc shouldn't ship with editing placeholders.
        for marker in ("FIXME", "XXX", "TBD", "Lorem ipsum"):
            self.assertNotIn(
                marker,
                self.text,
                f"unexpected leftover placeholder marker: {marker!r}",
            )
        # "TODO" does appear once, but only as a quoted example of what NOT
        # to write (inside the §4.3 system-prompt style guide) — not as a
        # leftover editing placeholder. Pin the count and location so a
        # future, genuinely-forgotten TODO still gets caught.
        self.assertEqual(self.text.count("TODO"), 1)
        self.assertIn('no "TODO: handle edge case"', self.text)

    # ------------------------------------------------------------------
    # Section structure
    # ------------------------------------------------------------------

    def test_required_top_level_sections_present_in_order(self):
        required_headers = [
            "## 1. What's actually good — keep and promote to \"core OS\"",
            "## 2. What's redundant or should be retired",
            "## 3. Recommended consolidated architecture (\"aces in their places\")",
            "## 4. Build prompts — one per surface",
            "## 5. Immediate next actions (in priority order)",
            "## Gaps I couldn't fill from here",
            "# LIVE AUDIT RECORD (added 2026-07-10)",
            "## Phase 1 — Inventory (CLAIM | DOC SAYS | REALITY | DELTA)",
            "## Phase 2 — Invariant findings (SEVERITY | FILE:LINE | ISSUE | FIX)",
            "## Phase 4 — Top-3 fix proposals (NOT executed — awaiting go)",
        ]
        positions = []
        for header in required_headers:
            idx = self.text.find(header)
            self.assertNotEqual(idx, -1, f"missing required header: {header!r}")
            positions.append(idx)
        # Headers must appear in this exact document order.
        self.assertEqual(
            positions,
            sorted(positions),
            "required headers are present but out of expected order",
        )

    def test_build_prompt_subsections_present(self):
        for sub in (
            "### 4.1 Claude Code — `CLAUDE.md` (project root)",
            "### 4.2 Claude Code — slash command example (`.claude/commands/kernel-review.md`)",
            "### 4.3 Cursor / other IDE — `.cursorrules` or system prompt",
            "### 4.4 Raw CLI / terminal agent (Codex CLI, aider, generic agent loop) — system prompt",
        ):
            self.assertIn(sub, self.text)

    # ------------------------------------------------------------------
    # Markdown structural integrity
    # ------------------------------------------------------------------

    def test_fenced_code_blocks_are_balanced(self):
        fence_lines = [line for line in self.lines if line.startswith("```")]
        self.assertEqual(
            len(fence_lines) % 2,
            0,
            "fenced code blocks (```) must open and close in pairs",
        )
        self.assertGreater(len(fence_lines), 0, "expected at least one fenced code block")

    def test_no_trailing_whitespace_in_headers(self):
        for line in self.lines:
            if line.startswith("#"):
                self.assertEqual(line, line.rstrip(), f"header has trailing whitespace: {line!r}")

    # ------------------------------------------------------------------
    # "Reconciled" audit callouts
    # ------------------------------------------------------------------

    def test_reconciled_callout_count(self):
        # Anchored to line-start so we don't match the backtick-quoted
        # example of the callout syntax in the intro paragraph.
        callouts = re.findall(r"^> \*\*Reconciled", self.text, flags=re.MULTILINE)
        self.assertEqual(len(callouts), 6)

    def test_reconciled_callouts_follow_each_original_claim_section(self):
        # Each of these anchor phrases (from the pre-reconciliation prose)
        # must be followed somewhere later in the doc by a "Reconciled" callout.
        anchor_then_callout = [
            ("Family-locked embedding failover", "Reconciled (row: rate ledging / handoff / embedding)"),
            ("kali-mcp/mcp_server.py at 217/500+ lines", "Reconciled (kali-mcp claim"),
            ('The routing rule ("aces in their places")', "Reconciled (does the split exist in code"),
            ("Codex CLI, aider, generic agent loop", "Reconciled (§4.4 note)"),
            ("Consolidate the three overlapping Ouroboros/Aurora master docs", "Reconciled (priority order after live audit)"),
            ("Local machine state (tkpsz3, Radxa, etc.)", '> **Reconciled:** the "no live access"'),
        ]
        for anchor, callout in anchor_then_callout:
            anchor_idx = self.text.find(anchor)
            callout_idx = self.text.find(callout)
            self.assertNotEqual(anchor_idx, -1, f"anchor text not found: {anchor!r}")
            self.assertNotEqual(callout_idx, -1, f"callout text not found: {callout!r}")
            self.assertLess(
                anchor_idx,
                callout_idx,
                f"expected {callout!r} to appear after {anchor!r}",
            )

    # ------------------------------------------------------------------
    # Corrected-fact consistency (the whole point of the "reconciled" doc)
    # ------------------------------------------------------------------

    def test_kali_mcp_is_stated_as_complete_not_broken(self):
        self.assertIn(
            "217 lines, and it is\n> complete, not truncated.",
            self.text,
        )
        self.assertIn("14 working `@mcp.tool` functions", self.text)
        self.assertIn("14 `@mcp.tool` fns", self.text)
        self.assertIn("14 tools", self.text)
        # The corrected framing must explicitly say it is NOT a P0 blocker.
        self.assertIn("not the P0 the doc claimed", self.text)
        self.assertIn("`kali-mcp` is **not** blocking", self.text)

    def test_kali_mcp_tool_inventory_has_fourteen_entries(self):
        match = re.search(
            r"kali-mcp tool inventory \| \(not enumerated\) \| `([^`]+)`",
            self.text,
        )
        self.assertIsNotNone(match, "could not locate the kali-mcp tool inventory table cell")
        raw_tools = match.group(1)
        # kali_tmux_new/send/read expands to 3 separate tools.
        tools = []
        for entry in raw_tools.split(","):
            entry = entry.strip()
            if "/" in entry and entry.startswith("kali_tmux"):
                prefix = "kali_tmux_"
                suffixes = entry[len(prefix):].split("/")
                tools.extend(prefix + s for s in suffixes)
            else:
                tools.append(entry)
        self.assertEqual(len(tools), 14, f"expected 14 tools, got {len(tools)}: {tools}")
        self.assertNotIn("kali_hashcat", tools)
        self.assertNotIn("kali_impacket", " ".join(tools))

    def test_tmux_corrected_from_missing_to_present(self):
        # Original (uncorrected) prose claims tmux is missing...
        self.assertIn(
            "tmux/hashcat/impacket/AD-enum missing",
            self.text,
        )
        # ...but the reconciliation explicitly overrides that for tmux.
        self.assertIn("**tmux is present**", self.text)
        self.assertIn("kali_tmux_new", self.text)
        self.assertIn("kali_tmux_send", self.text)
        self.assertIn("kali_tmux_read", self.text)
        self.assertIn("tmux claim wrong; other 3 confirmed", self.text)

    def test_placeholder_repos_stated_consistently(self):
        occurrences = self.text.count("empty placeholder")
        self.assertGreaterEqual(
            occurrences,
            2,
            "autoboros-backend/autoboros-cockpit 'empty placeholder' status "
            "should be reiterated in more than one section",
        )
        for name in ("autoboros-backend", "autoboros-cockpit"):
            self.assertIn(name, self.text)
        self.assertIn("Aurora-AI-Agency/autoboros/", self.text)

    def test_repo_inventory_has_seventeen_entries_matching_the_claim(self):
        self.assertIn("(17 repos)", self.text)
        self.assertIn("17 cloned repos", self.text)

        match = re.search(r"Repo set \(all on `[^`]+`\): (.+?)\.\n", self.text, flags=re.DOTALL)
        self.assertIsNotNone(match, "could not find the 'Repo set (...)' inventory line")
        body = match.group(1).replace("\n", " ")
        entries = re.findall(r"[\w.\-]+\s*\(\d+(?:\s+files)?\)", body)
        self.assertEqual(len(entries), 17, f"expected 17 repo entries, found {len(entries)}: {entries}")

    def test_not_cloned_repos_called_out(self):
        for name in ("freellmapi", "revfactory"):
            self.assertIn(name, self.text)
        self.assertIn("**not cloned**", self.text)
        self.assertIn("Not cloned** in this environment", self.text)

    # ------------------------------------------------------------------
    # Phase 1 table structural integrity
    # ------------------------------------------------------------------

    def test_phase1_table_rows_have_consistent_column_count(self):
        start = self.text.index("| Claim | Doc says | Reality (verified) | Delta |")
        end = self.text.index("Repo set (all on")
        table_block = self.text[start:end]
        rows = [r for r in table_block.splitlines() if r.strip().startswith("|")]
        self.assertGreaterEqual(len(rows), 3, "expected header + separator + data rows")
        expected_pipes = rows[0].count("|")
        for row in rows:
            self.assertEqual(
                row.count("|"),
                expected_pipes,
                f"table row has inconsistent column count: {row!r}",
            )

    # ------------------------------------------------------------------
    # Cross-reference integrity: finding IDs mentioned in prose must
    # resolve to an actual bolded finding defined in Phase 2 (or be the
    # single documented P2-A/P2-B alias below).
    # ------------------------------------------------------------------

    def test_finding_ids_referenced_in_prose_resolve_to_phase2_definitions(self):
        phase2_start = self.text.index("## Phase 2 — Invariant findings")
        phase2_end = self.text.index("## Phase 4 — Top-3 fix proposals")
        phase2_block = self.text[phase2_start:phase2_end]

        defined_ids = set(re.findall(r"\*\*(P[0-2]-[A-Z])\s+—", phase2_block))
        self.assertEqual(defined_ids, {"P0-A", "P0-B", "P1-A", "P1-B", "P2-A"})

        prose_before_phase2 = self.text[:phase2_start]
        referenced_ids = set(re.findall(r"\bP[0-2]-[A-Z]\b", prose_before_phase2))

        # P2-B is a known, pre-existing alias/typo in the doc: the "Known
        # open blockers" section (§4.1) refers to "finding P2-B" for the
        # docker-compose mem_limit issue, but Phase 2 defines that same
        # issue as P2-A. This test locks in that *known* discrepancy so a
        # future edit that silently introduces a *new*, undocumented
        # dangling reference will still fail loudly.
        undefined_referenced_ids = referenced_ids - defined_ids
        self.assertEqual(undefined_referenced_ids, {"P2-B"})
        self.assertIn("finding P2-B", self.text)

    def test_p0_findings_referenced_as_top_priority(self):
        phase2_start = self.text.index("## Phase 2 — Invariant findings")
        phase2_block = self.text[phase2_start:]
        self.assertIn("**P0-A — `shell=True` command sink**", phase2_block)
        self.assertIn("**P0-B — `shell=True` command sink**", phase2_block)
        # The final reconciled priority order must rank the P0 sinks first.
        reconciled_priority_idx = self.text.index("Reconciled (priority order after live audit)")
        p0_mention_idx = self.text.index("kill the two P0 `shell=True` sinks")
        self.assertLess(reconciled_priority_idx, p0_mention_idx)
        self.assertIn("This outranks everything else.", self.text)

    # ------------------------------------------------------------------
    # Negative / regression case
    # ------------------------------------------------------------------

    def test_original_incorrect_claims_are_preserved_verbatim_not_deleted(self):
        # The doc explicitly says "Original prose is otherwise preserved" —
        # verify the superseded claims still exist in the body (so a
        # reader can see what was corrected), rather than being silently
        # rewritten in place.
        self.assertIn(
            "flagged already as P0 blocker. Not \"redundant\" but actively broken",
            self.text,
        )
        self.assertIn(
            '"missing 8 MCP server entries (April 2026 stack)"',
            self.text,
        )
        self.assertIn("Original prose is otherwise preserved.", self.text)

    def test_document_does_not_claim_single_monolithic_install_script(self):
        # Phase 1 explicitly refutes the original "12-phase, 1089 lines"
        # install.sh claim; make sure the refutation text is present and
        # unambiguous.
        self.assertIn(
            "**No single 1089-line/12-phase installer.**",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()