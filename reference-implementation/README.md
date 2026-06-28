**Español** · [English](README.en.md)

# Implementación de referencia de CEA — correspondencia para MediaWiki

`cea_crosswalk_bot.py` es la herramienta de referencia que asigna códigos CEA a
los artículos de un sitio MediaWiki (Hispanopedia) sin descargas por artículo,
usando dos señales de la base de datos:

- el **tipo de ficha principal** (`Ficha de …`), reducido a su plantilla madre;
- las **categorías** (para refinar personas, taxones, lugares, libros y
  documentos, y para el caso de respaldo sin ficha).

Asigna un código CEA principal más códigos secundarios opcionales, siguiendo las
reglas de `../SPEC.md`. La salida se escribe en una base de datos SQLite local;
en la fase de clasificación no se escribe nada en la wiki.

Fases:
- `classify` — calcula las asignaciones en la base de datos local (no escribe en la wiki)
- `counts`   — recuentos por clase y cobertura
- `sample`   — muestra aleatoria para validación

Es una correspondencia pragmática basada en señales, no una parte canónica del
estándar CEA. Otras implementaciones pueden asignar los códigos como prefieran;
solo la estructura de clases y las reglas de `../SPEC.md` y `../TAXONOMY.md` son
normativas.

Nota: el script está pensado para un esquema concreto de MediaWiki 1.45 y un
conjunto particular de plantillas de ficha en español, por lo que es ilustrativo
más que de uso inmediato.
