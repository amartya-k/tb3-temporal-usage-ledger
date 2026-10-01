# Temporal usage ledger: evaluation record

Current source baseline: `harbor-framework/terminal-bench` commit
`1dcda8716784493721921c23e4bc7f7d988b4494`, inspected 2026-09-29 UTC.
The original baseline was `4def1f367467b34b18e0dbdc086400ba71c3e037`.
The contribution call, `CONTRIBUTING.md`, `docs/TASK_REVIEW_AUTOMATION.md`,
`docs/REVIEWING.md`, rubric, static scripts, and trial workflow were reviewed.
This is an independent hiring submission; no upstream PR is needed.

## Revision 2: durable CDC ledger (2026-09-30)

The initial task did not meet the difficulty requirement. The revision adds a
professionally motivated persistence boundary: independent stream offsets,
historical frontier reads, retries and conflicts, migration, compare-and-swap
invoice versions, rounded correction deltas and a transactional outbox.
The original billing API remains and the 1,000-millicents-per-cent conversion
is now explicit. This revision has **not** yet established the all-fail bar.

- All 26 static check scripts pass locally.
- The 12 reference tests pass in 5.66 seconds on the host. This host check uses
  a temporary harness copy that substitutes the trusted reference program and
  skips UID isolation because this host cannot change UID; it is not Docker
  oracle evidence. The actual committed verifier retains all isolation.
- Docker validation passed in [run 36695330749](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36695330749)
  at commit `61c1572cfb375626f4176de5d7a6844de84b83ec`: all 26 static checks,
  environment/verifier builds, oracle reward 1.0 and nop reward 0.0, with no
  Harbor exceptions. Artifact `11087127298` has SHA256
  `670476847724f674fb89e65e18763e12d92c11cafe1281bec4209239d6b6872c`.
- Six deliberately incorrect reference variants were rejected by the host
  verifier sensitivity check (`scripts/check_mutations.py`): billing buffered
  events, losing original receipts, ignoring invoice CAS, forgetting the
  previous invoice, acknowledging a prefix, and partially committing ingest.
  These are trusted host checks, not adversarial-agent evidence.
- [Run 36695559793](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36695559793),
  workflow attempt 1, tried three standard trials and one cheat trial for each
  Codex configuration. All eight ended with `NonZeroAgentExitCodeError` and
  are excluded from difficulty and cheat results. The downloaded first Astra
  artifact (`11087697194`, SHA256
  `abff942e446149da2bbe7b268661355763d45dc6b4956bb2e9f8ffec7abb5dc2`)
  records a subscription usage-limit error in `agent/codex.txt` after reading
  the task, before implementation. This is an execution failure, not a model
  failure. Workflow attempt 2 was launched at 2026-09-30 15:43 UTC after
  several hours, then deliberately cancelled before completion to move to
  attempt-specific artifact names. That interrupted attempt does not count.
- [Run 36739527266](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36739527266)
  was launched at 2026-09-30 15:48 UTC at commit
  `a4412de41b2e5a1ace61f4e9abc3cf78fc35a682`, with `kind=suite`,
  `configuration=both`, `agent=codex`. It evaluates the same task content as
  revision `61c1572`; only automation and documentation changed. It completed
  with one genuine pass and seven subscription-limit errors, detailed below.
  The analysis task staging was checked locally and its task config
  validated with the pinned Harbor model; automated Claude analysis remains
  unrun.
- Claude trials, upstream Claude rubric review/analysis, and human-authored
  README explanations remain required before a qualifying submission.

## Revision 2: completed trial findings

**This revision does not qualify.** All eight raw artifacts from run
`36739527266` were downloaded and their result files and agent error records
inspected. [Machine-readable evidence](reports/revision-2-trials.json) records
artifact IDs, ZIP SHA256 hashes, rewards, exceptions, and agent errors.

| Configuration | Standard 1 | Standard 2 | Standard 3 | Cheat |
| --- | --- | --- | --- | --- |
| CI: Codex GPT-6 Astra, xhigh | **reward 1, genuine pass** | usage-limit error | usage-limit error | usage-limit error |
| Assignment: Codex GPT-6 Sol, xhigh | usage-limit error | usage-limit error | usage-limit error | usage-limit error |

