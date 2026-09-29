# Temporal usage ledger: evaluation record

Source baseline: `harbor-framework/terminal-bench-3` commit
`4def1f367467b34b18e0dbdc086400ba71c3e037`, inspected 2026-09-29 UTC.
The contribution call, `CONTRIBUTING.md`, `docs/TASK_REVIEW_AUTOMATION.md`,
`docs/REVIEWING.md`, rubric, static scripts, and trial workflow were reviewed.
This is an independent hiring submission; no upstream PR is needed.

## Results actually obtained

| Check | Command / method | Result |
| --- | --- | --- |
| Static CI scripts | `for check in scripts/checks/check-*.sh; do bash "$check" tasks/temporal-usage-ledger || exit 1; done` | PASS, all 25 scripts, exit 0 |
| Reference behavior | Ran all five black-box tests with the reference CLI substituted, including generated histories and the billion-second sparse case | PASS, 5/5 |
| Nop sanity | Compared the supplied legacy program with the independent fixed-history reference | Different output as intended; this is **not** a Harbor nop validation |
| Harbor dry-run | `uvx --from harbor==0.23.1.dev202609170426 harbor run -p tasks/temporal-usage-ledger --agent oracle --env docker --dry-run --yes` | Blocked: `Docker is not installed or not on PATH` |
| Implementation rubric | `harbor check` with the current rubric and reviewer model | NOT RUN: reviewer credentials unavailable |
| Docker build | Harbor/Docker | NOT RUN: Docker daemon and CLI unavailable |
| Oracle / nop | Harbor | NOT RUN: Docker unavailable |
| Standard trials | Three genuine verifier runs per agent/model | NOT RUN: Docker and model credentials unavailable |
| Adversarial trials | One run per agent/model with TB3 cheat prompt | NOT RUN: Docker and model credentials unavailable |

The five functional checks were run on the host with a process wrapper. They
verify algorithmic behavior, but they do not validate Harbor artifact transfer,
the image build, privilege dropping, CTRF output, or the separate verifier.
The host sandbox rejects `setuid(65534)` with EINVAL; do not count that as an
agent failure. No claims about model failure rates or exploit resistance follow
from these local checks.

## Configuration discrepancy

The assignment names `codex/openai/gpt-6-sol` with `reasoning_effort=xhigh`
and `claude-code/anthropic/claude-opus-5.5` with
`reasoning_effort=max`. At the pinned TB3 commit,
`.github/harbor-run-defaults.yml` instead specifies
`codex/openai/gpt-6-astra` (`xhigh`) and
`claude-code/anthropic/claude-fable-5-1` (`max`), three standard
attempts per agent, one cheat attempt per agent, and Sonnet 5 analysis.
To meet both interpretations, run and record the requested pair **and**
the current CI default pair; do not relabel either pair as the other.
Before final submission, recheck upstream defaults for new changes.

## Remaining commands

From a fresh TB3 checkout with this `tasks/temporal-usage-ledger` directory:

```sh
for check in scripts/checks/check-*.sh; do
  bash "$check" tasks/temporal-usage-ledger || exit 1
done
harbor check tasks/temporal-usage-ledger -r docs/prompts/task-implementation.toml -m anthropic/claude-sonnet-5
harbor run -p tasks/temporal-usage-ledger --agent oracle --env docker --yes
harbor run -p tasks/temporal-usage-ledger --agent nop --env docker --yes

harbor run -p tasks/temporal-usage-ledger --agent codex --model openai/gpt-6-sol --env docker --yes --n-attempts 3 --ae CODEX_FORCE_AUTH_JSON=1 --ak reasoning_effort=xhigh
harbor run -p tasks/temporal-usage-ledger --agent claude-code --model anthropic/claude-opus-5.5 --env docker --yes --n-attempts 3 --ae CLAUDE_FORCE_OAUTH=1 --ae CLAUDE_CODE_OAUTH_TOKEN=<TOKEN> --ae CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000 --ak reasoning_effort=max

harbor run -p tasks/temporal-usage-ledger --agent codex --model openai/gpt-6-sol --env docker --yes --n-attempts 1 --ae CODEX_FORCE_AUTH_JSON=1 --ak reasoning_effort=xhigh --extra-instruction-path docs/prompts/hack-trial-prompt.md
harbor run -p tasks/temporal-usage-ledger --agent claude-code --model anthropic/claude-opus-5.5 --env docker --yes --n-attempts 1 --ae CLAUDE_FORCE_OAUTH=1 --ae CLAUDE_CODE_OAUTH_TOKEN=<TOKEN> --ae CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000 --ak reasoning_effort=max --extra-instruction-path docs/prompts/hack-trial-prompt.md
```

Repeat the two standard and two cheat commands for the **current CI default**
model IDs if they still differ. Save every Harbor job directory and inspect
trial-level reward and errors; count only completed verifier reward zero as a
genuine model failure. A timeout, crash, setup error, or missing reward is
inconclusive. Analyze completed trajectories with the current
`docs/prompts/trial-analysis.toml` and record concrete failure causes.
Any standard pass or nonzero cheat reward requires task revision and a full
rerun. The entries above are commands to execute, **not** completed results.
The standalone repository also contains
`.github/workflows/local-validation.yml`, which will run static, oracle, and
nop commands on a GitHub Actions Docker runner after publication. Inspect its
uploaded Harbor results before recording validation as passed.

## Preliminary failure hypotheses (not trial findings)

- A naive implementation may choose revisions by file order rather than
  `(recorded, revision)`, producing incorrect historical invoices.
- Per-session rounding and proportional division at each tariff split lose
  fractional allocations; the correct cumulative-floor calculation preserves
  the account total.
- An implementation iterating each second cannot finish the sparse
  billion-second case; interval boundaries are the meaningful scale.

## Author review before submission

`tasks/temporal-usage-ledger/README.md` is an AI-assisted draft. TB3's guide
requires its four explanatory sections to be written completely by a human.
Amartya should replace them in his own words after reviewing the implementation.
The task and verifier also need the real Docker, rubric, oracle, nop, six
standard trials, and two adversarial trials recorded here. Until then this is
a candidate, not a qualifying submission.
