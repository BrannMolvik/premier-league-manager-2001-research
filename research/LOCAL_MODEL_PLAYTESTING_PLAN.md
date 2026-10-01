# Local-model playtesting and low-cost analysis plan

_Date: 1 October 2026 KST_

## Purpose

After the original-faithful reconstruction is stable enough for broader
playtesting, use Daniel's local Ollama coding model as a subordinate analyst to
reduce hosted Codex usage on repetitive, bounded work.

Known local model:

- Ollama
- `qwen2.5-coder:14b`

The local model is **not** an authority for original FM2001 behavior. Native
behavior, fidelity claims, and reverse-engineered semantics still require direct
source evidence and higher-confidence adjudication.

## Good local-model tasks

Prefer the local model for mechanical work with explicit inputs/invariants:

- summarize long structured playtest/test logs;
- compare deterministic state dumps and identify first divergence;
- flag roster, transfer, calendar, finance, injury/discipline, competition or
  save-size anomalies against explicit thresholds;
- classify repeated failures by signature;
- generate bounded regression-test boilerplate from an already-understood bug;
- expand deterministic seed/state combinations;
- review straightforward diffs for obvious mistakes;
- turn verified results into draft documentation for later review.

A useful pattern is:

`test run -> structured JSON -> local Ollama analysis -> concise anomaly summary -> Codex/ChatGPT investigation`

The goal is to keep large repetitive logs and boilerplate away from hosted
reasoning models while preserving human/strong-model review of anything that
changes project truth.

## Tasks that stay with Codex / stronger source-backed analysis

Do **not** trust the local model to decide:

- authentic native FM2001 behavior from disassembly;
- unresolved executable control/data-flow semantics;
- whether a visual discrepancy is historically faithful;
- Windows GUI/media fidelity;
- architecture-changing fixes;
- final release acceptance;
- whether an unsupported inference should be promoted to source truth.

For those tasks, use Codex/local Windows plus direct evidence, or the normal
worker with canonical source evidence when its execution environment is
sufficient.

## Suggested tooling later

When playtesting volume justifies it, add reusable local wrappers such as:

- `ollama_analyze_test_run.py`
- `ollama_compare_state_dumps.py`
- `ollama_summarize_playtest.py`
- `ollama_draft_regression_tests.py`

These should consume structured, bounded inputs and emit machine-readable or
concise findings. Their output is advisory until reviewed and committed through
the normal evidence process.

## Timing

Do not divert the current Gate 13-15 fidelity work merely to build this tooling.
Introduce it when broad playtesting/log volume makes repetitive analysis a
material Codex/token cost.
