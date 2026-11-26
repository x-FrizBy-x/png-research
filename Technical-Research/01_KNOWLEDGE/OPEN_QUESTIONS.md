# Open Questions

| ID | question | raised | status | notes |
|---|---|---|---|---|
| Q001 | Which optimisation target: max compression, size/time Pareto, or fast encode? | S001 | OPEN (user decision) | see PROJECT_CHARTER |
| Q002 | Why is `pyref-minsum-z9` larger than `-z6` on the synthetic corpus (+2.5% total, +7.9% on rgb8_photolike)? Is it a zlib-ng level-9 behaviour or an interaction with minsum filter choice? | S001 (E000) | OPEN | synthetic only; check again on the real corpus and with stock zlib |
| Q003 | How much do results differ between zlib, zlib-ng and libdeflate at the same nominal level? | S001 | OPEN | Python here bundles zlib-ng 1.3.1 |
