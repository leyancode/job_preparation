# Supervisor Reply Draft

Subject: PETSc ex2 size-grid benchmark progression

Dear Paul,

Thank you for the feedback. I agree that going up to 128M unknowns may be too expensive in terms of compute resources and wall-clock time, so I will avoid extending the runs that far at this stage.

I have currently tested problem sizes up to 40.96M unknowns (`6400 x 6400`). I am now organising the results problem-size-first, using the criterion `10,000 < N/C < 1,000,000`, where `N = m x n` and `C = nodes x ppn x threads`. This makes the table read as problem size, then total cores, then `N/C`, then runtime, rather than starting from the node/thread configuration.

I will fill the table from the smaller cases and lower core counts first, then work down only where the `N/C` range and observed runtime look reasonable, to avoid excessive wall-clock cost.

For the 1M unknown case (`1000 x 1000`), the available data contain 62 completed timing rows. The fastest recorded runtime is 3.844 seconds at 128 total cores, and the slowest is 248.0 seconds at 1 total core. The best runtime at C=1 is 245.7 seconds, while the best runtime at C=128 is 3.844 seconds; however, C=128 gives `N/C = 7,812.5`, which is below the lower threshold, so I would treat that as too small per core rather than a priority case.

For the very-large cases, I will avoid running configurations where `N/C` or the observed wall-clock cost is unreasonable, and I will use the existing 40.96M results only where they help complete the valid part of the table.

Best regards,
Leyan
