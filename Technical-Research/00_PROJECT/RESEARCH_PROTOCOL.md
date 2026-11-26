# Research Protocol

The working rules live in `/CLAUDE.md` (ID conventions, claim statuses, experiment
rules, session protocol). This file records how the protocol changes over time.

## Experiment lifecycle
1. Hypothesis written as a Q (open question) or a D (decision proposal).
2. Implementation in `experiments/encoders/`, changing a single pipeline stage.
3. `python -m harness.bench E0NN_<name>`. Results dirs are immutable; a re-run gets a new E-ID.
4. Summary copied into `03_ANALYSIS/COMPARISON_TABLES.md` with the E-ID.
5. Claim statuses updated (`VERIFIED-EXPERIMENT` / `REFUTED`), logged in VERIFICATION_LOG.

## Protocol changes
| date | change | why |
|---|---|---|
| 2026-11-26 | Initial protocol (S001) | project setup |
