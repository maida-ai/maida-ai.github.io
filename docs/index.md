---
title: Maida documentation
description: Install Maida, inspect agent trajectories, capture behavioral baselines, and block regressions before merge.
html_theme.sidebar_secondary.remove: true
---

```{toctree}
:hidden:
:maxdepth: 2

getting-started
guides/index
integrations
reference/index
```

<div class="docs-hero__eyebrow">Maida documentation</div>

# Catch agent changes before merge.

<div class="docs-hero">
  <div class="docs-hero__copy">
    <p class="docs-hero__intro">Record how an agent runs, compare it with a reviewed baseline, and block structural regressions inside CI.</p>
  </div>
  <div class="docs-quickstart" aria-label="Maida sixty-second quickstart and behavioral trajectory">
    <div class="docs-quickstart__bar">
      <span>60 second quickstart</span>
      <span class="docs-quickstart__status">local · no keys</span>
    </div>
    <pre><code>uv tool install "maida-ai>=0.5"
maida demo
maida view
maida demo --regression</code></pre>
    <svg class="docs-trajectory" viewBox="0 0 560 142" role="img" aria-label="A healthy baseline path and a pull request path that diverges through repeated search calls and a new CRM tool">
      <path class="docs-trajectory__path docs-trajectory__path--pass" d="M20 36H138L208 36H318L388 36H538" />
      <path class="docs-trajectory__path" d="M20 106H138L208 106" />
      <path class="docs-trajectory__path docs-trajectory__path--change" d="M208 106H270C298 106 298 72 326 72H388C416 72 416 106 444 106H538" />
      <circle class="docs-trajectory__node" cx="138" cy="36" r="7" />
      <circle class="docs-trajectory__node" cx="318" cy="36" r="7" />
      <circle class="docs-trajectory__node" cx="138" cy="106" r="7" />
      <circle class="docs-trajectory__node docs-trajectory__node--change" cx="326" cy="72" r="7" />
      <circle class="docs-trajectory__node docs-trajectory__node--change" cx="444" cy="106" r="7" />
      <text x="18" y="22">MAIN</text>
      <text x="18" y="92">PR</text>
      <text x="116" y="59">agent</text>
      <text x="286" y="59">lookup</text>
      <text x="298" y="94">search ×3</text>
      <text x="416" y="130">CRM new</text>
      <text x="505" y="22">answer</text>
      <text x="505" y="92">answer</text>
    </svg>
  </div>
</div>

<div class="docs-section-label">Start with a task</div>
<div class="docs-task-list">
  <a class="docs-task" href="getting-started/">
    <span class="docs-task__label">First run</span>
    <span class="docs-task__title">Try Maida in 60 seconds</span>
    <span class="docs-task__description">Run a deterministic agent and inspect its execution timeline.</span>
    <span class="docs-task__arrow" aria-hidden="true">→</span>
  </a>
  <a class="docs-task" href="regression-testing/">
    <span class="docs-task__label">CI gate</span>
    <span class="docs-task__title">Gate a pull request</span>
    <span class="docs-task__description">Capture a reviewed baseline and fail CI when behavior regresses.</span>
    <span class="docs-task__arrow" aria-hidden="true">→</span>
  </a>
  <a class="docs-task" href="getting-started/#quickstart">
    <span class="docs-task__label">Instrument</span>
    <span class="docs-task__title">Trace your agent</span>
    <span class="docs-task__description">Add Maida to a Python entrypoint with a small, framework-neutral SDK.</span>
    <span class="docs-task__arrow" aria-hidden="true">→</span>
  </a>
  <a class="docs-task" href="integrations/">
    <span class="docs-task__label">Adapters</span>
    <span class="docs-task__title">Connect your framework</span>
    <span class="docs-task__description">Capture LangChain, LangGraph, OpenAI Agents, CrewAI, or Langfuse activity.</span>
    <span class="docs-task__arrow" aria-hidden="true">→</span>
  </a>
  <a class="docs-task" href="viewer/">
    <span class="docs-task__label">Evidence</span>
    <span class="docs-task__title">Inspect a run</span>
    <span class="docs-task__description">Follow the tool path, timing, loops, warnings, and errors locally.</span>
    <span class="docs-task__arrow" aria-hidden="true">→</span>
  </a>
</div>

## Find the exact interface

<div class="docs-reference-columns">
  <div class="docs-reference-group">
    <h3><a href="cli/">CLI reference</a></h3>
    <p>Every command, option, output shape, and exit code.</p>
  </div>
  <div class="docs-reference-group">
    <h3><a href="sdk/">SDK reference</a></h3>
    <p>Tracing contexts and event recorders for Python agents.</p>
  </div>
  <div class="docs-reference-group">
    <h3><a href="reference/policy/">Policy v2</a></h3>
    <p>Define acceptable structural behavior as code.</p>
  </div>
  <div class="docs-reference-group">
    <h3><a href="reference/trace-format/">Trace format</a></h3>
    <p>The versioned OTel-compatible data contract.</p>
  </div>
  <div class="docs-reference-group">
    <h3><a href="reference/trace-emitter/">External emitter guide</a></h3>
    <p>Produce native Maida traces without the Python SDK.</p>
  </div>
  <div class="docs-reference-group">
    <h3><a href="reference/config/">Configuration</a></h3>
    <p>Environment variables, YAML precedence, and safe local storage.</p>
  </div>
</div>
