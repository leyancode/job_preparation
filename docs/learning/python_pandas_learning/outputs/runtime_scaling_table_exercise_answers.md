# Exercise Helper Answers

Use this file after trying `lessons/exercises.md` yourself.

## Fastest vs Cheapest Configuration

| scale | fastest total cores | fastest threads | fastest runtime/s | cheapest total cores | cheapest threads | cheapest CUs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| small | 128 | 1 | 3.85 | 128 | 1 | 0.0011 |
| medium-small | 128 | 1 | 64.02 | 128 | 1 | 0.0178 |
| medium | 128 | 1 | 136.50 | 128 | 1 | 0.0379 |
| large | 128 | 1 | 340.45 | 128 | 1 | 0.0946 |
| very-large | 128 | 1 | 846.90 | 128 | 1 | 0.2352 |

## Efficiency Above 100%

Rows with efficiency above 100%: 2

These rows can be useful discussion points about superlinear speedup, baseline effects, and measurement variability.
