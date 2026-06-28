# CEA — Clasificación Enciclopédica Abierta
**Open Encyclopedic Classification**

CEA is an open, modern classification system for knowledge repositories (encyclopedias, wikis, libraries). It keeps the librarian-familiar idea of a numeric, hierarchical, browsable code, but **without the base-10 cap** of decimal systems like CDU/Dewey — so the top level can hold as many classes as a real corpus needs, and any node can be subdivided to unlimited depth.

It is released openly for anyone to adopt, translate, and extend. [Hispanopedia](https://es.hispanopedia.com) is the reference implementation; the standard itself is project-neutral.

## Why another classification?
General decimal schemes (Dewey, CDU) were built in the 19th century for **physical shelves**, and they cram everything into ten top classes. For a real encyclopedic corpus that means history, geography and biography all collapse into a single class, which stops discriminating. CEA fixes the two structural problems:

1. **No 10-class cap.** Top-level classes are zero-padded two-digit codes (`01`, `02`, … `17`, and beyond if needed). Up to 99 branches per level, unlimited depth. Codes still sort as plain text.
2. **Subject-only codes.** A code answers *what a thing is*, never *where* or *when*. Place and period are separate axes, not adjectives baked into the subject code.

## Core principles
- **Entity vs. discipline.** The *thing* and the *field that studies it* are classified apart. A writer goes in Biografías, not in Literatura; a specific mountain goes in Entidades geográficas, not in Geografía-the-discipline; a book goes in *its subject*, not blanket "literature."
- **Notation.** Zero-padded, dot-separated, two digits per level: `15.01.02.16`. Reads left-to-right as a path; truncate to zoom out, extend to zoom in.
- **Multi-class.** An article may carry up to three independent lineages (one primary + two secondary) for genuinely cross-cutting topics.
- **No geography in subject codes.** Geographic scope lives in class 15 (Entidades geográficas) and in the host system's own categories/properties.

## The 17 top classes
```
01 Información, documentación y comunicación   02 Filosofía y pensamiento
03 Religión, mitología y creencias             04 Ciencias sociales y política
05 Derecho                                     06 Economía, empresa y trabajo
07 Educación                                   08 Lengua y literatura
09 Artes, espectáculos y ocio                  10 Deporte
11 Ciencias formales y naturales               12 Tecnología, ingeniería e industria
13 Medicina y ciencias de la salud             14 Geografía (la disciplina)
15 Entidades geográficas                       16 Historia
17 Biografías
```
The full breakdown (subsections and sub-subsections) is in [`TAXONOMY.md`](TAXONOMY.md). The design rules are in [`SPEC.md`](SPEC.md).

## Using CEA in a wiki
On a MediaWiki site, each CEA node becomes a category named `Categoría:CEA <code> <name>` (e.g. `Categoría:CEA 15.04 Municipios y localidades`), nested under its parent code. Articles are tagged with their primary (and optional secondary) CEA categories. See [`reference-implementation/`](reference-implementation/) for the crosswalk bot that auto-assigns CEA codes from infobox types and categories.

## Versioning
CEA follows semantic versioning (see [`VERSION`](VERSION) and [`CHANGELOG.md`](CHANGELOG.md)). The taxonomy will grow and be refined; breaking renumberings bump the major version.

## License
The CEA specification and taxonomy are released under **CC BY 4.0**. The reference-implementation code is released under the **MIT License**. See [`LICENSE`](LICENSE).
