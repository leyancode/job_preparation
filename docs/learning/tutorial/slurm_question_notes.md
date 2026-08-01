# Question: why did the size loop only run `small`?

## Symptom

The script had:

```bash
SCALES="${SCALES:-small medium large very-large}"
```

The job output also showed:

```text
SCALES=small medium large very-large
```

But the run only executed the `small` scale and then printed `Completed`.
It never reached:

```text
[SCALE] medium
[SCALE] large
[SCALE] very-large
```

The CSV file was correct:

```text
scale,m,n,unknowns
small,2240,2240,5017600
medium,3160,3160,9985600
large,4500,4500,20250000
very-large,6400,6400,40960000
```

## Cause

The loop reads from the CSV file:

```bash
while IFS=, read -r SCALE M N UNKNOWNS; do
  ...
  srun ...
done < "${SIZE_TABLE}"
```

Because the whole `while` loop uses `${SIZE_TABLE}` as standard input, commands
inside the loop inherit that same input by default.

That means `srun` can also read from the CSV file. If `srun` or the MPI program
consumes stdin, it can accidentally eat the remaining CSV lines. Then the outer
`read` has nothing left to read, so the loop stops after `small`.

## Fix

Redirect `srun` stdin away from the CSV:

```bash
srun ... \
  < /dev/null \
  | tee "${LOG}"
```

`/dev/null` is an empty input source. This tells `srun`: if you try to read
stdin, read from an empty file instead of the CSV file.

After this change, only the outer `while read` consumes `${SIZE_TABLE}`, so the
loop can continue through:

```text
small
medium
large
very-large
```

## Lesson

When using this pattern:

```bash
while read ...; do
  command_that_might_read_stdin
done < input_file
```

be careful: commands inside the loop may steal input from `input_file`.

For commands like `srun`, `mpirun`, `ssh`, or anything that may touch stdin,
use:

```bash
command_that_might_read_stdin < /dev/null
```

This protects the loop input.

## Minimal Demo

I made a small demo script:

```text
scripts/ksp/stdin_loop_demo.sh
```

Run it with:

```bash
bash scripts/ksp/stdin_loop_demo.sh
```

The script compares two cases.

Without `< /dev/null`, the inner command reads from the same input stream as the
outer loop:

```text
== Without < /dev/null ==
outer loop got: small
inner command stole: medium
outer loop got: large
inner command stole: very-large
```

The outer loop only sees `small` and `large`, because the inner command stole
`medium` and `very-large`.

With `< /dev/null`, the inner command reads from an empty input source:

```text
== With < /dev/null ==
outer loop got: small
inner command stole: <nothing>
outer loop got: medium
inner command stole: <nothing>
outer loop got: large
inner command stole: <nothing>
outer loop got: very-large
inner command stole: <nothing>
```

Now the outer loop receives every line.
