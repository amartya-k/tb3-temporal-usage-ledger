## Task Metadata

- **Author:** Amartya Kalapahar (27891310+amartya-k@users.noreply.github.com)
- **Category:** `Software`
- **Tags:** <code>billing</code> <code>bitemporal</code> <code>reconciliation</code> <code>python</code>
- **Expert time:** 4 hours
- **Agent timeout:** 4 hours
- **CPUs:** 2
- **Memory:** 2 GB

## Difficulty explanation

The program must reconstruct two histories at each invoice cutoff, split usage at tariff boundaries, and allocate discrete units without losing any at the splits. Overlapping and revised rates interact with exact account-level rounding, so a locally plausible per-session calculation can produce a wrong invoice.

## Solution explanation

Select the latest visible revision of every logical ID for each query, discard tombstones, and partition each intersecting usage session at the visible tariff boundaries. Use cumulative integer allocation on each partition, select the highest-precedence covering rate, then aggregate millicents and round once per account.

## Verification explanation

The verifier runs the submitted program in an isolated process on fixed and generated histories, comparing its structured outputs with an independent per-second reference calculation. Tests cover late corrections, tombstones, gaps, overlaps, exact ties, zero-unit sessions, and input-order invariance.

## Relevant experience

The author has worked on Python services and clinical data pipelines where late corrections, durable audit histories, and precise reconciliation matter.

## Change Log

- Added current metadata requirements and hardened subprocess privilege and process handling in the verifier.
