"""Static regression tests for the interactive demo page.

These guard the *structure* that makes the animated diagrams safe, without a
browser or any new dependency:

* cleanup-by-DOM-query (``clearDiagram`` clears ``.node`` / ``.edge`` under the
  diagram root) can only prevent stale highlights if every element a sequence
  lights actually lives inside that diagram's SVG and actually exists. A typo'd
  or moved id would make ``el(id)`` return null and silently leave the opposite
  path lit — the exact bug class we fixed.
* every ``data-play`` control must be wired to a handler.
* captured-transcript terminals must carry an evidence label, so no static
  example can be presented as a freshly executed command.

The policy semantics themselves are covered by test_simulator_policy.py.
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
HTML = (HERE.parent / "index.html").read_text(encoding="utf-8")
JS = (HERE.parent / "app.js").read_text(encoding="utf-8")


def _flow_sequences() -> dict[str, list[str]]:
    seqs = {}
    for name, body in re.findall(r"var (FLOW\d_(?:ALLOW|BLOCK)) = \[(.*?)\];", JS, re.DOTALL):
        seqs[name] = re.findall(r"\[\"([^\"]+)\",\s*\"([^\"]+)\"\]", body) and \
            [m[0] for m in re.findall(r"\[\"([^\"]+)\",\s*\"([^\"]+)\"\]", body)]
    return seqs


def _svg_block(root_id: str) -> str:
    m = re.search(r'<svg[^>]*id="%s".*?</svg>' % re.escape(root_id), HTML, re.DOTALL)
    assert m, f"SVG #{root_id} not found in index.html"
    return m.group(0)


def _ids_in(text: str) -> set[str]:
    return set(re.findall(r'id="([^"]+)"', text))


SEQS = _flow_sequences()
DIAGRAM_OF = {"FLOW1_ALLOW": "flow1", "FLOW1_BLOCK": "flow1",
              "FLOW3_ALLOW": "flow3", "FLOW3_BLOCK": "flow3"}


def test_all_four_flow_sequences_defined():
    assert set(SEQS) == {"FLOW1_ALLOW", "FLOW1_BLOCK", "FLOW3_ALLOW", "FLOW3_BLOCK"}


def test_every_lit_element_exists_in_its_diagram_svg():
    """Root-cause guard: any element a sequence lights must exist inside that
    diagram's SVG so clearDiagram's DOM query covers it (no stale opposite path)."""
    for name, ids in SEQS.items():
        root = DIAGRAM_OF[name]
        svg_ids = _ids_in(_svg_block(root))
        for eid in ids:
            assert eid in svg_ids, f"{name}: {eid} is not an element inside SVG #{root}"


def test_lit_elements_are_nodes_or_edges_of_the_diagram():
    """The element being lit must carry .node or .edge so the cleanup selector
    (root.querySelectorAll('.node, .edge')) actually reaches it."""
    for name, body in re.findall(r"var (FLOW\d_(?:ALLOW|BLOCK)) = \[(.*?)\];", JS, re.DOTALL):
        root = DIAGRAM_OF[name]
        block = _svg_block(root)
        for eid, _cls in re.findall(r'\["([^"]+)",\s*"([^"]+)"\]', body):
            # find this id's tag line and confirm it is a node or edge element
            m = re.search(r'(<[^>]*id="%s"[^>]*)' % re.escape(eid), block)
            assert m, f"{eid} tag not found in SVG #{root}"
            tag = m.group(1)
            assert re.search(r'class="[^"]*\b(node|edge)\b', tag), \
                f"{eid} is not a .node/.edge and would not be cleared: {tag.strip()}"


def test_cleanup_uses_dom_query_not_hand_list():
    assert re.search(r'querySelectorAll\("\.node, \.edge"\)', JS), \
        "clearDiagram must clear all nodes/edges via a DOM query"
    # playDiagram takes a diagram object with a root id, then clears that root.
    assert re.search(r"function playDiagram\(diagram\)\s*\{\s*\n?\s*clearDiagram\(diagram\.root\)", JS) \
        or re.search(r"clearDiagram\(diagram\.root\)", JS), \
        "playDiagram should clear by diagram root"


def test_every_data_play_button_is_wired():
    play_keys = set(re.findall(r'data-play="([^"]+)"', HTML))
    assert play_keys, "no data-play controls found"
    for key in play_keys:
        wired = re.search(r'["\']' + re.escape(key) + r'["\']\s*:', JS)
        assert wired, f"data-play={key!r} has no handler entry in app.js"


def test_terminal_panels_are_labelled_for_integrity():
    # Every terminal bar must tag its kind, so captured vs simulated is unambiguous.
    bars = re.findall(r'<div class="bar">.*?</div>', HTML, re.DOTALL)
    assert bars, "no terminal bars found"
    for bar in bars:
        assert 'class="t-tag"' in bar, "a terminal is missing an evidence/simulation tag"


def test_captured_transcript_terminals_start_with_idle_placeholder():
    # Prefill must be an idle placeholder, not the full transcript, so idle vs
    # played is distinguishable and captured output isn't shown as a live run.
    assert "to replay this static example (not a live run)" in JS
    assert not re.search(
        r'pre\.innerHTML = PLAY_TERMS\[k\]\.lines\.map', JS), \
        "captured terminals should not be prefilled with the full transcript on load"
