# Temporal usage ledger — Terminal-Bench 3 task candidate

An original task for repairing a durable CDC billing service. The agent must
preserve historical billing semantics while handling out-of-order event delivery,
idempotent retries, schema migration, concurrent invoice settlement and a durable
outbox. The verifier compares fresh-process behavior with independent billing
and state-transition models in a separate container.

The task is in [`tasks/temporal-usage-ledger/`](tasks/temporal-usage-ledger/).
[Evaluation results and reproduction commands](RESULTS.md) distinguish
checks actually run from checks still pending. This is a **candidate**, not a
claim that the hiring assignment's all-fail trial requirement has been met.

The task format follows Terminal-Bench 3 at upstream commit
`1dcda8716784493721921c23e4bc7f7d988b4494`. Copy its task folder into a
checkout of that revision to run upstream static checks and the rubric.
Harbor can run the task directly from this repository's task path once Docker
and agent credentials are configured.
The included GitHub Actions workflow checks static rules, oracle, and nop
validation on a Docker-capable runner and preserves the raw Harbor results.
It does not substitute for the rubric or agent trials.

[Evaluation setup](RUNNING.md) describes the subscription-authenticated workflow.
The original task was solved by GPT-6 Astra in three of three trials. The
first durable-ledger revision passed 26 static checks and Docker oracle/nop
validation, but Astra solved it in one completed trial; seven subsequent
attempts hit subscription limits. This `revision-3` branch adds causal CDC
predecessors and tests their effect on delivery watermarks and historical
snapshots. Its host reference tests and static checks pass; Docker validation
and model trials are tracked in [RESULTS.md](RESULTS.md). The repository link
was emailed to Klavis on September 30, 2026, before this branch was created.
The submitted default branch still contains revision 2.

The four task README explanations are AI-assisted drafts. The contribution
guide requires the author to rewrite those sections personally before
the task can claim full conformance.
