# CEA Specification (v0.1.0)

## 1. Scope
CEA (Clasificación Enciclopédica Abierta / Open Encyclopedic Classification) is a numeric, hierarchical, browsable classification for knowledge repositories. It assigns each item one primary class (and optionally secondary classes) describing **what the item is**.

## 2. Notation
- Codes are **zero-padded, dot-separated segments, two digits per segment**: `09`, `09.03`, `10.01.02`, `15.01.02.16`.
- Each segment is a level of the hierarchy; reading left to right walks the tree from general to specific.
- Up to **99 branches per level** (`01`–`99`); **unlimited depth** (add segments as needed).
- Codes sort correctly as plain text because every segment is fixed width.
- **Not decimal**: there is no base-10 cap on the number of top-level classes. The system grows in breadth (more top classes) and depth (more segments) as a corpus requires.

## 3. Design rules
### 3.1 Subject-only codes
A CEA code describes the *subject/nature* of an item, never its place or time. Do **not** create geographic variants of subject classes (no "geología ibérica", no "ingeniería hispana"). Geographic scope is expressed by class **15 (Entidades geográficas)** and by the host system's own categories/metadata; period is expressed by class **16 (Historia)** and metadata.

### 3.2 Entity vs. discipline
The *thing* and the *field that studies it* are separate objects in separate lineages:
- a **person** → 17 Biografías (by profession); the **study of their field** → the relevant subject class.
- a **specific place or natural feature** (a city, a river, a mountain, a park) → 15 Entidades geográficas; **geography as a discipline** → 14 Geografía.
- a **work** (book, treatise, film) → *its subject* (an engineering treatise → 12, a novel → 08); never blanket "literature" just because it is a book.

### 3.3 Multi-class
An item may carry **one primary** CEA code plus **up to two secondary** codes, for genuinely cross-cutting topics (e.g. a historic church → 09.02 Arquitectura + 03 Religión + 16 Historia). Hierarchy membership is implied: tagging a child code implies membership of all its ancestors.

### 3.4 Person ↔ subject cross-reference
Biography subclasses (17.x) correspond thematically to the subject classes (e.g. 17.01 Escritores ↔ 08 Lengua y literatura). A biography may carry its field as a secondary code so that browsing the subject surfaces both works and the people who made them.

## 4. The class structure
The authoritative class list (17 top classes, their subsections and sub-subsections) is maintained in `TAXONOMY.md`. Implementations should treat that file as the source of truth for the current version.

## 5. Implementation in MediaWiki (reference)
- Each CEA node is a category `Categoría:CEA <code> <name>`, nested under its parent code's category.
- Articles are tagged with their primary (and optional secondary) CEA category.
- Codes are assigned by a crosswalk from existing signals (infobox type, categories). See `reference-implementation/`.
- Items with no confident assignment go to a `CEA sin asignar` tracking category — never silently dropped.

## 6. Governance & versioning
- Semantic versioning. Additive refinements bump minor; renumberings that break existing codes bump major.
- Changes are recorded in `CHANGELOG.md`.
