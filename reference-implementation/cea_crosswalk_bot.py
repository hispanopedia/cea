#!/usr/bin/env python3
"""
CDE (Clasificación Decimal Enciclopédica) crosswalk bot.

Assigns each ns0 article a primary CDE class (+ up to 2 secondaries) from its
infobox type and categories. DRY by default — produces a state DB, per-class
counts and a random sample, and writes NOTHING to the wiki until validated.

Signals (no per-article getText; all from the DB):
  - primary infobox  (templatelinks 'Ficha de X', subpages folded to parent)
  - categories       (categorylinks, for person/taxon refinement + fallback)

Phases:
  classify : compute assignments into state DB (no wiki writes)
  sample   : print N random assignments for hand-validation
  counts   : per primary-class counts + coverage stats
  (writing to the wiki is a later phase, added only after sample sign-off)
"""
import argparse, re, sqlite3, subprocess, sys

DB_NAME = "mw_dbes_wd"
STATE = "/home/admin/bot/state_cea.db"

# Translate the legacy 0-9 codes the classifier emits into the locked CEA 17-class codes.
REMAP = {
    "9.1":"17.01","9.2":"17.02","9.3":"17.03","9.4":"17.04","9.5":"17.06","9.6":"17.07",
    "9.7":"17.08","9.8":"17.09","9.91":"17.10","9.92":"17.11","9.93":"17.12","9.9":"17.14",
    "4.1":"09.01","4.2":"09.02","4.3":"09.03","4.4":"09.04","4.5":"09.05","4.6":"10",
    "4.7":"09.11","4.8":"09.10","4":"09",
    "3.1":"08.01","3.2":"08.09","3.3":"08.07","3":"08",
    "0.2":"01.02","0.3":"01.04","0.4":"01.05","0.5":"01.06","0.6":"01.08","0":"01",
    "7.1":"15.01","7.2":"15.02","7.3":"15.04","7.4":"15.06","7.5":"14.02","7.6":"14.05","7.7":"15.08","7":"15",
    "8.1":"16.05","8.2":"16.07","8.3":"16.08","8.4":"16.09","8.5":"16.10","8.6":"16.11","8":"16",
    "5.5":"11.06","5.6":"11.09","5.7":"11.10","5.8":"11.11","5.9":"11.15","5":"11",
    "6.1":"12.01","6.2":"13.03","6.4":"12.05","6.5":"12.03","6.7":"12.09","6":"12",
    "2.1":"04.05","2.3":"05","2.4":"06","2.8":"07","2.83":"07.03","2":"04",
    "1.1":"02.01","1.4":"03.01","1":"03",
}