All seven errors explicitly report the subscription usage limit in
`agent/codex.txt` and `NonZeroAgentExitCodeError` in the trial result. Their
recorded zero rewards are **not** genuine model failures or successful cheat
validation. Neither Claude configuration has run.

The successful Astra trial completed normally in approximately 13 minutes,
with no Harbor exception, reward 1.0, and all 12 verifier tests passing in
11.40 seconds. Its trajectory shows contract reading, reproduction, a shared
integer billing calculator, transactional SQLite persistence, an independent
billing oracle, migration/replay checks, 12 concurrent writers, and deterministic
crash/retry tests. The agent reported 16 of its own regression tests. The
passing verifier output confirms that the intended constraints were satisfied;
this was not a timeout, refusal, or recorded execution error.

Design analysis: adding persistence and concurrency did not establish the
required difficulty. The agent decomposed the explicit contracts into ordinary
SQLite transactions and independently tested the key invariants. A further
revision needs a substantive engineering challenge validated by new trials;
rerunning this same revision cannot erase its observed pass. No arbitrary
constraints, hidden requirements, or reduced time budget have been introduced
to manufacture failures. Automated upstream Claude trajectory analysis remains
unrun, so this paragraph is an inspection of the preserved evidence, not a
claimed automated rubric verdict.

## Revision 1: standard trial findings

[Run 36666825314](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36666825314)
evaluated commit `fa975e7ad3bde28744b106af7d8e0da1a6552549`, six standard attempts:

| Configuration | Attempt 1 | Attempt 2 | Attempt 3 |
| --- | --- | --- | --- |
| CI: Codex GPT-6 Astra, xhigh | reward 1 | reward 1 | reward 1 |
| Assignment: Codex GPT-6 Sol, xhigh | reward 0 | reward 0 | reward 1 |

All six completed without a Harbor exception. The workflow is red because its
acceptance gate requires zero reward, so four legitimately solved trials
caused the evaluation gate to fail. These are not infrastructure failures.

The two Sol zero-reward artifacts were inspected, including trajectories,
result files and verifier stdout. Both agents finished normally and built
local randomized tests. Both divided millicents by 10 rather than 1,000,
causing all six verifier tests to disagree on charge amounts (for example,
1,000 millicents became 100 cents rather than 1 cent). Their local reference
tests repeated the same unit-conversion mistake. No refusal or cutoff was
observed. This is an implementation mistake, but it does not establish the
intended temporal-reconciliation difficulty; revision 2 explicitly removes
that ambiguity. Upstream automated Claude analysis has not run.

Raw zero-reward evidence:
- [Sol attempt 1](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36666825314/artifacts/11076618875), SHA256 `fc4fb19ce80aee13bb97528abab5b36043807199e6242a112ca7e35018797058`.
- [Sol attempt 2](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36666825314/artifacts/11077348451), SHA256 `0ac28ffbad58844f33b6f35840df3f000e7939744eead1b1fc78da86e5e849f9`.

## Revision 1: validation history


The verifier now clears supplementary groups, drops UID/GID, prevents privilege
recovery, captures subprocess output to files, and kills the subprocess group.
The task also declares its invocation time and input limits, tests same-time
revision precedence and large integers, and includes the newly required README
metadata. All 26 current static scripts pass locally. The result gate was checked
to reject timeout exceptions, absent rewards, unfinished trials, and positive
rewards when zero is required.

Docker validation passed in [run 36564356995](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36564356995)
at task revision `b59905dcb6a39a96659af1eae8e0c747d79cb9bc`:

| Check | Result |
| --- | --- |
| All 26 current static scripts | PASS |
| Docker environment and verifier images | PASS |
| Oracle | 1 trial, reward 1.0, zero exceptions |
| Nop | 1 trial, reward 0.0, zero exceptions |
| Explicit result validation | PASS for both oracle and nop |

The [raw Harbor artifact](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36564356995/artifacts/11031126904)
has SHA256 `becd9e906bf265c2e17f45513f2db1dca8fadc2c440ea8307791bd7c87042315`.
The logs confirm complete verifier results and the expected rewards, rather than
only successful process exit codes.

