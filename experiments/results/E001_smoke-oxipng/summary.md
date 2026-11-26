# E001_smoke-oxipng

Files: 12 · source bytes: 1,164,014 · baseline: `pyref-minsum-z6`

| encoder | scope | files ok | total bytes | Δ vs baseline | Σ median time (s) | mismatch | alpha-equiv | errors |
|---|---|---|---|---|---|---|---|---|
| pyref-minsum-z6 | encode | 12/12 | 555,087 | — | 0.143 | 0 | 0 | 0 |
| pillow-z9 | encode | 12/12 | 553,012 | -0.37% | 0.080 | 0 | 0 | 0 |
| oxipng-o2 | recode | 12/12 | 542,509 | -2.27% | 0.274 | 0 | 0 | 0 |
| oxipng-max | recode | 12/12 | 541,654 | -2.42% | 1.034 | 0 | 0 | 0 |

### Δ vs baseline by category

| encoder | synthetic |
|---|---|
| pyref-minsum-z6 | — |
| pillow-z9 | -0.37% |
| oxipng-o2 | -2.27% |
| oxipng-max | -2.42% |

Δ is computed only over files where both encoders succeeded. Time scopes: `encode` = pixels already decoded; `recode` = PNG bytes in, includes decoding; `process` = CLI tool, includes process startup. Don't compare times across scopes without saying so.
