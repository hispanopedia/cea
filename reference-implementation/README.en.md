**English** · [Español](README.md)

# CEA reference implementation — MediaWiki crosswalk

`cea_crosswalk_bot.py` is the reference tool that assigns CEA codes to the
articles of a MediaWiki site (Hispanopedia) without per-article fetches,
using two signals from the database:

- **primary infobox type** (`Ficha de …`), folded to its parent template;
- **categories** (for refining persons, taxa, places, books, documents, and
  for the no-infobox fallback).

It assigns one primary CEA code plus optional secondary codes, following the
rules in `../SPEC.md`. Output is written to a local SQLite state DB; nothing is
written to the wiki in the classify phase.

Phases:
- `classify` — compute assignments into the state DB (no wiki writes)
- `counts`   — per-class counts and coverage
- `sample`   — random sample for validation

This is a pragmatic, signal-based crosswalk, not a canonical part of the CEA
standard. Other implementations may assign codes however they like; only the
class structure and rules in `../SPEC.md` and `../TAXONOMY.md` are normative.

Note: the script targets a specific MediaWiki 1.45 schema and a particular set
of Spanish infobox templates, so it is illustrative rather than turnkey.