The rubric and model workflow is prepared in `.github/workflows/model-evaluation.yml`.
It uses the upstream production reviewer staging script and the current defaults.
See [RUNNING.md](RUNNING.md) for the authentication and execution steps.
The prepared matrix contains 12 standard trials and four cheat trials across
both the current CI pair and assignment pair.
Codex-only standard evaluation was launched in [run 36666825314](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36666825314)
at revision `fa975e7ad3bde28744b106af7d8e0da1a6552549`. This run has now completed; its results are recorded above. The owner requested proceeding without Claude, so Claude trials and
the upstream Claude rubric reviewer remain unrun. This is a partial evaluation,
not a qualifying completed submission.

## Earlier iteration results actually obtained

| Check | Command / method | Result |
| --- | --- | --- |
| Static CI scripts | `for check in scripts/checks/check-*.sh; do bash "$check" tasks/temporal-usage-ledger || exit 1; done` | PASS, all 25 scripts, exit 0 |
| Reference behavior | Ran all five black-box tests with the reference CLI substituted, including generated histories and the billion-second sparse case | PASS, 5/5 |
| Nop sanity | Compared the supplied legacy program with the independent fixed-history reference | Different output as intended; this is **not** a Harbor nop validation |
| Harbor dry-run | `uvx --from harbor==0.23.1.dev202609170426 harbor run -p tasks/temporal-usage-ledger --agent oracle --env docker --dry-run --yes` | Blocked: `Docker is not installed or not on PATH` |
| Implementation rubric | Upstream staged reviewer and configured review model | NOT RUN: reviewer credentials unavailable |
| Docker build | GitHub Actions `TB3 local validation` run #2, `harbor run --agent oracle` and `--agent nop` on Docker | PASS: both environment builds and runs completed, no exceptions |
| Oracle | `uvx --from harbor==0.23.1.dev202609170426 harbor run -p tasks/temporal-usage-ledger --agent oracle --env docker --yes --jobs-dir ../harbor-oracle` | PASS: 1 trial, 0 exceptions, reward 1.0 |
| Nop | Same Harbor invocation with `--agent nop --jobs-dir ../harbor-nop` | PASS: 1 trial, 0 exceptions, reward 0.0 |
| Standard trials | Three genuine verifier runs per agent/model | NOT RUN: agent credentials unavailable on the Docker runner |
| Adversarial trials | One run per agent/model with TB3 cheat prompt | NOT RUN: agent credentials unavailable on the Docker runner |

GitHub Actions [run #2](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36527321411)
at repository commit `253fdb47b7b57662b4bfccc7a70f93e69a80c14c`
ran on 2026-09-29 UTC. The log reports Docker available, static checks passed,
oracle reward 1.0 and nop reward 0.0, each with zero exceptions. Its
[`harbor-validation` artifact](https://github.com/amartya-k/tb3-temporal-usage-ledger/actions/runs/36527321411/artifacts/11014204812)
contains the raw job directories. Run #1 failed because the workflow's Harbor
commands contained stray `+` arguments; run #2 fixed that workflow error.

The five functional checks were also run on the host with a process wrapper.
The host sandbox rejects `setuid(65534)` with EINVAL; do not count that as an
agent failure. The completed oracle/nop runs validate the real Docker path,
but no claims about model failure rates or exploit resistance follow from them.

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
# Run the repository's Model evaluation workflow with kind=review for the
# production staged reviewer and complete per-criterion verdicts.
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
`.github/workflows/local-validation.yml`, which ran static, oracle, and nop
commands on a GitHub Actions Docker runner. Its log and raw results are linked
above.

## Preliminary failure hypotheses (not trial findings)

Design-review concern: the billing rules are largely spelled out and the
reference program is compact. This task may be too easy for frontier agents or
fail the rubric's `difficult` and `agentic` criteria. Static/oracle/nop success
does not establish difficulty. Real trials may require a substantial redesign;
the all-fail requirement has not been demonstrated.

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
The task still needs a passing rubric, the required standard and adversarial
trials, and their trajectory analyses recorded here. Until then this is a
candidate, not a qualifying submission.
