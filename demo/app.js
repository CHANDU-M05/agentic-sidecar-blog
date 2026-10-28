/* Agentic Sidecar — interactive visual companion
 * Vanilla JS only. No dependencies, no network. All scenario data comes from
 * the JSON island in index.html, which is validated against live 0.6.0 by
 * blog_posts/demo/tests/test_simulator_policy.py.
 */
(function () {
  "use strict";

  // ---- data -----------------------------------------------------------------
  var DATA = JSON.parse(document.getElementById("sim-data").textContent);
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var motionOff = reduce; // toggled by the Motion button

  function prefersStill() { return motionOff; }

  // ---- helpers --------------------------------------------------------------
  function el(id) { return document.getElementById(id); }
  function on(node, evt, fn) { node && node.addEventListener(evt, fn); }

  // ---- tabs -----------------------------------------------------------------
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".tab[role=tab]"));
  function selectTab(tab) {
    tabs.forEach(function (t) {
      var selected = t === tab;
      t.setAttribute("aria-selected", selected ? "true" : "false");
      var panel = el(t.getAttribute("aria-controls"));
      if (panel) panel.hidden = !selected;
    });
  }
  tabs.forEach(function (t, i) {
    on(t, "click", function () { selectTab(t); });
    on(t, "keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); tabs[(i + 1) % tabs.length].focus(); tabs[(i + 1) % tabs.length].click(); }
      if (e.key === "ArrowLeft") { e.preventDefault(); tabs[(i - 1 + tabs.length) % tabs.length].focus(); tabs[(i - 1 + tabs.length) % tabs.length].click(); }
    });
  });

  // ---- motion toggle --------------------------------------------------------
  var motionBtn = el("motion-toggle");
  on(motionBtn, "click", function () {
    motionOff = !motionOff;
    document.body.classList.toggle("reduce-motion", motionOff);
    motionBtn.textContent = "Motion: " + (motionOff ? "off" : "on");
    motionBtn.setAttribute("aria-pressed", motionOff ? "true" : "false");
  });
  if (reduce) {
    document.body.classList.add("reduce-motion");
    motionBtn.textContent = "Motion: off";
    motionBtn.setAttribute("aria-pressed", "true");
  }

  // ---- copy buttons ---------------------------------------------------------
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    on(btn, "click", function () {
      var term = btn.closest(".terminal");
      var pre = term && term.querySelector("pre");
      if (!pre) return;
      var text = pre.textContent;
      function done() { btn.textContent = "Copied"; setTimeout(function () { btn.textContent = "Copy"; }, 1400); }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { fallback(text); done(); });
      } else { fallback(text); done(); }
    });
  });
  function fallback(text) {
    var ta = document.createElement("textarea");
    ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(ta);
  }

  // ---- terminal line typer --------------------------------------------------
  function paintTerminal(pre, lines, animate) {
    pre.classList.remove("typing");
    if (!animate || prefersStill()) {
      pre.innerHTML = lines.map(function (l) { return '<div class="line">' + l + "</div>"; }).join("");
      return Promise.resolve();
    }
    pre.innerHTML = lines.map(function (l) { return '<div class="line">' + l + "</div>"; }).join("");
    pre.classList.add("typing");
    var rows = pre.querySelectorAll(".line");
    var i = 0;
    return new Promise(function (resolve) {
      (function next() {
        if (i >= rows.length) { pre.classList.remove("typing"); resolve(); return; }
        rows[i++].classList.add("show");
        setTimeout(next, 260);
      })();
    });
  }

  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  // ---- simulator ----------------------------------------------------------
  var scenarioGroup = el("scenario-group");
  var matrixBody = el("matrix-body");
  var current = DATA.scenarios[0];

  DATA.scenarios.forEach(function (s, i) {
    var lab = document.createElement("label");
    lab.innerHTML =
      '<input type="radio" name="scenario" value="' + s.id + '"' + (i === 0 ? " checked" : "") + ">" +
      '<span class="seg-item">' + esc(s.label) + "</span>";
    scenarioGroup.appendChild(lab);
    on(lab.querySelector("input"), "change", function () { current = s; resetRun(); });

    var tr = document.createElement("tr");
    var decCls = s.decision === "ALLOW" ? "allow" : "block";
    tr.innerHTML =
      "<td>" + esc(s.label) + "</td>" +
      '<td class="' + decCls + '">' + s.decision + "</td>" +
      "<td>" + (s.executesObserve ? "Yes — ran anyway" : "No") + "</td>" +
      "<td>" + (s.executesGovern ? "Yes" : "<strong>No — prevented</strong>") + "</td>";
    matrixBody.appendChild(tr);
  });

  function modeValue() {
    var m = document.querySelector('input[name="mode"]:checked');
    return m ? m.value : "observe";
  }

  // Build deterministic, evidence-faithful terminal lines for a scenario+mode.
  function buildLines(s, mode) {
    var L = [];
    L.push('<span class="t-dim">$ python src/customer_support_agent.py</span>  <span class="t-warn"># simulator</span>');
    L.push("User: " + esc(s.userRequest));
    if (s.decision === "BLOCK") {
      var tag = mode === "observe" ? "OBSERVE" : "GOVERN";
      L.push('<span class="t-block">[' + tag + "] BLOCK</span> tool=" + esc(s.tool) +
        " args=" + esc(s.argsRepr) + " risk=" + esc(s.risk) + " reason=" + esc(s.primaryReason));
    }
    var ran = mode === "observe" ? s.executesObserve : s.executesGovern;
    if (ran) {
      L.push('    <span class="t-exec">&gt;&gt;&gt; TOOL EXECUTED: ' + esc(s.execMarker) + "</span>");
      L.push("Final: Done. Tool result: " + esc(s.toolResult));
    } else {
      L.push('    <span class="t-block">&gt;&gt;&gt; TOOL NOT EXECUTED</span>');
      L.push('<span class="t-block">Execution stopped:</span> SidecarBlockedError: ' +
        esc(s.tool) + " was blocked before its body ran");
    }
    L.push("");
    L.push("Sidecar decisions:");
    L.push("  " + esc(s.tool) + ": <span class='" + (s.decision === "ALLOW" ? "t-allow" : "t-block") + "'>" +
      s.decision + "</span> | risk=" + esc(s.risk) + " | " + esc(s.decisionReason));
    return L;
  }

  var runBtn = el("run-btn"), resetBtn = el("reset-btn");
  var outDecision = el("out-decision"), outExec = el("out-exec"), outLayer = el("out-layer");
  var modeEcho = el("mode-echo"), timeline = el("timeline");
  var steps = Array.prototype.slice.call(timeline.querySelectorAll("li"));
  var simPre = document.querySelector('[data-terminal="sim"] .type-target');
  var runToken = 0;

  function setPill(node, cls, text) {
    node.className = "status " + cls; node.textContent = text;
  }
  function resetSteps() {
    steps.forEach(function (li) { li.classList.remove("current", "done", "blocked"); });
  }

  function resetRun() {
    var mode = modeValue();
    modeEcho.className = "status idle";
    modeEcho.textContent = (mode === "observe" ? "Observe" : "Govern") + " mode · " + current.label;
    setPill(outDecision, "idle", "—");
    setPill(outExec, "idle", "—");
    outLayer.textContent = "—";
    resetSteps();
    paintTerminal(simPre, ['<span class="t-dim"># select a scenario and press Run scenario</span>'], false);
  }

  function lightStep(i, state) {
    var li = steps[i];
    if (!li) return;
    li.classList.remove("current");
    if (state === "current") li.classList.add("current");
    else if (state === "done") li.classList.add("done");
    else if (state === "blocked") li.classList.add("blocked", "done");
  }

  function runSim() {
    var token = ++runToken;
    var mode = modeValue();
    var s = current;
    var ran = mode === "observe" ? s.executesObserve : s.executesGovern;
    resetSteps();
    setPill(outDecision, "idle", "…");
    setPill(outExec, "idle", "…");
    outLayer.textContent = "…";
    modeEcho.className = "status idle";
    modeEcho.textContent = (mode === "observe" ? "Observe" : "Govern") + " mode · " + s.label;

    var dwell = prefersStill() ? 0 : 480;
    var seq = [
      function () { lightStep(0, "current"); },
      function () { lightStep(0, "done"); lightStep(1, "current"); },
      function () { lightStep(1, "done"); lightStep(2, "current"); },
      function () { lightStep(2, "done"); lightStep(3, "current"); },
      function () {
        lightStep(3, "done");
        setPill(outDecision, s.decision === "ALLOW" ? "allow" : "block", s.decision);
        outLayer.textContent = s.matchedLayer + " · risk=" + s.risk;
        lightStep(4, "current");
      },
      function () {
        if (s.decision === "BLOCK" && !ran) lightStep(4, "blocked");
        else lightStep(4, "done");
        setPill(outExec, ran ? "ran" : "notran", ran ? "Tool ran" : "Prevented");
        lightStep(5, "current");
      },
      function () { lightStep(5, "done"); }
    ];

    var i = 0;
    (function tick() {
      if (token !== runToken) return;         // a newer run superseded this one
      if (i >= seq.length) { paintTerminal(simPre, buildLines(s, mode), !prefersStill()); return; }
      seq[i++]();
      setTimeout(tick, dwell);
    })();
  }

  on(runBtn, "click", runSim);
  on(resetBtn, "click", function () { runToken++; resetRun(); });
  document.querySelectorAll('input[name="mode"]').forEach(function (r) {
    on(r, "change", resetRun);
  });
  resetRun();

  // ---- animated diagrams ----------------------------------------------------
  // A step is [elementId, className]. Playing walks steps; still mode applies final classes.
  var FLOW1_ALLOW = [
    ["f1-user", "active"], ["e1a", "lit"], ["f1-agent", "active"], ["e1b", "lit"],
    ["f1-call", "active"], ["e1c", "lit"], ["f1-gate", "active"],
    ["e1d", "lit"], ["f1-decision", "active-allow"], ["e1e", "lit"], ["f1-run", "active-allow"]
  ];
  var FLOW1_BLOCK = [
    ["f1-user", "active"], ["e1a", "lit"], ["f1-agent", "active"], ["e1b", "lit"],
    ["f1-call", "active"], ["e1c", "lit"], ["f1-gate", "active"],
    ["e1f", "lit"], ["f1-stop", "active-block"]
  ];
  var FLOW3_ALLOW = [
    ["f3-agent", "active"], ["e3a", "lit"], ["f3-cond", "active"], ["e3b", "lit"],
    ["f3-toolnode", "active"], ["e3c", "lit"], ["f3-attach", "active"],
    ["e3d", "lit"], ["f3-run", "active-allow"], ["e3e", "lit"]
  ];
  var FLOW3_BLOCK = [
    ["f3-agent", "active"], ["e3a", "lit"], ["f3-cond", "active"], ["e3b", "lit"],
    ["f3-toolnode", "active"], ["e3c", "lit"], ["f3-attach", "active"],
    ["e3f", "lit"], ["f3-break", "active-block"]
  ];

  // Clear EVERY node and edge inside a diagram's SVG root. Because this walks the
  // live DOM (.node / .edge) rather than a hand-kept id list, switching between the
  // permitted and blocked play-throughs can never leave the opposite path lit.
  function clearDiagram(rootId) {
    var root = el(rootId);
    if (!root) return;
    root.querySelectorAll(".node, .edge").forEach(function (n) {
      n.classList.remove("active", "active-allow", "active-block", "lit");
    });
  }

  // diagram = { root: svgId, seq: [[elementId, className], ...] }
  function playDiagram(diagram) {
    clearDiagram(diagram.root);
    var seq = diagram.seq;
    if (prefersStill()) {
      seq.forEach(function (s) { el(s[0]) && el(s[0]).classList.add(s[1]); });
      return;
    }
    var i = 0;
    (function step() {
      if (i >= seq.length) return;
      var s = seq[i++];
      var n = el(s[0]);
      if (n) n.classList.add(s[1]);
      setTimeout(step, 420);
    })();
  }

  // ---- static (captured) transcripts ---------------------------------------
  var d = {};
  DATA.scenarios.forEach(function (s) { d[s.id] = s; });
  var read = d.read_order, del = d.delete_customer, ref750 = d.refund_750;

  var TERM_A1 = [
    '<span class="t-dim">$ python src/customer_support_agent.py</span>',
    "User: " + esc(read.userRequest),
    '    <span class="t-exec">&gt;&gt;&gt; TOOL EXECUTED: ' + esc(read.execMarker) + "</span>",
    "Final: Done. Tool result: " + esc(read.toolResult),
    "  <span class=\"t-allow\">read_order: ALLOW</span> | risk=LOW | " + esc(read.primaryReason),
    "",
    "User: " + esc(del.userRequest),
    '<span class="t-block">[GOVERN] BLOCK</span> tool=delete_customer ' + esc(del.argsRepr),
    '<span class="t-block">Execution stopped:</span> SidecarBlockedError: ' + esc(del.primaryReason),
    '  <span class="t-block">delete_customer: BLOCK</span> | risk=None | ' + esc(del.primaryReason),
    '    <span class="t-block">&gt;&gt;&gt; TOOL NOT EXECUTED</span>'
  ];
  var TERM_A3_ALLOW = buildLines(read, "govern");
  var TERM_A3_BLOCK = buildLines(del, "govern");

  var PLAY_TERMS = {
    "term-a1": { pre: '[data-terminal="a1"] .type-target', lines: TERM_A1 },
    "term-a3-allow": { pre: '[data-terminal="a3-allow"] .type-target', lines: TERM_A3_ALLOW },
    "term-a3-block": { pre: '[data-terminal="a3-block"] .type-target', lines: TERM_A3_BLOCK }
  };
  // Each captured transcript is bound to the SVG-less static terminals; playback is
  // a replay of captured evidence, never a live re-run. Diagram play keys carry the
  // diagram root so cleanup can clear all nodes/edges of that diagram.
  var PLAY_DIAGRAMS = {
    "flow1-allow": { root: "flow1", seq: FLOW1_ALLOW },
    "flow1-block": { root: "flow1", seq: FLOW1_BLOCK },
    "flow3-allow": { root: "flow3", seq: FLOW3_ALLOW },
    "flow3-block": { root: "flow3", seq: FLOW3_BLOCK }
  };

  document.querySelectorAll("[data-play]").forEach(function (btn) {
    on(btn, "click", function () {
      var key = btn.getAttribute("data-play");
      if (PLAY_DIAGRAMS[key]) playDiagram(PLAY_DIAGRAMS[key]);
      else if (PLAY_TERMS[key]) {
        var pre = document.querySelector(PLAY_TERMS[key].pre);
        paintTerminal(pre, PLAY_TERMS[key].lines, !prefersStill());
      }
    });
  });

  // Show an idle placeholder in the captured-transcript terminals until the reader
  // presses play, so an idle panel is visually distinct from a played one and no
  // captured evidence is presented as a freshly executed command.
  Object.keys(PLAY_TERMS).forEach(function (k) {
    var pre = document.querySelector(PLAY_TERMS[k].pre);
    if (pre) pre.innerHTML = '<div class="line"><span class="t-dim"># captured output \u2014 press \u25b6 to replay this static example (not a live run).</span></div>';
  });
})();
