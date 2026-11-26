# E000_smoke

Files: 12 · source bytes: 1,164,014 · baseline: `pyref-minsum-z6`

| encoder | scope | files ok | total bytes | Δ vs baseline | Σ median time (s) | mismatch | alpha-equiv | errors |
|---|---|---|---|---|---|---|---|---|
| pyref-none-z9 | encode | 12/12 | 1,165,589 | +109.98% | 0.103 | 0 | 0 | 0 |
| pyref-paeth-z9 | encode | 12/12 | 579,511 | +4.40% | 0.106 | 0 | 0 | 0 |
| pyref-minsum-z6 | encode | 12/12 | 555,087 | — | 0.114 | 0 | 0 | 0 |
| pyref-minsum-z9 | encode | 12/12 | 569,184 | +2.54% | 0.141 | 0 | 0 | 0 |
| pillow-z6 | encode | 12/12 | 559,825 | +0.85% | 0.032 | 0 | 0 | 0 |
| pillow-z9 | encode | 12/12 | 553,012 | -0.37% | 0.065 | 0 | 0 | 0 |

### Δ vs baseline by category

| encoder | synthetic |
|---|---|
| pyref-none-z9 | +109.98% |
| pyref-paeth-z9 | +4.40% |
| pyref-minsum-z6 | — |
| pyref-minsum-z9 | +2.54% |
| pillow-z6 | +0.85% |
| pillow-z9 | -0.37% |

Δ is computed only over files where both encoders succeeded. Times with scope `process` include process startup and decode, so don't compare them directly with `encode`.
