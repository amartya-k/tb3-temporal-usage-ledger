## Task Metadata

- **Author:** Amartya Kalapahar (27891310+amartya-k@users.noreply.github.com)
- **Category:** `Software`
- **Tags:** <code>billing</code> <code>bitemporal</code> <code>reconciliation</code> <code>causal-ordering</code> <code>python</code>
- **Expert time:** 4 hours
- **Agent timeout:** 4 hours
- **CPUs:** 2
- **Memory:** 2 GB

## Difficulty explanation

AI-assisted draft requiring the author's rewrite: A backend engineer must reconcile independent delivery order and business-time revisions while preserving historical invoices across migration, retries, and concurrent writers. The synthetic CDC histories model realistic duplicate delivery, gaps, corrections and account movement; the hard part is maintaining all visibility and atomicity invariants together.

## Solution explanation

AI-assisted draft requiring the author's rewrite: Store immutable received events separately from contiguous committed prefixes, and resolve every billing snapshot using both a delivery frontier and business-time cutoff. Commit mutation receipts, compare-and-swap invoice versions, frozen totals, and outbox records in one transaction; derive correction deltas from already-rounded invoice totals.

## Verification explanation

AI-assisted draft requiring the author's rewrite: Black-box subprocess tests compare persisted outputs with an independent in-memory transition model and a per-second billing model. The suite checks gaps, conflicts, retry receipts, migration, historical snapshots, invoice deltas, acknowledgments, concurrent writers, and process interruption; tests and rewards remain inaccessible to submitted processes.

## Relevant experience

Human author must provide one to three sentences describing their own relevant professional experience; this section is not complete.

## Change Log

- Added current metadata requirements and hardened subprocess privilege and process handling in the verifier.

- Extended reconciliation into a durable CDC ledger with migration, atomic receipts, historical delivery frontiers, invoice corrections and an outbox.

- Revision 3 adds causal predecessor vectors, fixed-point stream watermarks, and causally closed historical frontiers.
