# Completing the evaluation

The workflow defaults to `kind=standard`, `configuration=both`, and `agent=codex`.
The first Codex evaluation completed in [run 36666825314](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36666825314).
Claude trials and the upstream Claude implementation reviewer are intentionally
deferred at the owner's request. No Claude credential is needed for Codex runs.
This partial evaluation does not satisfy the full assignment; human authorship
and all required evaluation results are still outstanding.

## Subscription authentication

For the current Codex-only setup, only `CODEX_AUTH_JSON` is required.
The Claude secret below is optional until Claude evaluation is resumed.
In this repository's **Settings → Secrets and variables → Actions**, add:

| Repository secret | Value |
| --- | --- |
| `CODEX_AUTH_JSON` | Contents of your own `~/.codex/auth.json` after signing in to Codex with your subscription |
| `CLAUDE_CODE_OAUTH_TOKEN` | Token obtained using `claude setup-token` with your Claude subscription |

These values are stored as private GitHub Actions secrets and supplied to the
Docker runner for this evaluation. Do not put them in source files, issues,
workflow inputs, or chat. No API key is required by this workflow; it forces
subscription authentication. Authentication alone does not guarantee that a
subscription supports every model ID below.

## Runs

Open **Actions → Model evaluation → Run workflow**. For Codex-only evaluation,
keep `agent=codex` and select `kind=suite` to queue standard then cheat trials
sequentially. Individual `standard` and `cheat` modes remain available.
Do not launch overlapping runs using the same subscription credential.

For the full assignment once Claude access is available, start with `kind=review`.
It stages the review task using upstream `scripts/review/stage_task.py`, the
current implementation rubric, and the configured review agent/model.
The workflow fails if any criterion fails or a verdict is missing.

Once review passes, run `kind=standard` and then `kind=cheat`, using
`configuration=both`. There are three independent standard attempts and one
cheat attempt per agent/model. The workflow reads upstream kwargs and environment
settings, and uses the unmodified upstream cheat prompt. Each attempt receives a
fresh Docker environment. Attempts are queued sequentially to limit subscription
rate pressure; an error remains an error and must not be counted as a model failure.

If only one subscription is available, select `agent=codex` or `agent=claude-code`
to run that subset independently. The other agent and rubric remain required.

The current pin is `harbor-framework/terminal-bench` at
`1dcda8716784493721921c23e4bc7f7d988b4494`, checked 2026-09-29 UTC.
The former `terminal-bench-3` URL redirects to this repository.

| Configuration | Agent | Model | Reasoning |
| --- | --- | --- | --- |
| Current CI | codex | openai/gpt-6-astra | xhigh |
| Current CI | claude-code | anthropic/claude-fable-5-1 | max |
| Assignment | codex | openai/gpt-6-sol | xhigh |
| Assignment | claude-code | anthropic/claude-opus-5.5 | max |

`both` runs both pairs because the written assignment and the current CI differ.
The review model is `anthropic/claude-sonnet-5` with `claude-code`, as configured
by upstream. Before submission, compare the pin with upstream main again.

Each job stores the selected configuration and exact command, Harbor result,
verifier output, and available trajectory in an `evaluation-*` artifact.
Known credential strings are redacted before upload; the artifact manifest lists
redactions and omitted binary or oversized files. Unredacted temporary credentials
are not uploaded. Artifacts do not constitute a completed analysis.

## Acceptance and analysis

`scripts/check_results.py` rejects incomplete results, Harbor exceptions, missing
rewards, and rewards other than the required value. A zero is only a candidate
model failure until its trajectory and verifier output have been reviewed. Check
for API errors, rate limits, internal crashes, refusals, timeouts, reward tampering,
and task specification defects using upstream `docs/prompts/trial-analysis.toml`.
Record concrete failure causes in `RESULTS.md`; do not infer them from zero alone.

Any standard pass requires a task revision and fresh trials. Any nonzero cheat
reward requires investigation and revision. Preserve failed attempts and all
iterations; never select only successful evaluation attempts for the report.

## Author step

The four explanatory sections in the task README remain AI-assisted drafts.
Upstream `CONTRIBUTING.md` requires them to be written completely by a human.
Replace each with one to three sentences in your own words and verify every
personal-experience claim. The metadata section may be generated from task.toml.
