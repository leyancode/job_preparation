# Dissertation LaTeX build

Compilation workspace for the MSc dissertation. Markdown drafts live one level up in
`../dissertation_prep/`. The whole `docs/` tree is gitignored, so nothing here is
committed.

## Which file am I editing?

**Right now: `draft.tex`.** It is one self-contained file (preamble + all chapters) and
it is the live copy.

`main.tex` + `chapters/*.tex` are the **frozen** multi-file structure kept for the final
dissertation. They are out of date and must not be edited until the split-back below.

Why keep both: the official EPCC template is not in hand yet (see the C-class item in
`../dissertation_prep/00_outline_and_data_gaps.md`). When it arrives, only `main.tex`'s
preamble gets swapped and `chapters/` stays untouched — so the multi-file layout is worth
keeping for later, while a single file is easier to draft in now.

## Build

```bash
tectonic draft.tex     # the live copy -> draft.pdf
tectonic main.tex      # frozen structure -> main.pdf (stale until split-back)
```

One-shot: it compiles and exits. Nothing rebuilds by itself.

### Auto-rebuild on save

Recommended (no install; leaves no intermediate files):

```bash
tectonic -X watch --exec "compile draft.tex"
```

Also works, using the system TeX Live (leaves `.aux`/`.log`/`.fls`/`.fdb_latexmk`):

```bash
latexmk -pdf -pvc -view=none draft.tex
```

Both were verified to rebuild `draft.pdf` on save. Leave either running in a terminal.

Neither refreshes a *viewer* — that depends on the PDF reader.

### VS Code (the actual setup here)

LaTeX Workshop (already installed) is configured in `../../.vscode/settings.json` to build
with tectonic. Nothing to install. Open `draft.tex` and save — it builds, and the PDF
preview tab refreshes itself.

- Preview: `Ctrl+Alt+V` (View LaTeX PDF), or the magnifier icon top-right.
- Jump PDF -> source: `Ctrl+click` in the PDF. Source -> PDF: `Ctrl+Alt+J`.
- Errors land in the Problems panel (that's what `--keep-logs` is for).
- Build now: `Ctrl+Alt+B`.

Why the config is needed at all: LaTeX Workshop ships a tectonic recipe but lists
`latexmk` first, and `latex-workshop.latex.recipe.default` is `"first"` — so without
overriding `latex-workshop.latex.recipes`, VS Code would silently use latexmk instead.
`main.tex` is excluded from root-file detection so `draft.tex` stays the unambiguous root.

Build artifacts `draft.log` and `draft.synctex.gz` appear next to the PDF; both are needed
(error parsing, click-to-jump) and `docs/` is gitignored, so they are harmless.

### A note on the two engines

`tectonic` carries its own package bundle and downloads what a document needs. The system
TeX Live here is incomplete — `siunitx` was missing and broke `latexmk` until the unused
`\usepackage{siunitx}` was dropped from the preamble. If a new package is ever added,
`tectonic` will just fetch it while `latexmk` may need `sudo apt install texlive-*`.
Prefer `tectonic`, and prefer one engine consistently.

## Split-back plan

`draft.tex` keeps `report` + `\chapter`, i.e. the dissertation's real structure, and each
chapter is preceded by a marker:

```
% ===== FILE: chapters/ch3_methodology.tex =====
```

To split: cut at each marker into the named file under `chapters/`, discard `draft.tex`'s
preamble (`main.tex` already has the same one), and `main.tex` compiles unchanged. There
are 11 markers, covering front matter, Ch1–Ch8, and the appendix.

## Draft vs print settings

`oneside` is used so there are no blank pages between chapters (a `twoside,openright`
draft came out 31 pages with 13 blank). For the bound submission, switch the
`\documentclass` options to `[11pt,a4paper,twoside,openright]`, restore
`bindingoffset=6mm` in `geometry`, and re-enable `\listoffigures` / `\listoftables` once
figures and tables exist. All four spots are marked with comments.

## Layout

```
draft.tex             LIVE single-file working copy
main.tex              frozen: preamble + \include of each chapter
chapters/             frozen: 00_frontmatter, ch1..ch8, appendix
references.bib        bibliography (two stub entries; migrate the real .bib in)
figures/              plots go here (\graphicspath points at it)
```

Chapter structure mirrors the outline in
`../dissertation_prep/00_outline_and_data_gaps.md`; `% TODO(G…)` comments mark the data
gaps each section is waiting on.
