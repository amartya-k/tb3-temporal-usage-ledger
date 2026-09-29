# Temporal usage ledger — Terminal-Bench 3 task candidate

An original task for repairing a bitemporal usage-billing reconciler. The
agent receives a broken Python program and must produce accurate invoices
despite late revisions, cancellations, overlapping tariffs, partial intervals,
exact integer allocation, and account-level rounding. The verifier runs the
submitted program on fixed and generated inputs in a separate container.

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

[Evaluation setup](RUNNING.md) describes the prepared subscription-authenticated
rubric and trial workflow. The task was updated for the latest static requirements
and verifier isolation rules; earlier validation results apply to the earlier
revision only.

The four task README explanations are AI-assisted drafts. The contribution
guide requires the author to rewrite those sections personally before
submission.
