#!/usr/bin/env python3
"""Build three evidence-based blog articles as .docx.

Content is grounded strictly in the real agentic-sidecar-internship repo
(agentic-sidecar==0.6.0). Terminal/log excerpts are ACTUAL captured output;
latency was NOT benchmarked and the articles say so explicitly. No fabricated
bugs, benchmarks, or timings.
"""
from __future__ import annotations

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ASSETS = "/home/chandu/Projects/Work/deepagentlabs_internship/blog_posts/assets"
OUT = "/home/chandu/Projects/Work/deepagentlabs_internship/blog_posts"
AUTHOR = "Chandu"
DATE = "October 26, 2026"

NAVY = RGBColor(0x0F, 0x1C, 0x30)
GRAY = RGBColor(0x55, 0x55, 0x55)


# ── styling helpers ─────────────────────────────────────────────────────────

def shade(paragraph, fill="F3F5F9"):
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def add_code(doc, text, fill="F3F5F9", size=9):
    for line in text.split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.left_indent = Inches(0.12)
        shade(p, fill)
        r = p.add_run(line if line else " ")
        r.font.name = "Courier New"
        r.font.size = Pt(size)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Courier New")


def add_para(doc, text, size=11, bold=False, italic=False, color=None,
             space_after=8, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    if align:
        p.alignment = align
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    if color:
        r.font.color.rgb = color
    return p


def add_h(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.color.rgb = NAVY
    return h


def add_caption(doc, text):
    return add_para(doc, text, size=9, italic=True, color=GRAY,
                    align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)


def add_image(doc, path, width=6.2):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Inches(width))


def add_bullets(doc, items):
    for it in items:
        doc.add_paragraph(it, style="List Bullet")


def add_scenario_hook(doc, text):
    """A shaded, italic relatable-scenario opener above the introduction."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.left_indent = Inches(0.12)
    p.paragraph_format.right_indent = Inches(0.12)
    shade(p, "EEF3FF")
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    return p


def add_demo_pointer(doc):
    """Point readers to the self-contained interactive companion and be honest
    that .docx / dev.to Markdown cannot run its JavaScript."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.left_indent = Inches(0.12)
    shade(p, "F3F5F9")
    r1 = p.add_run("Interactive companion: ")
    r1.bold = True
    r1.font.size = Pt(10)
    r2 = p.add_run(
        "An animated, self-contained demo page accompanies this series "
        "(blog_posts/demo/index.html): the tool-boundary flow, the LangGraph loop, and "
        "an Observe-vs-Govern simulator whose truth table is checked against live "
        "agentic-sidecar 0.6.0 (blog_posts/demo/tests/test_simulator_policy.py). It is a "
        "simulation over stub tools \u2014 no real refunds, deletions, or network. This .docx "
        "cannot run its JavaScript; host the page and link or embed it via an <iframe>. "
        "The diagrams below are the static fallbacks; the animated versions live in the demo. "
        "See blog_posts/demo/README.md for hosting and embedding steps."
    )
    r2.font.size = Pt(10)
    r2.italic = True
    return p


def add_kv_block(doc, title, pairs):
    add_h(doc, title, level=2)
    for k, v in pairs:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(f"{k}: ")
        r1.bold = True
        r1.font.size = Pt(10)
        r2 = p.add_run(v)
        r2.font.size = Pt(10)


# ── shared reference list (v0.6.0 baseline) ───────────────────────────────────
REFS = [
    "Agentic Sidecar v0.6.0 on PyPI - https://pypi.org/project/agentic-sidecar/0.6.0/",
    "README.md at the v0.6.0 tag - https://github.com/DeepAgentLabs/agentic-sidecar/blob/v0.6.0/README.md",
    "Official repository - https://github.com/DeepAgentLabs/agentic-sidecar",
    "Internship implementation - https://github.com/CHANDU-M05/agentic-sidecar--internship",
    "Published Use Cases - https://deepagentlabs.io/agentic-sidecar/usecases/",
]


def add_refs(doc):
    add_h(doc, "References", level=2)
    for r in REFS:
        p = doc.add_paragraph(r, style="List Number")
        for run in p.runs:
            run.font.size = Pt(10)


def add_footer_note(doc):
    add_para(
        doc,
        "Version note: all API claims in this article target agentic-sidecar==0.6.0, "
        "the version pinned in the internship project's requirements.txt. Later "
        "features are not described as if they existed in that release.",
        size=9, italic=True, color=GRAY, space_after=4,
    )
    add_para(
        doc,
        "Evidence note: code excerpts are taken verbatim from the project source. "
        "Terminal excerpts are actual captured output (Python 3.14.8, pytest-9.1.1, "
        "agentic_sidecar 0.6.0). Latency and per-call overhead were not benchmarked "
        "and are not reported.",
        size=9, italic=True, color=GRAY,
    )


# ── real captured data ───────────────────────────────────────────────────────

SIDECAR_CONFIG = '''from agentic_sidecar import Sidecar
from agentic_sidecar.gate.policy import PolicyAdvisor
from agentic_sidecar.gate.risk import RiskEvaluator
from agentic_sidecar.gate.budget import BudgetGuardian

policy = PolicyAdvisor.from_mapping({
    "default": "allow",
    "rules": [
        {"tool": "delete_*", "effect": "deny",
         "reason": "Destructive operations require sign-off"},
        {"tool": "read_*",   "effect": "allow"},
    ],
})

risk = RiskEvaluator.from_mapping({
    "default": "LOW",
    "rules": [
        {"tool": "issue_refund", "arg_name": "amount",
         "arg_op": "gt", "arg_value": 500, "risk": "HIGH"},
        {"tool": "delete_*", "risk": "HIGH"},
        {"tool": "read_*",   "risk": "LOW"},
    ],
})

budget = BudgetGuardian(max_cost=10.0, max_tokens=50_000)

sidecar = Sidecar(
    on_sidecar_failure="fail_closed",   # never run ungoverned on internal error
    policy=policy, risk=risk, intent=intent_guardian, budget=budget,
    mode="govern", risk_block_threshold="HIGH",
    roles=["policy", "risk", "intent_guardian", "budget"],
)'''

GOVERN_LOG = '''SAFE ORDER LOOKUP  (read_order ORD-123)
  >>> TOOL EXECUTED: read_order(ORD-123)
  read_order: ALLOW | risk=LOW | Policy Advisor: Matched policy rule
              tool='read_*' -> effect=allow ...

AUTHORIZED REFUND  (issue_refund $250)
  >>> TOOL EXECUTED: issue_refund(ORD-123, amount=250.0)
  issue_refund: ALLOW | risk=LOW ...

OVERSIZED REFUND  (issue_refund $750)
  [GOVERN] BLOCK tool=issue_refund args={'order_id':'ORD-123','amount':750.0}
           risk=HIGH reason=Risk Evaluator: ... risk=HIGH (>= block 'HIGH')
  Execution stopped: SidecarBlockedError: Sidecar blocked 'issue_refund'(...)
  issue_refund: BLOCK | risk=HIGH ...        (tool did NOT execute)

DESTRUCTIVE ACTION  (delete_customer CUS-123)
  [GOVERN] BLOCK tool=delete_customer reason=Policy Advisor:
           Destructive operations require sign-off
  Execution stopped: SidecarBlockedError: Sidecar blocked 'delete_customer'(...)
  delete_customer: BLOCK | risk=None ...      (tool did NOT execute)'''

OBSERVE_LOG = '''MODE: OBSERVE
  Calling governed delete_customer(customer_id='CUS-123') ...
  [OBSERVE] BLOCK tool=delete_customer args={'customer_id':'CUS-123'}
            reason=Policy Advisor: Destructive operations require sign-off
      >>> TOOL EXECUTED: delete_customer
  Tool returned: 'customer CUS-123 deleted'
  Decisions recorded by sidecar (1):
    tool=delete_customer  status=BLOCK  risk=None'''

GOVERN_LOG2 = '''MODE: GOVERN
  Calling governed delete_customer(customer_id='CUS-123') ...
  [GOVERN] BLOCK tool=delete_customer args={'customer_id':'CUS-123'}
           reason=Policy Advisor: Destructive operations require sign-off
  SidecarBlockedError raised!
      Decision : BLOCK
      Reason   : Policy Advisor: Destructive operations require sign-off
      >>> TOOL NOT EXECUTED
  Decisions recorded by sidecar (1):
    tool=delete_customer  status=BLOCK  risk=None'''

PYTEST_OUT = '''$ pytest -v
platform linux -- Python 3.14.8, pytest-9.1.1, pluggy-1.6.0
collected 22 items

tests/test_budget_guardian.py::test_under_budget_is_allowed              PASSED
tests/test_budget_guardian.py::test_cost_limit_exceeded_pauses_for_escalation PASSED
tests/test_budget_guardian.py::test_token_limit_exceeded_pauses_for_escalation PASSED
tests/test_budget_guardian.py::test_govern_mode_does_not_stop_over_budget_tool PASSED
tests/test_customer_support_agent.py::test_safe_order_lookup_is_allowed    PASSED
tests/test_customer_support_agent.py::test_authorized_refund_is_allowed    PASSED
tests/test_customer_support_agent.py::test_oversized_refund_is_blocked     PASSED
tests/test_customer_support_agent.py::test_customer_deletion_is_blocked    PASSED
tests/test_intent_guardian.py::test_refund_below_limit_is_allowed          PASSED
tests/test_intent_guardian.py::test_refund_at_exact_limit_is_allowed       PASSED
tests/test_intent_guardian.py::test_refund_above_limit_is_blocked          PASSED
tests/test_intent_guardian.py::test_block_reason_is_from_binding           PASSED
tests/test_intent_guardian.py::test_intent_guardian_is_independent_of_policy PASSED
tests/test_intent_guardian.py::test_different_tool_is_not_constrained      PASSED
tests/test_observe_vs_govern.py::test_observe_mode_records_block_but_tool_still_executes PASSED
tests/test_observe_vs_govern.py::test_govern_mode_raises_and_tool_does_not_execute PASSED
tests/test_observe_vs_govern.py::test_govern_mode_allows_safe_tool         PASSED
tests/test_observe_vs_govern.py::test_observe_mode_decision_is_still_recorded PASSED
tests/test_sidecar_controls.py::test_safe_order_lookup_is_allowed          PASSED
tests/test_sidecar_controls.py::test_small_refund_is_allowed               PASSED
tests/test_sidecar_controls.py::test_large_refund_is_blocked               PASSED
tests/test_sidecar_controls.py::test_customer_deletion_is_blocked          PASSED

============================== 22 passed in 0.32s =============================='''

LANGGRAPH_SNIPPET = '''from agentic_sidecar.adapters.langgraph import attach
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph

# Plain functions know nothing about policy.
def read_order(order_id: str) -> str: ...
def issue_refund(order_id: str, amount: float) -> str: ...
def delete_customer(customer_id: str) -> str: ...

# Governance is applied outside the tool bodies.
governed_functions = attach(sidecar, [read_order, issue_refund, delete_customer])
governed_tools = [tool(fn) for fn in governed_functions]

tool_node = ToolNode(governed_tools)
graph = StateGraph(AgentState)
graph.add_node("agent", scripted_agent)      # deterministic, no LLM in tests
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition,
                            {"tools": "tools", "__end__": "__end__"})
graph.add_edge("tools", "agent")
app = graph.compile()'''


# ── article bodies ──────────────────────────────────────────────────────────

def article_1():
    doc = Document()
    add_image(doc, f"{ASSETS}/featured1.png", 6.4)
    h = doc.add_heading("Don't Trust the Prompt: Enforcing Policy at the Tool Boundary", level=0)
    for r in h.runs:
        r.font.color.rgb = NAVY
    add_para(doc, f"By {AUTHOR} · {DATE} · ~4 min read", size=10, color=GRAY,
             align=WD_ALIGN_PARAGRAPH.CENTER)

    add_scenario_hook(doc,
        "Scenario: a customer messages your support agent \u2014 \u201cThat order was a "
        "disaster. Refund me $750 and just delete my account.\u201d The agent is glad to "
        "help: it reaches for issue_refund(amount=750) and delete_customer. Nothing in "
        "the prompt objected. Here is what stopped both actions before they ever ran.")
    add_demo_pointer(doc)

    add_para(doc,
        "If you tell a language model \u201cplease never delete a customer,\u201d you are "
        "trusting a probabilistic system to obey a soft suggestion. Context "
        "compression, adversarial prompts, or plain model error can all route around "
        "that instruction. In the Agentic Sidecar customer-support project we moved "
        "enforcement away from the prompt and into the one place an action actually "
        "happens: the tool call.")

    add_h(doc, "The boundary idea", 1)
    add_para(doc,
        "The sidecar wraps each tool function. Before the real function runs, the "
        "call is evaluated against policy and a decision is recorded. If the "
        "decision blocks, execution is stopped before the side effect ever fires. "
        "The tool functions themselves stay clean \u2014 they contain no policy logic "
        "and never decide whether they are allowed to run.")

    add_h(doc, "Four independent governance layers", 1)
    add_para(doc,
        "A single tool call passes through four concerns, evaluated together:")
    add_bullets(doc, [
        "PolicyAdvisor \u2014 pattern rules over tool names. Here: default allow, "
        "read_* allow, and delete_* denied with a reason.",
        "RiskEvaluator \u2014 assigns risk. issue_refund with amount > 500 is HIGH; "
        "in govern mode HIGH meets the block threshold.",
        "IntentGuardian \u2014 a ConstraintBinding pins the intent envelope's "
        "max_refund_amount <= 500 to the issue_refund amount argument as a BLOCK.",
        "BudgetGuardian \u2014 ceilings of $10.00 cost and 50,000 tokens per the run.",
    ])
    add_code(doc, SIDECAR_CONFIG)

    add_h(doc, "Fail-closed by default", 1)
    add_para(doc,
        "Setting on_sidecar_failure to fail_closed means that if the governance "
        "machinery itself errors, the call is not allowed to proceed ungoverned. For "
        "destructive operations that is the only defensible default.")

    add_h(doc, "What it actually did", 1)
    add_para(doc,
        "Below is the real output of the LangGraph customer-support demo (actual "
        "captured log). Two calls run; two are stopped:")
    add_code(doc, GOVERN_LOG, fill="EEF1F6")
    add_para(doc,
        "Note that read_order and the $250 refund reach the tool (>>> TOOL "
        "EXECUTED), while the $750 refund and the customer deletion are blocked and "
        "the bodies never run. The precise reason is attached to each decision, so "
        "the audit trail explains itself.")

    add_h(doc, "Architecture at a glance", 1)
    add_image(doc, f"{ASSETS}/diagram1_policy_boundary.png", 6.0)
    add_caption(doc, "Figure 1 \u2014 Every tool call is intercepted at the attach() "
                     "boundary and evaluated by the four governance layers before dispatch.")

    add_h(doc, "Why this beats prompt-level rules", 1)
    add_bullets(doc, [
        "Consistent: the same rule fires regardless of what the model \u201cintended.\u201d",
        "Auditable: each call yields a structured decision with a reason.",
        "Decoupled: policy lives in config, not sprinkled through tool code.",
        "Testable: decisions are deterministic enough to assert in CI.",
    ])

    add_h(doc, "Two independent guards on one refund limit", 1)
    add_para(doc,
        "The $500 refund ceiling is enforced twice, by two layers that do not know "
        "about each other. The RiskEvaluator marks issue_refund with amount > 500 as "
        "HIGH, and because the sidecar runs with risk_block_threshold set to HIGH, "
        "that classification alone stops the call. Separately, the IntentGuardian "
        "carries a ConstraintBinding that pins the envelope's max_refund_amount (500.0) "
        "to the issue_refund amount argument with op set to lte and severity set to "
        "BLOCK. Either guard would block a $750 refund on its own. In the captured log "
        "the reported reason comes from the Risk Evaluator, but the intent binding is "
        "real defense in depth: loosening one rule does not silently open the door.")

    add_h(doc, "Every decision is a structured object", 1)
    add_para(doc,
        "After each call the sidecar exposes a list of (context, decision) pairs, and "
        "the demo prints tool name, status, risk, and reason for every one. That is "
        "what turns a blocked action into an explainable audit entry: not just that "
        "delete_customer was stopped, but that Policy Advisor denied it with the reason "
        "\u201cDestructive operations require sign-off.\u201d The same structure is what "
        "the tests assert against.")

    add_para(doc,
        "One caveat we will not hand-wave: we did not benchmark per-call latency "
        "or overhead for this project, so no performance numbers are claimed here.")

    add_footer_note(doc)
    add_refs(doc)
    add_kv_block(doc, "SEO metadata", [
        ("Title", "Don't Trust the Prompt: Enforcing Policy at the Tool Boundary (Agentic Sidecar)"),
        ("Meta description", "Move AI-agent safety from fragile prompt instructions to "
         "enforcement at the tool-call boundary. A Python + LangGraph example with "
         "policy, risk, intent and budget layers \u2014 plus real blocked-call logs."),
        ("Keywords", "AI agent governance, tool call policy, LangGraph, agentic-sidecar, "
         "LLM safety, runtime guardrails, fail closed"),
        ("Slug", "enforcing-policy-at-the-tool-boundary-agentic-sidecar"),
        ("Author", AUTHOR), ("Date", DATE),
        ("Category", "AI Engineering / Agent Governance"),
        ("Tags", "agentic-sidecar, policy, langgraph, guardrails, python"),
        ("Featured image", "featured1_policy_boundary"),
    ])
    return doc


def article_2():
    doc = Document()
    add_image(doc, f"{ASSETS}/featured2.png", 6.4)
    h = doc.add_heading("Observe vs Govern: Recording a BLOCK Isn't Preventing It", level=0)
    for r in h.runs:
        r.font.color.rgb = NAVY
    add_para(doc, f"By {AUTHOR} · {DATE} · ~4 min read", size=10, color=GRAY,
             align=WD_ALIGN_PARAGRAPH.CENTER)

    add_scenario_hook(doc,
        "Scenario: your dashboard shows a wall of green BLOCK entries, so the team "
        "believes the destructive call was stopped. Scroll three lines and it reads "
        ">>> TOOL EXECUTED. The BLOCK was only recorded. This article is about the one "
        "flag that turns a recorded BLOCK into a prevented one.")
    add_demo_pointer(doc)

    add_para(doc,
        "The most useful thing a governance layer can do early on is nothing. In "
        "the Agentic Sidecar, setting mode to observe evaluates every call and records "
        "the decision, but it does not stop the tool. Setting mode to govern enforces "
        "the decision and prevents the call. Knowing the difference is what lets you "
        "roll governance out gradually instead of flipping a risky switch on day one.")

    add_h(doc, "Where the enforcement actually lives", 1)
    add_para(doc,
        "A subtlety we confirmed by reading the source: Sidecar.evaluate() never "
        "raises. It only produces and records a decision. SidecarBlockedError is "
        "raised by the LangGraph adapter's attach() wrapper, which inspects "
        "decision.status and sidecar.mode after evaluate() returns. So to see "
        "enforce-vs-observe you must call the wrapped tool, not evaluate() directly.")

    add_h(doc, "The same blocked call, both modes", 1)
    add_para(doc, "Real output \u2014 OBSERVE mode. The decision is BLOCK, yet the tool "
                  "still runs:")
    add_code(doc, OBSERVE_LOG, fill="EEF1F6")
    add_para(doc, "Real output \u2014 GOVERN mode. The wrapper raises and the tool never "
                  "executes:")
    add_code(doc, GOVERN_LOG2, fill="EEF1F6")

    add_h(doc, "Reading the contrast", 1)
    add_bullets(doc, [
        "Observe: the tool returned 'customer CUS-123 deleted' \u2014 the side effect "
        "happened; you have a log entry telling you it SHOULD have been blocked.",
        "Govern: '>>> TOOL NOT EXECUTED' \u2014 the deletion never fired, and the "
        "exception carries the same BLOCK decision and reason.",
        "In both modes the decision count is identical (1 recorded). Only enforcement "
        "differs.",
    ])

    add_h(doc, "What the wrapper actually does in each mode", 1)
    add_para(doc,
        "Both modes run the identical evaluate() step and record the identical "
        "decision; the divergence is one branch in the wrapper around your function. "
        "In observe mode the wrapper writes the [OBSERVE] line and then falls through "
        "to call the real tool. In govern mode the same wrapper sees decision.status "
        "of BLOCK plus mode=govern and raises SidecarBlockedError before it ever "
        "invokes the tool body \u2014 which is exactly why the governed log ends at "
        ">>> TOOL NOT EXECUTED instead of a return value. One evaluation, one record, "
        "two outcomes decided by a single flag.")

    add_h(doc, "Architecture at a glance", 1)
    add_image(doc, f"{ASSETS}/diagram2_observe_govern.png", 5.4)
    add_caption(doc, "Figure 2 \u2014 evaluate() records; the mode flag decides whether "
                     "attach() merely logs (observe) or raises to block (govern).")

    add_h(doc, "A rollout path this enables", 1)
    add_para(doc,
        "Start in observe mode in production: you measure how often your policy "
        "would have blocked, and catch misconfigured rules, without breaking "
        "legitimate flows. When the recorded BLOCK decisions match what you truly "
        "want stopped, switch the sidecar to govern mode and enforcement turns on \u2014 "
        "the same BLOCK decisions, now prevented.")

    add_h(doc, "How we know both modes work", 1)
    add_para(doc,
        "It is covered directly by automated tests, not just claimed. The suite "
        "includes test_observe_mode_records_block_but_tool_still_executes and "
        "test_govern_mode_raises_and_tool_does_not_execute (among others), and the "
        "full run is 22/22 passing \u2014 see Article 3 for the complete output.")

    add_h(doc, "The same shape shows up with budgets", 1)
    add_para(doc,
        "Govern mode is not a blanket wall; it enforces one status. The budget "
        "guardian configured for the demo (max_cost 10.0, max_tokens 50,000) returns "
        "PAUSE with escalation_required set when either ceiling is reached, and never "
        "BLOCK. attach() raises SidecarBlockedError only for BLOCK, so at 0.6.0 an "
        "over-budget call is recorded as PAUSE and the tool runs anyway \u2014 in govern "
        "mode. Registering @sidecar.on_escalation_required does not rescue it: at this "
        "version the hook is stored and never invoked. Stopping on cost means checking "
        "decision.escalation_required in your own code. Four tests in "
        "test_budget_guardian.py pin this down, including the one asserting the tool "
        "still executes.")

    add_para(doc,
        "Later releases close this gap. agentic-sidecar 0.6.1 introduces "
        "Sidecar.enforce(): PAUSE and ESCALATE route through a registered escalation "
        "handler and, with none registered, raise SidecarSuspendedError before the "
        "tool is dispatched (0.8.1 keeps that behaviour). That makes the upgrade more "
        "than a version bump \u2014 code that only catches SidecarBlockedError now has "
        "to handle SidecarSuspendedError too.")

    add_h(doc, "The mistake this distinction is meant to prevent", 1)
    add_para(doc,
        "Read the observe-mode log again: the sidecar records status BLOCK for "
        "delete_customer, and then the very next line reads >>> TOOL EXECUTED with "
        "the tool returning 'customer CUS-123 deleted'. A team that only glances at "
        "the decision stream can convince itself they are protected, because the "
        "block is right there in the log. They are not \u2014 observe mode is a "
        "measurement instrument, not a wall. Treat a stream of observe-mode BLOCK "
        "entries as evidence that you still need to flip the switch to govern.")

    add_h(doc, "Switching modes changes exactly one field", 1)
    add_para(doc,
        "Both runs in the demo share the same policy, risk, intent, budget, roles, "
        "and risk_block_threshold. The only thing that differs is mode. That is the "
        "point: you build confidence in the decisions first, in observe mode, and "
        "when the recorded decisions match what you actually want stopped you change "
        "one setting and the same decisions become enforcement \u2014 no policy rewrite, "
        "no re-testing of the rules themselves.")

    add_para(doc,
        "As with the first article: no latency or overhead figures are reported "
        "because we did not benchmark them.")

    add_footer_note(doc)
    add_refs(doc)
    add_kv_block(doc, "SEO metadata", [
        ("Title", "Observe vs Govern Modes in Agentic Sidecar: Logging a BLOCK vs Preventing It"),
        ("Meta description", "Why recording a BLOCK is not the same as preventing an "
         "action. A Python example showing agentic-sidecar observe mode (shadow logging) "
         "vs govern mode (SidecarBlockedError), with real captured logs."),
        ("Keywords", "agentic-sidecar, observe mode, govern mode, SidecarBlockedError, "
         "agent enforcement, shadow rollout, LangGraph adapter"),
        ("Slug", "observe-vs-govern-agentic-sidecar"),
        ("Author", AUTHOR), ("Date", DATE),
        ("Category", "AI Engineering / Agent Governance"),
        ("Tags", "agentic-sidecar, modes, enforcement, langgraph, python"),
        ("Featured image", "featured2_observe_vs_govern"),
    ])
    return doc


def article_3():
    doc = Document()
    add_image(doc, f"{ASSETS}/featured3.png", 6.4)
    h = doc.add_heading("Wiring Governance Into a LangGraph Agent Without Touching the Tools", level=0)
    for r in h.runs:
        r.font.color.rgb = NAVY
    add_para(doc, f"By {AUTHOR} · {DATE} · ~5 min read", size=10, color=GRAY,
             align=WD_ALIGN_PARAGRAPH.CENTER)

    add_scenario_hook(doc,
        "Scenario: your LangGraph support agent already works in production, and "
        "security wants runtime governance added this sprint \u2014 without rewriting the "
        "business tools or breaking the agent \u2192 tools \u2192 agent loop. This article is the "
        "one-seam way to do it.")
    add_demo_pointer(doc)

    add_para(doc,
        "The easiest mistake in agent governance is threading policy through every "
        "tool: if-statements, decorators, and checks scattered across business code. "
        "We kept the opposite boundary in this project \u2014 plain tool functions that "
        "know nothing about rules, and a governance layer attached from the outside.")

    add_h(doc, "The integration pattern", 1)
    add_para(doc,
        "attach(sidecar, [read_order, issue_refund, delete_customer]) returns "
        "governed wrapper functions. We convert those into LangChain tools, drop them "
        "in a ToolNode, and run the usual agent/tools StateGraph. The policy config "
        "and the tool bodies never see each other.")
    add_code(doc, LANGGRAPH_SNIPPET)

    add_h(doc, "Deterministic agent, reproducible tests", 1)
    add_para(doc,
        "For tests we swap the language model for a small scripted agent that "
        "proposes a fixed tool call based on the user's words (for example a message "
        "containing 750 triggers a large refund, and delete triggers deletion). No API "
        "key, no network, no flakiness. The tools print a marker when they run, so a "
        "test can distinguish an allowed-and-executed call from a blocked-and-never-"
        "dispatched one.")
    add_para(doc,
        "The scripted agent also settles the loop cleanly. It inspects the last "
        "message: if it is a ToolMessage the tool already ran, so it emits a final "
        "text reply instead of re-proposing the same call. The source docstring is "
        "explicit that this avoids the infinite agent \u2192 tools \u2192 agent cycle "
        "that happens when an agent keeps reading the original request. Governance and "
        "graph-shape are thus both exercised on every run, deterministically.")

    add_h(doc, "Real test evidence", 1)
    add_para(doc,
        "This is the actual pytest run for the project (Python 3.14.8, "
        "agentic_sidecar 0.6.0, pytest-9.1.1): 22 passed in 0.32s. It covers allowed "
        "reads and refunds, blocked oversized refunds and deletions, the intent "
        "boundary at the exact limit, both observe and govern modes, and the budget "
        "ceilings:")
    add_code(doc, PYTEST_OUT, fill="EEF1F6")

    add_h(doc, "Architecture at a glance", 1)
    add_image(doc, f"{ASSETS}/diagram3_langgraph.png", 6.4)
    add_caption(doc, "Figure 3 \u2014 Plain functions are wrapped by attach(), exposed as "
                     "governed tools, and used inside the LangGraph agent/tools loop.")

    add_h(doc, "One seam, four roles", 1)
    add_para(doc,
        "The sidecar is built with a roles list of policy, risk, intent_guardian, and "
        "budget, so a single attach() point runs every call through all four gates. The "
        "fourth, BudgetGuardian, is configured with a max_cost of 10.0 and a max_tokens "
        "of 50,000 for the run. None of the demo scenarios trips that ceiling \u2014 the "
        "refund and delete blocks come from policy and risk \u2014 so budget is covered "
        "by its own tests rather than by the demo. The point of the seam is that adding "
        "that fourth concern required no change to the tool functions at all.")

    add_para(doc,
        "Those tests turned up something worth stating plainly. At 0.6.0 the Budget "
        "Guardian returns PAUSE with escalation_required set once either ceiling is "
        "reached, and never BLOCK. attach() raises SidecarBlockedError only for BLOCK, "
        "so the PAUSE verdict is recorded and the over-budget tool still runs \u2014 in "
        "govern mode. Registering @sidecar.on_escalation_required does not change "
        "that: at this version the hook is stored and never invoked, so stopping on "
        "cost means checking decision.escalation_required in your own code. Budget is "
        "wired in and observable here, not enforcing on its own.")

    add_h(doc, "What this buys you", 1)
    add_bullets(doc, [
        "Separation: changing a refund limit is a config edit, not a tool rewrite.",
        "Portability: the same sidecar governs the same tools with or without LangGraph.",
        "Confidence: a deterministic harness means 22 assertions actually exercise "
        "both modes and every threshold edge.",
    ])

    add_h(doc, "How the 22 tests are organized", 1)
    add_para(doc,
        "The suite is split across five files, each checking a different layer so a "
        "failure points at the right place: test_sidecar_controls.py exercises the "
        "Sidecar directly (safe read allowed, small refund allowed, large refund "
        "blocked, deletion blocked); test_customer_support_agent.py drives the full "
        "compiled LangGraph graph end to end; test_intent_guardian.py probes the "
        "refund boundary including the exact-limit case (test_refund_at_exact_limit_is_allowed) "
        "and confirms the intent guardian blocks independently of policy; "
        "test_observe_vs_govern.py is the two-mode proof covered in Article 2; and "
        "test_budget_guardian.py pins the budget behavior above, including the test "
        "that asserts an over-budget tool still executes in govern mode. Because "
        "the graph itself is tested, the boundary behavior is asserted with the real "
        "ToolNode and tools_condition, not a mock.")

    add_para(doc,
        "We did not measure the runtime overhead of the wrapper graph, so no latency "
        "figure is claimed; the honest statement is that governance cost was not "
        "benchmarked in this project.")

    add_footer_note(doc)
    add_refs(doc)
    add_kv_block(doc, "SEO metadata", [
        ("Title", "Integrating agentic-sidecar Governance with a LangGraph Agent (Python)"),
        ("Meta description", "Attach runtime governance to a LangGraph agent by wrapping "
         "plain tool functions with attach() \u2014 keeping policy out of tool code \u2014 "
         "plus a deterministic 22-test suite. Real pytest output included."),
        ("Keywords", "LangGraph, agentic-sidecar, agent governance, python, ToolNode, "
         "attach adapter, deterministic testing, pytest"),
        ("Slug", "langgraph-agent-governance-agentic-sidecar"),
        ("Author", AUTHOR), ("Date", DATE),
        ("Category", "AI Engineering / Agent Governance"),
        ("Tags", "agentic-sidecar, langgraph, testing, python, integration"),
        ("Featured image", "featured3_langgraph_integration"),
    ])
    return doc


def main():
    jobs = [
        ("article_1_policy_at_tool_boundary.docx", article_1),
        ("article_2_observe_vs_govern.docx", article_2),
        ("article_3_langgraph_integration.docx", article_3),
    ]
    for name, fn in jobs:
        doc = fn()
        path = f"{OUT}/{name}"
        doc.save(path)
        print(f"saved {path}")


if __name__ == "__main__":
    main()
