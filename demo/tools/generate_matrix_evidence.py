"""Reproducibly generate the Observe-vs-Govern decision matrix used by the
interactive simulator, against the SAME ruleset as
agentic-sidecar-internship/src/customer_support_agent.py.

Run it with the internship project's virtualenv (agentic-sidecar==0.6.0):

    ../agentic-sidecar-internship/.venv/bin/python \
        blog_posts/demo/tools/generate_matrix_evidence.py

Output is printed to stdout; the checked-in copy lives in
blog_posts/demo/evidence/observe_govern_matrix.txt. It is a simulation harness
over stub tools only — it never touches a real database, payment system, or
network.
"""
from __future__ import annotations

from agentic_sidecar import Sidecar, SidecarBlockedError
from agentic_sidecar.gate.policy import PolicyAdvisor
from agentic_sidecar.gate.risk import RiskEvaluator
from agentic_sidecar.gate.budget import BudgetGuardian
from agentic_sidecar.intent.envelope import IntentEnvelope, Requester
from agentic_sidecar.intent.alignment import IntentGuardian, ConstraintBinding
from agentic_sidecar.adapters.langgraph import attach


def make_sidecar(mode: str) -> Sidecar:
    """Identical to customer_support_agent.create_sidecar(), but mode-toggled."""
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


SCENARIOS = [
    ("read_order", "read_order", {"order_id": "ORD-123"}),
    ("refund_500", "issue_refund", {"order_id": "ORD-123", "amount": 500.0}),
    ("refund_750", "issue_refund", {"order_id": "ORD-123", "amount": 750.0}),
    ("delete_customer", "delete_customer", {"customer_id": "CUS-123"}),
]


def make_stub(tool_name: str, executed: list[str]):
    if tool_name == "read_order":
        def read_order(order_id: str) -> str:
            executed.append("read_order")
            return f"Order {order_id}: status=shipped, items=3"
        return read_order
    if tool_name == "issue_refund":
        def issue_refund(order_id: str, amount: float) -> str:
            executed.append("issue_refund")
            return f"Refund of {amount} issued for {order_id}"
        return issue_refund

    def delete_customer(customer_id: str) -> str:
        executed.append("delete_customer")
        return f"Customer {customer_id} deleted"
    return delete_customer


def main() -> None:
    for mode in ("observe", "govern"):
        print(f"==== MODE: {mode.upper()} ====")
        for label, tool_name, args in SCENARIOS:
            executed: list[str] = []
            sidecar = make_sidecar(mode)
            [governed] = attach(sidecar, [make_stub(tool_name, executed)])
            raised = None
            try:
                governed(**args)
            except SidecarBlockedError as exc:
                raised = exc.decision.status
            _ctx, dec = sidecar.decisions[0]
            ran = executed == [tool_name]
            print(f"scenario      = {label}")
            print(f"  tool        = {tool_name}  args={args}")
            print(f"  decision    = {dec.status}")
            print(f"  risk        = {dec.risk}")
            print(f"  reason      = {dec.reason}")
            print(f"  tool_ran    = {ran}")
            print(f"  raised      = {raised}")
            print()
        print()


if __name__ == "__main__":
    main()
