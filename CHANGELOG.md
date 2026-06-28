# Changelog

All notable changes to CEA are documented here. Versioning is semantic
(MAJOR.MINOR.PATCH): renumberings that break existing codes bump MAJOR,
additive refinements bump MINOR, fixes/wording bump PATCH.

## [0.1.0] — initial public release
- First open release of the Clasificación Enciclopédica Abierta (CEA).
- 17 top-level classes; subject-only, non-decimal, zero-padded notation.
- Core rules established: entity-vs-discipline, no geography in subject codes,
  up to three lineages per item, person↔subject cross-reference.
- Class 15 (Entidades geográficas) includes a by-continent, alphabetical
  enumeration of countries (15.01).
- Reference implementation: MediaWiki crosswalk bot (Hispanopedia).
