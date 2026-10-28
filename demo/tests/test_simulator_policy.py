"""Validate the interactive simulator's truth table.

Source of truth: the JSON island in ``blog_posts/demo/index.html``
(``<script type="application/json" id="sim-data">``). Two levels of checking:

1. Always runs: internal-consistency assertions on the table (the exact refund
   ceiling behaviour, mode semantics, and the four required scenarios).
2. Runs when ``agentic-sidecar`` 0.6.0 is importable (e.g. from the internship
   project's virtualenv): re-derives every decision from the live library and
   asserts the table matches, so the demo cannot drift from verified behaviour.

No real refunds/deletions/network: the live checks use in-memory stub tools.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
HTML = HERE.parent / "index.html"


def load_data() -> dict:
    text = HTML.read_text(encoding="utf-8")
    m = re.search(
        r'<script type="application/json" id="sim-data">(.*?)</script>',
        text,
        re.DOTALL,
    )
    assert m, "sim-data JSON island not found in index.html"
    return json.loads(m.group(1))


DATA = load_data()
BY_ID = {s["id"]: s for s in DATA["scenarios"]}


# ── level 1: internal consistency (no external dependency) ──────────────────

def test_four_required_scenarios_present():
    assert set(BY_ID) == {"read_order", "refund_500", "refund_750", "delete_customer"}


def test_version_and_config_metadata():
    assert DATA["version"] == "0.6.0"
    assert DATA["failMode"] == "fail_closed"
    assert DATA["refundCeiling"] == 500
    assert DATA["riskBlockThreshold"] == "HIGH"
    assert DATA["layers"] == ["policy", "risk", "intent", "budget"]


def test_policy_outcomes_match_expected_table():
    assert BY_ID["read_order"]["decision"] == "ALLOW"
    assert BY_ID["refund_500"]["decision"] == "ALLOW"   # boundary is inclusive (lte)
    assert BY_ID["refund_750"]["decision"] == "BLOCK"
    assert BY_ID["delete_customer"]["decision"] == "BLOCK"


def test_risk_levels():
    assert BY_ID["read_order"]["risk"] == "LOW"
    assert BY_ID["refund_500"]["risk"] == "LOW"
    assert BY_ID["refund_750"]["risk"] == "HIGH"
    assert BY_ID["delete_customer"]["risk"] == "None"


def test_observe_never_prevents_execution():
    # Observe records the decision but the tool body still runs, for every scenario.
    for s in DATA["scenarios"]:
        assert s["executesObserve"] is True, s["id"]


def test_govern_blocks_only_the_blocked_calls():
    for s in DATA["scenarios"]:
        expected = s["decision"] == "ALLOW"
        assert s["executesGovern"] is expected, s["id"]


# ── level 2: re-derive from the live agentic-sidecar 0.6.0 library ────────────

def _build_sidecar(mode):
    from agentic_sidecar import Sidecar
    from agentic_sidecar.gate.policy import PolicyAdvisor
    from agentic_sidecar.gate.risk import RiskEvaluator
    from agentic_sidecar.gate.budget import BudgetGuardian
    from agentic_sidecar.intent.envelope import IntentEnvelope, Requester
    from agentic_sidecar.intent.alignment import IntentGuardian, ConstraintBinding

    policy = PolicyAdvisor.from_mapping({
        "default": "allow",
        "rules": [
            {"tool": "delete_*", "effect": "deny",
             "reason": "Destructive operations require sign-off"},
            {"tool": "read_*", "effect": "allow"},
        ],
    })
    risk = RiskEvaluator.from_mapping({
        "default": "LOW",
        "rules": [
            {"tool": "issue_refund", "arg_name": "amount",
             "arg_op": "gt", "arg_value": 500, "risk": "HIGH"},
            {"tool": "delete_*", "risk": "HIGH"},
            {"tool": "read_*", "risk": "LOW"},
        ],
    })
    budget = BudgetGuardian(max_cost=10.0, max_tokens=50_000)
    envelope = IntentEnvelope(
        goal="Provide customer support and issue authorized refunds",
        requested_by=Requester(type="human", id="customer-support-user"),
        constraints={"max_refund_amount": 500.0},
        authority={"can_issue_refund": True},
        expires=None,
    )
    bindings = [ConstraintBinding(
        constraint="max_refund_amount", tool="issue_refund",
        arg_name="amount", op="lte", severity="BLOCK",
        reason="Refund exceeds the user's authorized maximum of 500",
    )]
    intent = IntentGuardian(envelope=envelope, bindings=bindings)
    return Sidecar(
        on_sidecar_failure="fail_closed",
        policy=policy, risk=risk, intent=intent, budget=budget,
        mode=mode, risk_block_threshold="HIGH",
        roles=["policy", "risk", "intent_guardian", "budget"],
    )


def _live_run(scenario, mode):
    """Return (decision, risk, tool_ran) for a scenario under a mode, via the real lib."""
    from agentic_sidecar import SidecarBlockedError
    from agentic_sidecar.adapters.langgraph import attach

    executed = []
    tool = scenario["tool"]
    if tool == "read_order":
        def read_order(order_id: str) -> str:
            executed.append("read_order"); return "ok"
        fn, args = read_order, {"order_id": "ORD-123"}
    elif tool == "issue_refund":
        def issue_refund(order_id: str, amount: float) -> str:
            executed.append("issue_refund"); return "ok"
        fn, args = issue_refund, {"order_id": "ORD-123",
                                  "amount": 500.0 if scenario["id"] == "refund_500" else 750.0}
    else:
        def delete_customer(customer_id: str) -> str:
            executed.append("delete_customer"); return "ok"
        fn, args = delete_customer, {"customer_id": "CUS-123"}

    sidecar = _build_sidecar(mode)
    [governed] = attach(sidecar, [fn])
    try:
        governed(**args)
    except SidecarBlockedError:
        pass
    _ctx, dec = sidecar.decisions[0]
    return dec.status, str(dec.risk), executed == [tool]


try:
    import agentic_sidecar  # noqa: F401
    HAVE_LIB = True
except Exception:
    HAVE_LIB = False


@pytest.mark.skipif(
    not HAVE_LIB,
    reason="agentic-sidecar not importable; run inside the internship venv for live checks",
)
@pytest.mark.parametrize("mode,exec_key", [("observe", "executesObserve"),
                                            ("govern", "executesGovern")])
def test_table_matches_live_060_decisions(mode, exec_key):
    if agentic_sidecar.__dict__.get("__version__", "0.6.0") not in ("0.6.0", None):
        pytest.skip("live checks pinned to agentic-sidecar 0.6.0")
    for s in DATA["scenarios"]:
        decision, risk, ran = _live_run(s, mode)
        assert decision == s["decision"], (s["id"], mode, decision)
        assert risk == s["risk"], (s["id"], mode, risk)
        assert ran is s[exec_key], (s["id"], mode, ran)
