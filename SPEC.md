**Español** · [English](SPEC.en.md)

# Especificación de CEA (v0.1.0)

## 1. Ámbito
CEA (Clasificación Enciclopédica Abierta) es una clasificación numérica, jerárquica y navegable para repositorios de conocimiento. Asigna a cada elemento una clase principal (y, opcionalmente, clases secundarias) que describe **qué es** el elemento.

## 2. Notación
- Los códigos son **segmentos de dos dígitos con cero a la izquierda, separados por puntos**: `09`, `09.03`, `10.01.02`, `15.01.02.16`.
- Cada segmento es un nivel de la jerarquía; leído de izquierda a derecha recorre el árbol de lo general a lo específico.
- Hasta **99 ramas por nivel** (`01`–`99`); **profundidad ilimitada** (se añaden segmentos según haga falta).
- Los códigos se ordenan correctamente como texto plano porque cada segmento tiene anchura fija.
- **No es decimal**: no hay límite de base 10 en el número de clases superiores. El sistema crece en amplitud (más clases superiores) y en profundidad (más segmentos) según lo requiera el corpus.

## 3. Reglas de diseño
### 3.1 Códigos solo de materia
Un código CEA describe la *materia o naturaleza* de un elemento, nunca su lugar ni su tiempo. **No** se crean variantes geográficas de las clases de materia (nada de «geología ibérica» ni «ingeniería hispana»). El ámbito geográfico se expresa con la clase **15 (Entidades geográficas)** y con las categorías/metadatos del sistema anfitrión; el período, con la clase **16 (Historia)** y metadatos.

### 3.2 Entidad frente a disciplina
La *cosa* y el *campo que la estudia* son objetos distintos en linajes distintos:
- una **persona** → 17 Biografías (por profesión); el **estudio de su campo** → la clase de materia correspondiente.
- un **lugar o accidente natural concreto** (una ciudad, un río, una montaña, un parque) → 15 Entidades geográficas; la **geografía como disciplina** → 14 Geografía.
- una **obra** (libro, tratado, película) → *su materia* (un tratado de ingeniería → 12, una novela → 08); nunca un genérico «literatura» por el mero hecho de ser un libro.

### 3.3 Multiclase
Un elemento puede llevar **una clase principal** y **hasta dos secundarias**, para temas genuinamente transversales (p. ej. una iglesia histórica → 09.02 Arquitectura + 03 Religión + 16 Historia). La pertenencia jerárquica es implícita: etiquetar un código hijo implica pertenecer a todos sus ancestros.

### 3.4 Referencia cruzada persona ↔ materia
Las subclases de biografía (17.x) se corresponden temáticamente con las clases de materia (p. ej. 17.01 Escritores ↔ 08 Lengua y literatura). Una biografía puede llevar su campo como código secundario, de modo que al explorar la materia aparezcan tanto las obras como las personas que las crearon.

## 4. La estructura de clases
La lista autoritativa de clases (17 clases superiores, sus subsecciones y sub-subsecciones) se mantiene en `TAXONOMY.md`. Las implementaciones deben tratar ese archivo como la fuente de verdad de la versión vigente.

## 5. Implementación en MediaWiki (referencia)
- Cada nodo CEA es una categoría `Categoría:CEA <código> <nombre>`, anidada bajo la categoría del código madre.
- Los artículos se etiquetan con su categoría CEA principal (y las secundarias opcionales).
- Los códigos se asignan mediante una correspondencia a partir de señales existentes (tipo de ficha, categorías). Véase `reference-implementation/`.
- Los elementos sin asignación fiable van a una categoría de seguimiento `CEA sin asignar`; nunca se descartan en silencio.

## 6. Gobernanza y versionado
- Versionado semántico. Los refinamientos aditivos suben la versión menor; las renumeraciones que rompen códigos existentes suben la mayor.
- Los cambios se registran en `CHANGELOG.md`.
