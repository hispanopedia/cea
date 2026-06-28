**Español** · [English](README.en.md)

# CEA — Clasificación Enciclopédica Abierta

CEA es un sistema de clasificación abierto y moderno para repositorios de conocimiento (enciclopedias, wikis, bibliotecas). Conserva la idea, familiar para bibliotecarios, de un código numérico, jerárquico y navegable, pero **sin el límite de base 10** de los sistemas decimales como la CDU o Dewey, de modo que el nivel superior puede tener tantas clases como necesite un corpus real, y cualquier nodo puede subdividirse hasta una profundidad ilimitada.

Se publica de forma abierta para que cualquiera pueda adoptarlo, traducirlo y ampliarlo. [Hispanopedia](https://es.hispanopedia.com) es la implementación de referencia; el estándar en sí es independiente del proyecto.

## ¿Por qué otra clasificación?
Los esquemas decimales generales (Dewey, CDU) se concibieron en el siglo XIX para **estanterías físicas** y lo encajan todo en diez clases superiores. Para un corpus enciclopédico real eso significa que historia, geografía y biografía se concentran en una sola clase, que deja de discriminar. CEA corrige los dos problemas estructurales:

1. **Sin límite de 10 clases.** Las clases de nivel superior son códigos de dos dígitos con cero a la izquierda (`01`, `02`, … `17`, y más si hace falta). Hasta 99 ramas por nivel y profundidad ilimitada. Los códigos siguen ordenándose como texto.
2. **Códigos solo de materia.** Un código responde a *qué es* algo, nunca a *dónde* o *cuándo*. El lugar y el período son ejes aparte, no adjetivos incrustados en el código de materia.

## Principios fundamentales
- **Entidad frente a disciplina.** La *cosa* y el *campo que la estudia* se clasifican por separado. Un escritor va en Biografías, no en Literatura; una montaña concreta va en Entidades geográficas, no en Geografía-disciplina; un libro va en *su materia*, no en un genérico «literatura».
- **Notación.** Segmentos de dos dígitos con cero a la izquierda, separados por puntos: `15.01.02.16`. Se lee de izquierda a derecha como una ruta; se trunca para ampliar la vista y se extiende para precisar.
- **Multiclase.** Un artículo puede llevar hasta tres linajes independientes (uno principal y dos secundarios) para temas genuinamente transversales.
- **Nada de geografía en los códigos de materia.** El ámbito geográfico vive en la clase 15 (Entidades geográficas) y en las categorías o propiedades del propio sistema.

## Las 17 clases superiores
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
El desglose completo (subsecciones y sub-subsecciones) está en [`TAXONOMY.md`](TAXONOMY.md). Las reglas de diseño, en [`SPEC.md`](SPEC.md).

## Uso de CEA en una wiki
En un sitio MediaWiki, cada nodo CEA se convierte en una categoría llamada `Categoría:CEA <código> <nombre>` (p. ej. `Categoría:CEA 15.04 Municipios y localidades`), anidada bajo el código de su categoría madre. Los artículos se etiquetan con su categoría CEA principal (y las secundarias opcionales). En [`reference-implementation/`](reference-implementation/) está el bot de correspondencia que asigna códigos CEA automáticamente a partir de los tipos de ficha y las categorías.

## Versionado
CEA sigue el versionado semántico (véanse [`VERSION`](VERSION) y [`CHANGELOG.md`](CHANGELOG.md)). La taxonomía crecerá y se refinará; las renumeraciones que rompan códigos existentes suben la versión mayor.

## Licencia
La especificación y la taxonomía de CEA se publican bajo **CC BY 4.0**. El código de la implementación de referencia se publica bajo la **licencia MIT**. Véase [`LICENSE`](LICENSE).
