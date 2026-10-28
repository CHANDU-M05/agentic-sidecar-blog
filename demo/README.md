# Interactive Visual Companion — Agentic Sidecar articles

A **self-contained**, animated web page that accompanies the three Agentic
Sidecar engineering articles:

1. **Don't Trust the Prompt: Enforcing Policy at the Tool Boundary**
2. **Observe vs Govern: Recording a BLOCK Isn't Preventing It** (interactive simulator)
3. **Wiring Governance Into a LangGraph Agent Without Touching the Tools**

It is plain HTML + CSS + vanilla JS. No framework, no build step, no network,
no API keys. Everything technical is grounded in **agentic-sidecar 0.6.0** and
the internship project's verified behaviour.

> ⚠️ **This is a simulation.** The simulator runs deterministic logic derived
> from the verified 0.6.0 policy over stub tools. It never issues a real refund,
> deletes any record, or makes an external call.

---

## What's in this folder

```
blog_posts/demo/
├── index.html                        # the page + the simulator truth-table (JSON island)
├── styles.css                         # shared design system (ALLOW/BLOCK/PAUSE, terminal, animations)
├── app.js                             # tabs, simulator, timeline + diagram animation, copy buttons
├── README.md                          # this file
├── evidence/
│   └── observe_govern_matrix.txt      # LIVE 0.6.0 output backing every scenario x mode outcome
├── tools/
│   └── generate_matrix_evidence.py    # regenerates the matrix evidence (run in internship venv)
└── tests/
    └── test_simulator_policy.py       # validates the truth table, incl. against live 0.6.0
```

---

## Run / preview locally

The page uses only inline data and relative `<link>`/`<script>` files, so it
works straight from disk **and** over HTTP.

Open directly:

```bash
# from this folder
xdg-open index.html          # Linux
# open blog_posts/demo/index.html in a browser on macOS/Windows
```

Or serve the folder (recommended — matches how it will be hosted):

```bash
cd blog_posts/demo
python3 -m http.server 8080
# visit http://localhost:8080
```

### Feature checklist

- **Tabs** switch between the three articles (arrow keys also work).
- **Tab 1 / Tab 3** — "Play permitted call" / "Play blocked call" animate the
  architecture diagram; the green path runs the tool, the red path stops it.
  "Replay transcript" types out a terminal panel line by line.
- **Tab 2** — the Observe vs Govern **simulator**: pick a mode, pick a scenario,
  press **Run scenario**. Watch the decision pill, the tool-execution pill, the
  6-step timeline, the simulated terminal, and the outcome matrix. **Reset**
  clears it for another run.
- **Motion: on/off** in the tab bar (and OS `prefers-reduced-motion`) disables
  animation; every diagram has a written static reading as a fallback.
- **Copy** buttons copy any terminal panel.

---

## Publish / embed

Neither the `.docx` articles nor Markdown-only platforms (e.g. dev.to) can
execute JavaScript, so the interactive layer lives here as a separate page that
the articles **link to** or **embed**.

- **Link it** (works everywhere): host this folder (GitHub Pages, Netlify, any
  static host) and add the URL where each article's "Interactive companion"
  callout points.
- **Embed it** (platforms that allow an `<iframe>`, e.g. a personal site):

  ```html
  <iframe src="https://YOUR-HOST/agentic-sidecar-demo/index.html"
          title="Agentic Sidecar — interactive visual companion"
          loading="lazy" style="width:100%;height:900px;border:0;border-radius:14px"></iframe>
  ```

- **GitHub Pages**: copy `index.html`, `styles.css`, `app.js` into a directory
  on a `gh-pages` branch (or a `/docs` folder) and enable Pages. The page has no
  external asset dependencies, so no build pipeline is required.
- **dev.to**: paste the captured logs / static figures as you already do, and add
  a link to the hosted demo. Do **not** claim the interactive simulator runs
  inline — it does not on dev.to.

The three **static PNG diagrams** (`blog_posts/assets/diagram1..3.png`) remain
the embedded figures for the documents; the **animated** versions live in this
page.

---

## Verifying the accuracy

The simulator's truth table is the `<script type="application/json" id="sim-data">`
island in `index.html`. It is validated two ways by
`tests/test_simulator_policy.py`:

1. Internal consistency (runs anywhere): refund of exactly **500 → ALLOW**
   (inclusive `lte` boundary), **750 → BLOCK**, `delete_customer → BLOCK`,
   `read_order → ALLOW`; observe never prevents execution; govern prevents only
   the blocked calls.
2. **Against live agentic-sidecar 0.6.0** (runs inside the internship venv): it
   rebuilds the demo's Sidecar and re-derives every decision, risk, and
   executed/not-executed outcome for all four scenarios in both modes, then
   asserts the table matches.

```bash
# from the repo root — uses the internship venv that pins agentic-sidecar==0.6.0
agentic-sidecar-internship/.venv/bin/python -m pytest \
    blog_posts/demo/tests/test_simulator_policy.py -v
# 8 passed  (6 consistency + 2 live matrix checks)
```

Regenerate the captured evidence any time:

```bash
agentic-sidecar-internship/.venv/bin/python \
    blog_posts/demo/tools/generate_matrix_evidence.py \
    > blog_posts/demo/evidence/observe_govern_matrix.txt
```

The internship project's own suite is unchanged and still green:

```bash
cd agentic-sidecar-internship && .venv/bin/python -m pytest -q   # 22 passed
```

---

## Verified facts vs simulated output

- **Verified / captured:** `evidence/observe_govern_matrix.txt` and the
  internship `evidence/demo_output.txt` are real `0.6.0` output. Panels tagged
  **real captured output** reproduce them.
- **Simulated:** the simulator's per-scenario terminal is assembled
  deterministically from those verified decisions and tagged **simulated**. The
  $500-exact scenario in Govern mode is verified live but was not part of the
  original four-case `demo_output.txt` capture (that capture used $250); the
  boundary is covered by `test_refund_at_exact_limit_is_allowed` and by the live
  matrix check here.
- **Not claimed:** no latency/throughput benchmarks, no production deployment,
  and no real side effects. Budget `PAUSE` is intentionally excluded from the
  simulator's ALLOW/BLOCK enforcement view because, at 0.6.0, `PAUSE` is recorded
  but **not** enforced by the adapter (see the in-page note).