# ---- infobox -> (primary class, [secondary classes]); lower prio = wins when several present
# prio: biographical/specific first, generic/containers last
INFOBOX = {
    # biographies (profession refined later via categories; default subclass here)
    "Ficha de escritor":        ("9.1", ["3"],   10),
    "Ficha de artista":         ("9.2", ["4"],   10),
    "Ficha de actor":           ("9.4", ["4"],   10),
    "Ficha de militar":         ("9.7", ["6.7"], 10),
    "Ficha de noble":           ("9.91",["2.1"], 10),
    "Ficha de líder cristiano": ("9.8", ["1"],   10),
    "Ficha de líder religioso": ("9.8", ["1"],   10),
    "Ficha de autoridad":       ("9.6", ["2.1"], 12),
    "Ficha de persona":         ("9.9", [],      40),  # refined by categories
    # works / media / arts
    "Ficha de película":        ("4.4", [],      10),
    "Ficha de álbum":           ("4.3", [],      10),
    "Ficha de sencillo":        ("4.3", [],      10),
    "Ficha de canción":         ("4.3", [],      10),
    "Ficha de libro":           ("3.2", [],      10),
    "Ficha de obra de arte":    ("4.1", [],      10),
    "Ficha de obra musical":    ("4.3", [],      10),
    "Ficha de periódico":       ("0.5", [],      10),
    "Ficha de revista":         ("0.5", [],      10),
    # buildings / heritage
    "Ficha de edificio religioso": ("4.2", ["1"], 10),
    "Ficha de templo":          ("4.2", ["1"],  10),
    "Ficha de edificio":        ("4.2", [],      15),
    "Ficha de estructura":      ("4.2", [],      18),
    "Ficha de monumento":       ("4.2", [],      12),
    "Ficha de museo":           ("0.6", ["4"],  10),
    "Ficha de puente":          ("6.4", [],      10),
    "Ficha de faro":            ("6.4", [],      10),
    "Ficha de bien de interés cultural": ("4.2", [], 30),
    # geography / places
    "Ficha de país":            ("7.1", [],      10),
    "Ficha de entidad subnacional": ("7.2", [],  20),
    "Ficha de localidad de España": ("7.3", [],  10),
    "Ficha de localidad":       ("7.3", [],      12),
    "Ficha de barrio":          ("7.3", [],      10),
    "Ficha de antigua entidad territorial": ("7.2", ["8.1"], 14),
    "Ficha de cuerpo de agua":  ("7.4", [],      10),
    "Ficha de montaña":         ("7.4", [],      10),
    "Ficha de cordillera":      ("7.4", [],      10),
    "Ficha de isla":            ("7.4", [],      10),
    "Ficha de archipiélago":    ("7.4", [],      10),
    "Ficha de cabo":            ("7.4", [],      10),
    "Ficha de playa":           ("7.4", [],      10),
    "Ficha de accidente geográfico": ("7.4", [], 12),
    "Ficha de embalse":         ("7.4", ["6.5"], 10),
    "Ficha de espacio natural": ("7.7", ["5.9"], 10),
    "Ficha de parque":          ("7.7", [],      12),
    "Ficha de cartografía":     ("7.6", [],      10),
    # history / events
    "Ficha de conflicto":       ("8.3", [],      10),
    "Ficha de conflicto militar": ("8.3", [],    10),
    "Ficha de estructura militar": ("6.7", ["8"],10),
    "Ficha de unidad militar":  ("6.7", [],      12),
    "Ficha de yacimiento arqueológico": ("8.5", [], 10),
    "Ficha de documento":       ("8.4", [],      10),
    "Ficha de terremoto":       ("5.5", ["8.2"], 10),
    # science / nature / tech
    "Ficha de taxón":           ("5.6", [],      10),  # refined plant/animal via categories
    "Ficha de proteína":        ("5.6", [],      10),
    "Ficha de enfermedad":      ("6.2", [],      10),
    "Ficha de barco":           ("6.4", [],      12),
    "Ficha de estación":        ("6.4", [],      10),
    "Ficha de vía de transporte": ("6.4", [],    10),
    "Ficha de aeropuerto":      ("6.4", [],      10),
    # society / education / orgs
    "Ficha de universidad":     ("2.83",[],      10),
    "Ficha de centro educativo":("2.83",[],      10),
    "Ficha de organización":    ("2.1", [],      25),
    "Ficha de organismo oficial":("2.1", [],     14),
    "Ficha de partido político":("2.1", [],      10),
    "Ficha de título nobiliario":("2.1", [],     14),
    "Ficha de fiesta":          ("4.8", ["1"],   12),
}

# Ficha de persona refinement: (category keyword regex) -> (9.x subclass, [secondary subject])
PROFESSION = [
    (r"escritor|escritora|novelist|poet|poeta|dramaturg|filólog|ensayist|periodist", "9.1", ["3"]),
    (r"pintor|pintora|escultor|fotógraf|artista|arquitect|grabador|dibujant|diseñador", "9.2", ["4"]),
    (r"compositor|música|músico|cantante|cantautor|pianist|guitarrist|director de orquesta", "9.3", ["4.3"]),
    (r"actor|actriz|cineast|director de cine|guionist|bailar|coreógraf|presentador", "9.4", ["4"]),
    (r"científic|física|físico|químic|matemátic|biólog|astrónom|investigador|geólog|ingenier|médic|inventor", "9.5", ["5"]),
    (r"polític|presidente|ministr|alcald|diputad|senador|gobernad|diplomátic|rey |reina|monarca", "9.6", ["2.1"]),
    (r"militar|general|almirante|coronel|capitán|soldado|conquistador", "9.7", ["6.7"]),
    (r"obispo|arzobispo|papa|cardenal|santo|santa|beat|mártir|sacerdote|monj|fraile|teólog|religios", "9.8", ["1"]),
    (r"explorador|navegante|descubridor|cosmógraf", "9.93", ["8"]),
    (r"noble|rey |reina|infante|duque|conde|marqués|monarca|emperador", "9.91", ["2.1"]),
    (r"empresari|economist|banquero|comerciante", "9.92", ["2.4"]),
    (r"deportist|futbolist|ciclist|tenist|atleta|jugador", "9.3", ["4.6"]),
]
TAXON = [
    (r"\bave|aves|pájaro|mamífer|pez|peces|reptil|anfibio|insecto|molusco|animal|fauna|artrópod", "5.8"),
    (r"planta|flora|árbol|orquíde|hongo|musgo|helecho|angiosperm|gimnosperm", "5.7"),
]

def sql(query):
    p = subprocess.run(["sudo","mariadb",DB_NAME,"-N","-e",query],
                       capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        sys.exit("DB query failed: " + (p.stderr or p.stdout))
    return p.stdout

def db():
    c = sqlite3.connect(STATE); c.execute("PRAGMA journal_mode=WAL")
    c.execute("""CREATE TABLE IF NOT EXISTS art(
        page_id INTEGER PRIMARY KEY, title TEXT, primary_cls TEXT,
        secondary TEXT, source TEXT)""")
    c.commit(); return c

def fold(name):
    """Fold 'Ficha de X/subpage' -> 'Ficha de X'; underscores -> spaces."""
    n = name.replace("_", " ")
    return n.split("/")[0]

def phase_classify(c):
    print("loading article infoboxes ...", flush=True)
    rows = sql(
        "SELECT tl.tl_from, lt.lt_title FROM templatelinks tl "
        "JOIN linktarget lt ON tl.tl_target_id=lt.lt_id "
        "JOIN page p ON p.page_id=tl.tl_from AND p.page_namespace=0 AND p.page_is_redirect=0 "
        r"WHERE lt.lt_namespace=10 AND lt.lt_title LIKE 'Ficha\_de\_%';")
    art_ib = {}
    for line in rows.splitlines():
        pid, name = line.split("\t", 1)
        ib = fold(name)
        if ib in INFOBOX:
            art_ib.setdefault(int(pid), set()).add(ib)
    print(f"  {len(art_ib)} articles with a mapped infobox", flush=True)

    # titles for all ns0 non-redirect
    print("loading titles ...", flush=True)
    titles = {}
    for line in sql("SELECT page_id,page_title FROM page WHERE page_namespace=0 AND page_is_redirect=0;").splitlines():
        pid, t = line.split("\t", 1); titles[int(pid)] = t

    # categories only for persons, taxa (refinement) and no-infobox (fallback)
    need_person = {pid for pid, ibs in art_ib.items() if "Ficha de persona" in ibs}
    need_taxon  = {pid for pid, ibs in art_ib.items() if "Ficha de taxón" in ibs}
    need_esub   = {pid for pid, ibs in art_ib.items() if "Ficha de entidad subnacional" in ibs}
    need_libro  = {pid for pid, ibs in art_ib.items() if "Ficha de libro" in ibs}
    need_doc    = {pid for pid, ibs in art_ib.items() if "Ficha de documento" in ibs}
    no_ib = set(titles) - set(art_ib)
    need = need_person | need_taxon | need_esub | need_libro | need_doc | no_ib
    print(f"  fetching categories for {len(need)} articles (persons/taxa/no-infobox) ...", flush=True)
    art_cats = {}
    for line in sql(
        "SELECT cl.cl_from, lt.lt_title FROM categorylinks cl "
        "JOIN linktarget lt ON cl.cl_target_id=lt.lt_id "
        "JOIN page p ON p.page_id=cl.cl_from AND p.page_namespace=0 AND p.page_is_redirect=0 "
        "WHERE lt.lt_namespace=14;").splitlines():
        pid, ct = line.split("\t", 1); pid = int(pid)
        if pid in need:
            art_cats.setdefault(pid, []).append(ct.replace("_", " ").lower())

    def refine_person(pid):
        cats = " ".join(art_cats.get(pid, []))
        for rgx, sub, sec in PROFESSION:
            if re.search(rgx, cats):
                return sub, list(sec)
        return "9.9", []

    def refine_taxon(pid):
        cats = " ".join(art_cats.get(pid, []))
        for rgx, sub in TAXON:
            if re.search(rgx, cats):
                return sub
        return "5.6"

    def refine_esub(pid):
        cats = " ".join(art_cats.get(pid, []))
        if re.search(r"municipios de|localidades de|pedanías|pueblos de|ciudades de|"
                     r"comunas de|distritos de|parroquias de|corregimientos de|villas de|"
                     r"cabeceras|juntas vecinales", cats):
            return "7.3"
        return "7.2"

    # a book/work is classified by its SUBJECT, not blanket-literature (correction #1)
    LIBRO = [
        (r"ingeniería|tecnología|mecánica|máquinas|náutic", "6.1"),
        (r"medicina|médic|farmac|anatomía|cirugía", "6.2"),
        (r"libros de ciencia|matemátic|física|químic|biolog|astronom|naturalist|botánic|zoolog|historia natural", "5"),
        (r"libros de historia|históric|crónica|crónicas", "8"),
        (r"religios|teológic|teología|bíblic|hagiograf|devocionario|litúrgic|sagrad", "1.4"),
        (r"filosofía|filosófic|pensamiento", "1.1"),
        (r"derecho|jurídic|legislación|jurisprudencia|código", "2.3"),
        (r"polític|económic|economía", "2"),
        (r"libros de arte|arquitectura|de música|de pintura", "4"),
        (r"libros de viaj|geografía|cartografía", "7"),
    ]
    def refine_libro(pid):
        cats = " ".join(art_cats.get(pid, []))
        for rgx, cls in LIBRO:
            if re.search(rgx, cats):
                return cls
        return "3.2"   # default: literary work

    # a treaty/document: legal-constitutional -> 2, historical -> 8.4 (correction #2)
    def refine_documento(pid):
        cats = " ".join(art_cats.get(pid, []))
        if re.search(r"constituci[oó]n|convención|convenio|legislación|código|leyes|"
                     r"derecho|unión europea|derechos humanos", cats):
            return "2.3"
        return "8.4"

    PERSON_HINT = re.compile(r"nacidos (en|por)|fallecidos (en|por)|personas (vivas|de|del|por)|"
                             r"hombres |mujeres |biografía", re.IGNORECASE)
    def fallback(pid, title):
        cats = " ".join(art_cats.get(pid, []))
        # 1) person first, but ONLY with a real person signal (nacidos/fallecidos/
        #    personas) — a bare profession stem also matches topical cats (Mariachi,
        #    Matemáticas), so it can't be the trigger; it only picks the subclass.
        if PERSON_HINT.search(cats):
            for rgx, sub, sec in PROFESSION:
                if re.search(rgx, cats):
                    return sub, list(sec)
            return "9.9", []
        # 2) year / date / chronology pages -> cronología
        tl = title.replace("_", " ")
        if (re.fullmatch(r"\d{1,4}", title) or re.fullmatch(r"\d{1,2}_de_[a-zé]+", title)
                or tl in ("Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio",
                          "Agosto","Septiembre","Octubre","Noviembre","Diciembre")
                or re.match(r"(Siglo |Años |Década|Milenio|Era com|Anexo:Tabla anual|"
                            r"Anexo:Año bisiesto|Calendario )", tl)
                or re.search(r"a\. ?C\.$", tl)):
            return "8.6", []
        # 3) awards/prizes -> classified by the field they honor (correction #5)
        if re.search(r"premios", cats) or tl.startswith("Premio "):
            if re.search(r"literari|de las letras|de literatura|de poesía|de novela", cats): return "3", []
            if re.search(r"de cine|cinematográfic|musicales|de música|artístic|de teatro|de pintura|de fotografía|deportiv", cats): return "4", []
            if re.search(r"de periodismo|de comunicación", cats): return "0.5", []
            if re.search(r"científic|de ciencia|de física|de químic|de medicina|de investigación", cats): return "5", []
            if re.search(r"de arquitectura", cats): return "4.2", []
            if re.search(r"de economía|de la paz|derechos humanos", cats): return "2", []
        # 4) treaties / legal-constitutional documents (correction #2)
        if re.search(r"constituci[oó]n|convención|convenio|legislación|código (civil|penal|de comercio)|"
                     r"derecho de|leyes de|unión europea|derechos humanos", cats):
            return "2.3", []
        if (re.match(r"(Tratado |Paz de |Capitulación|Concordato|Bula |Real cédula|Pragmática|Armisticio)", tl)
                or re.search(r"tratados de|paz de |concordato", cats)):
            return "8.4", []
        # 5) topical fallback (bare 'siglo' excluded — it appears on profession cats)
        table = [
            (r"deporte|deportiv|fútbol|futbolist|baloncesto|balonmano|voleibol|rugby|béisbol|tenis|"
             r"ciclis|atletismo|gimnasia|boxeo|natación|olímpic|federación de fútbol|liga de fútbol", "4.6"),   # -> 10
            (r"escritor|novela|poesía|literatura|lingüística|idioma|filolog", "3"),
            (r"película|cine|música|álbum|canción|pintura|escultura|arquitectura|gastronom|teatro|danza|fotografía", "4"),
            (r"filosofía|filósof|filosófic|metafísica|epistemolog|ética|estética|lógica", "1.1"),                # -> 02
            (r"matemátic|física|químic|biolog|botánic|zoolog|especie|astronom|geología|ecología|supercontinente", "5"),
            (r"medicina|enfermedad|ingenier|tecnología|transporte|ferrocarril|agricultura|náutic|moneda|numismática", "6"),
            (r"localidad|municipio|provincia|río|montaña|isla|geografía|país|región|comarca|barrio|condados de", "7"),
            (r"historia|guerra|batalla|imperio|virreinato|revolución|dinastía|reconquista|edad media|edad moderna|antigua roma|arqueológic", "8"),
            (r"religión|iglesia|santo|santa|teología|orden religios|mitología|diócesis|jesuit", "1"),
            (r"universidades de|centros educativos|escuelas de|colegios de|facultades|institutos de enseñanza", "2.83"),
            (r"educación|pedagog|sistema educativo", "2.8"),
            (r"economía|económic|finanzas|banca|empresa|mercado|comercio|hacienda pública", "2.4"),               # -> 06
            (r"política|derecho|ley |partido|sociedad|institucion", "2"),
            (r"informática|biblioteca|enciclopedia|periodismo|revista|periódico|museo", "0"),
        ]
        for rgx, cls in table:
            if re.search(rgx, cats):
                return cls, []
        return None, []

    print("assigning ...", flush=True)
    n = 0
    for pid, t in titles.items():
        ibs = art_ib.get(pid)
        sec = []
        if ibs:
            best = min(ibs, key=lambda x: INFOBOX[x][2])
            prim, sec, _ = INFOBOX[best]; sec = list(sec)
            source = "infobox:" + best
            if best == "Ficha de persona":
                prim, sec = refine_person(pid); source = "persona+cat"
            elif best == "Ficha de taxón":
                prim = refine_taxon(pid); source = "taxón+cat"
            elif best == "Ficha de entidad subnacional":
                prim = refine_esub(pid); source = "esub+cat"
            elif best == "Ficha de libro":
                prim = refine_libro(pid); source = "libro+cat"
            elif best == "Ficha de documento":
                prim = refine_documento(pid); source = "documento+cat"
        else:
            prim, sec = fallback(pid, t)
            source = "cat-fallback" if prim else "sin-asignar"
        prim = (REMAP.get(prim, prim) if prim else None)
        sec = [REMAP.get(s, s) for s in sec]
        c.execute("INSERT OR REPLACE INTO art(page_id,title,primary_cls,secondary,source) VALUES(?,?,?,?,?)",
                  (pid, t, prim, ",".join(sec), source))
        n += 1
        if n % 20000 == 0:
            c.commit(); print(f"  {n}/{len(titles)}", flush=True)
    c.commit()
    print(f"classify done: {n} articles assigned")

def phase_counts(c):
    total = c.execute("SELECT COUNT(*) FROM art").fetchone()[0]
    sa = c.execute("SELECT COUNT(*) FROM art WHERE primary_cls IS NULL").fetchone()[0]
    print(f"total ns0 articles: {total}   sin-asignar: {sa} ({100*sa//max(total,1)}%)")
    print("by primary class (top level):")
    rows = c.execute("SELECT substr(primary_cls,1,2) d, COUNT(*) n FROM art WHERE primary_cls IS NOT NULL GROUP BY d ORDER BY d").fetchall()
    for d, n in rows: print(f"  {d}: {n}")
    print("by source:")
    for s, n in c.execute("SELECT source,COUNT(*) n FROM art GROUP BY source ORDER BY n DESC").fetchall():
        print(f"  {s}: {n}")

def phase_sample(c, n):
    # deterministic-ish spread sample across classes
    rows = c.execute("SELECT title,primary_cls,secondary,source FROM art ORDER BY page_id").fetchall()
    step = max(1, len(rows)//n)
    for t, p, s, src in rows[::step][:n]:
        print(f"  {p or 'SIN-ASIGNAR':6} {('+'+s) if s else '':10} | {t.replace('_',' ')}   [{src}]")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["classify","counts","sample"], required=True)
    ap.add_argument("--n", type=int, default=200)
    a = ap.parse_args()
    c = db()
    if a.phase == "classify": phase_classify(c)
    elif a.phase == "counts": phase_counts(c)
    elif a.phase == "sample": phase_sample(c, a.n)
    c.close()
