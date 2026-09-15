# -*- coding: utf-8 -*-
"""Zamienia surowe dane OpenStreetMap w `maps/osm-data.json` używany przez maps.py.

Uruchomienie wymaga sieci (Overpass i nominatim.openstreetmap.org); wynik jest
wersjonowany w repo, więc sam skład książki działa już offline.

    python3 osm_build.py

Dane: © OpenStreetMap contributors, licencja ODbL.
"""
import json
import math
import os
import unicodedata

import geom
import osm
from geom import centroid, dist_m, simplify

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "maps", "osm-data.json")

# Prostokąty czterech map (s, w, n, e) — patrz maps.py.
BBOX = {
    "1": (10.2860, -75.6180, 10.4520, -75.4900),
    "2": (10.3872, -75.5694, 10.4579, -75.5059),
    "3": (10.4203, -75.5549, 10.4320, -75.5427),
    "4": (10.4164, -75.5506, 10.4273, -75.5417),
}
# Wycinek ze szczegółami (mapy 3 i 4) — z zapasem na obiekty wychodzące poza kadr.
DETAIL = (10.4160, -75.5570, 10.4320, -75.5400)

# Obiekty pobierane po identyfikatorze z Nominatim (geometria = oryginalny OSM).
LOOKUP = {
    "R18430278": "Bahía de Cartagena",
    "R20607558": "Bahía de Las Ánimas",
    "R20607560": "Bahía Interior",
    "R4004791":  "Ciénaga de la Virgen",
    "W25896749": "Laguna del Cabrero",
    "W238972766": "Laguna de Chambacú",
    "W25841555": "Cerro de la Popa",
    "R1643328":  "Bocagrande",
    "R1643334":  "El Laguito",
    "R1643329":  "Castillogrande",
    "R19110567": "Manga",
    "R19110390": "Pie de la Popa",
    "R19135837": "El Cabrero",
    "R19139198": "Centro",
    "R19139197": "Getsemaní",
    "R19138461": "San Diego",
    "R19138463": "La Matuna",
    "W100101180": "Aeropuerto Rafael Núñez",
    "W49551791": "Castillo San Felipe de Barajas",
    "W54977866": "Fuerte de San Sebastián del Pastelillo",
    "W101809402": "Fuerte de San Fernando de Bocachica",
    "W94687123": "Mercado de Bazurto",
    "W25446658": "Playa de Bocagrande",
    "W109198419": "Playa Blanca",
    "R1343457":  "Cartagena de Indias",
    # Gminy sąsiednie — granica gminy Cartagena biegnie po linii brzegowej,
    # więc bez sąsiadów ląd na wschodzie mapy wyszedłby jako woda.
    "R1448412":  "Turbaco",
    "R2460383":  "Turbaná",
    "R1448415":  "Arjona",
    "R1448413":  "Santa Rosa de Lima",
    "R4062807":  "Santa Catalina",
    "R1324937":  "Clemencia",
    "R1448410":  "Villanueva",
}
# Gminy tworzące maskę lądu (poza Cartageną).
NEIGHBOURS = ("R1448412", "R2460383", "R1448415", "R1448413",
              "R4062807", "R1324937", "R1448410")

STREET_CLASS = {
    "motorway": "main", "trunk": "main", "primary": "main",
    "secondary": "main", "secondary_link": "main", "trunk_link": "main",
    "motorway_link": "main", "primary_link": "main",
    "tertiary": "mid", "tertiary_link": "mid", "unclassified": "mid",
    "residential": "mid", "living_street": "mid",
    "pedestrian": "foot", "footway": "foot", "path": "foot",
    "steps": "foot", "service": "minor", "track": "minor",
}


# ------------------------------------------------------------------ pomoce
def rnd(pts, nd=5):
    out, prev = [], None
    for la, lo in pts:
        p = (round(la, nd), round(lo, nd))
        if p != prev:
            out.append([p[0], p[1]])
            prev = p
    return out


def touches(pts, bbox, pad=0.0015):
    return geom.hits(pts, bbox, pad)


# Słowa rodzajowe: plac to nie kościół o tym samym wezwaniu, a baluarte to nie
# brama — bez tego „Bal. de Santo Domingo" skleja się z „Plaza de Santo Domingo".
TYPE_WORDS = {
    "plaza": "plac", "plazuela": "plac", "parque": "plac", "square": "plac",
    "iglesia": "kosciol", "catedral": "kosciol", "convento": "kosciol",
    "capilla": "kosciol", "ermita": "kosciol", "basilica": "kosciol",
    "templo": "kosciol", "claustro": "kosciol", "monasterio": "kosciol",
    "baluarte": "bastion", "bal": "bastion", "bastion": "bastion",
    "puerta": "brama", "portal": "brama",
    "museo": "muzeum", "palacio": "dwor", "casa": "dwor", "casona": "dwor",
    "teatro": "teatr", "torre": "wieza",
    "calle": "ulica", "callejon": "ulica", "camellon": "ulica",
    "muelle": "ulica", "avenida": "ulica", "paseo": "ulica",
    "castillo": "forteca", "fuerte": "forteca", "fortaleza": "forteca",
    "bateria": "forteca",
    "monumento": "pomnik", "estatua": "pomnik", "mercado": "targ",
    "cerro": "wzgorze", "laguna": "woda", "bahia": "woda",
    "edificio": "budynek", "hotel": "hotel", "colegio": "szkola",
    "universidad": "szkola", "escuela": "szkola", "banco": "bank",
    "santuario": "kosciol", "hospital": "szpital", "aeropuerto": "lotnisko",
    "isla": "wyspa", "playa": "plaza_morska", "biblioteca": "biblioteka",
}
STOP = {"de", "la", "el", "los", "las", "del", "y", "a", "en", "i"}


def norm(t):
    """Nazwa → (rodzaj obiektu, zbiór słów kluczowych)."""
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    words = [w for w in "".join(c if c.isalnum() else " " for c in t).split()
             if w and w not in STOP]
    kind = next((TYPE_WORDS[w] for w in words if w in TYPE_WORDS), None)
    keys = {w for w in words if w not in TYPE_WORDS}
    return kind, keys


# ------------------------------------------------------------ wycinek detali
def detail_want(t):
    return bool(t.get("highway") or t.get("building") or t.get("barrier")
                or t.get("historic") or t.get("natural") or t.get("waterway")
                or t.get("leisure") or t.get("place") or t.get("landuse")
                or t.get("man_made") or t.get("amenity") or t.get("tourism"))


DETAIL_QUERY = """[out:json][timeout:180];
(
  way["highway"]({bbox});
  way["building"]({bbox});
  way["barrier"]({bbox});
  way["historic"]({bbox});
  way["natural"]({bbox});
  way["waterway"]({bbox});
  way["landuse"]({bbox});
  way["leisure"]({bbox});
  way["place"]({bbox});
  way["man_made"]({bbox});
  node["name"]({bbox});
);
out body geom;"""


def load_detail():
    """Stare Miasto + Getsemaní — pełny wycinek do map 3 i 4.

    Najpierw oficjalne API 0.6 w kaflach: jest szybkie i zwraca *wszystko*
    z prostokąta, więc nic nie wypadnie przez niedomknięty filtr tagów.
    Gdy jest zablokowane, schodzimy na Overpass (mniej danych do pobrania,
    ale publiczne instancje bywają przeciążone), a na końcu na wcześniej
    zapisany wycinek z `osm-cache/`.
    """
    try:
        return osm.fetch_area(DETAIL, detail_want, "detail", tile=0.012)
    except RuntimeError as err:
        print(f"  ! API 0.6 niedostępne ({err})\n  ! próbuję Overpass")
    try:
        bbox = "{0},{1},{2},{3}".format(*DETAIL)
        els = osm.overpass(DETAIL_QUERY.format(bbox=bbox), "detail")
        return osm.from_overpass(els, detail_want)
    except RuntimeError as err:
        seeds = [f for f in os.listdir(osm.CACHE) if f.startswith("seed_")] \
            if os.path.isdir(osm.CACHE) else []
        if not seeds:
            raise
        print(f"  ! {err}\n  ! korzystam z cache'u: {seeds[0]}")
        d = json.load(open(os.path.join(osm.CACHE, seeds[0]), encoding="utf-8"))
        return osm._keyed(d)


def simplify_keeping(pts, ids, forced, tol_m):
    """Upraszcza polilinię, ale nie rusza węzłów wspólnych z innymi ulicami.

    Bez tego Douglas–Peucker kasuje skrzyżowania i graf ulic rozpada się na
    kawałki — trasy spacerów nie mają wtedy po czym iść.
    """
    cuts = [0] + [i for i in range(1, len(pts) - 1) if ids[i] in forced] \
        + [len(pts) - 1]
    out = []
    for a, b in zip(cuts, cuts[1:]):
        part = simplify(pts[a:b + 1], tol_m)
        out += part if not out else part[1:]
    return out


def junction_nodes(ways):
    """Węzły należące do więcej niż jednej ulicy."""
    seen, twice = set(), set()
    for x in ways.values():
        if x["tags"].get("highway") not in STREET_CLASS:
            continue
        for i in set(x["nodes"]):
            (twice if i in seen else seen).add(i)
    return twice


def extract_detail(d):
    N, Wy = d["nodes"], d["ways"]
    forced = junction_nodes(Wy)
    streets, buildings, walls, coast, squares, districts, water = \
        [], [], [], [], [], {}, []
    seen_sq = set()

    for wid, x in Wy.items():
        t = x["tags"]
        ids = [i for i in x["nodes"] if i in N]
        pts = [N[i] for i in ids]
        if len(pts) < 2 or not touches(pts, DETAIL, 0.002):
            continue
        name = t.get("name", "")

        if t.get("barrier") == "city_wall" or t.get("historic") == "citywalls":
            walls.append(rnd(simplify(pts, 1.0)))
        elif t.get("natural") == "coastline":
            coast.append(rnd(simplify(pts, 2.0)))
        elif t.get("highway") in STREET_CLASS:
            line = simplify_keeping(pts, ids, forced, 1.5)
            streets.append([STREET_CLASS[t["highway"]], rnd(line, 6)])
        elif t.get("building"):
            buildings.append(rnd(simplify(pts, 1.5)))
        elif (t.get("place") == "square" or t.get("leisure") in ("park", "garden")
              or t.get("landuse") == "grass"):
            key = (name, round(centroid(pts)[0], 4))
            if key not in seen_sq:
                seen_sq.add(key)
                squares.append([name, rnd(simplify(pts, 1.5))])
        elif t.get("natural") == "water" or t.get("waterway") == "dock":
            water.append([name, rnd(simplify(pts, 2.0))])
        elif t.get("place") in ("neighbourhood", "suburb", "quarter") and name:
            districts[name] = rnd(simplify(pts, 3.0))

    return dict(streets=streets, buildings=buildings, walls=walls,
                coast=coast, squares=squares, districts=districts,
                water_small=water)


# --------------------------------------------------------------- Nominatim
def load_lookup():
    recs = osm.nominatim_lookup(",".join(LOOKUP), "core")
    out = {}
    for r in recs:
        key = f"{r['osm_type'][0].upper()}{r['osm_id']}"
        rings = [x for x in osm.geojson_rings(r.get("geojson")) if len(x) > 3]
        out[key] = {"name": LOOKUP.get(key, r.get("name", "")),
                    "cat": f"{r.get('category')}/{r.get('type')}",
                    "rings": rings}
    return out


def split_at_jumps(ring, max_m=350.0):
    """Dzieli pierścień granicy gminy na kawałki; długie proste odcinki to
    granice administracyjne na morzu, a nie linia brzegowa."""
    out, cur = [], [ring[0]]
    for i in range(1, len(ring)):
        if dist_m(ring[i - 1], ring[i]) > max_m:
            if len(cur) > 4:
                out.append(cur)
            cur = [ring[i]]
        else:
            cur.append(ring[i])
    if len(cur) > 4:
        out.append(cur)
    return out


# ------------------------------------------- weryfikacja współrzędnych POI
# Punkty spoza wycinka detalicznego, szukane po nazwie w Nominatim.
POI_QUERY = {
    "2.2": "Zapatos Viejos, Cartagena",
    "2.3": "Monasterio de la Popa, Cartagena",
    "2.4": "Casa Museo Rafael Núñez, Cartagena",
    "2.5": "Ermita del Cabrero, Cartagena",
    "2.9": "La Boquilla, Cartagena",
    "4.6": "Callejón Angosto, Getsemaní",
    "4.12": "Centro de Convenciones Cartagena de Indias",
}
# Punkty pobierane wprost z obiektów LOOKUP (środek geometrii).
# Punkty mapy 1 (cieśniny, wyspy, archipelag) to etykiety obszarów, a nie
# obiekty punktowe — zostają tam, gdzie postawił je autor. Wyjątkiem jest
# Fuerte de San Fernando, który w OSM ma własny obrys.
POI_FROM_LOOKUP = {
    "2.1": "W49551791", "2.6": "W94687123",
    "2.7": "W54977866", "2.8": "W100101180", "1.3": "W101809402",
}


# Nazwy, pod którymi obiekt figuruje w OSM, jeśli różnią się od tej z książki.
POI_ALIAS = {
    "3.1":  "Puerta del Reloj",              # OSM nie zna nazwy „Torre del Reloj"
    "3.10": "Palacio de la Inquisión",       # literówka w OSM, ale to ten obiekt
    "3.17": "Gabriel García Márquez",        # prochy w Claustro de La Merced
    "3.23": "Sofitel Legend Santa Clara Cartagena",
    "3.3":  "Portal de los Dulces",
}


def candidates(detail, lookup):
    """Wszystko, co ma nazwę i pozycję — z rodzajem obiektu.

    Ulice o tej samej nazwie sklejamy w jeden ciąg: w OSM „Calle de la Media
    Luna" to kilka odcinków, a środek jednego z nich nie jest środkiem ulicy.
    """
    out = []
    for p in detail.get("pois", {}).values():
        out.append((p["tags"]["name"], [p["at"]], "punkt"))
    N = detail["nodes"]
    roads = {}
    for x in detail["ways"].values():
        nm = x["tags"].get("name")
        pts = [N[i] for i in x["nodes"] if i in N]
        if not nm or not pts:
            continue
        if x["tags"].get("highway"):
            roads.setdefault(nm, []).append([i for i in x["nodes"] if i in N])
        else:
            out.append((nm, pts, "obiekt"))
    for nm, segs in roads.items():
        for ring in geom.join_rings(segs):
            out.append((nm, [N[i] for i in ring], "ulica"))
    for key, v in lookup.items():
        if v["rings"]:
            out.append((v["name"], v["rings"][0], "obszar"))
    return out


# POI, których nazwa opisuje ulicę/ciąg — wtedy wolno dopasować `highway`
# i przyciągnąć znacznik do najbliższego punktu tej ulicy.
# Maksymalne przysunięcie etykiety ulicy do jej osi.
LINEAR_SNAP = 120.0


def nearest_on(pts, at):
    """Najbliższy punkt na polilinii (z rzutem na odcinki)."""
    k = math.cos(math.radians(at[0]))
    best, bd = pts[0], float("inf")
    for i in range(len(pts) - 1):
        (y0, x0), (y1, x1) = pts[i], pts[i + 1]
        dx, dy = (x1 - x0) * k, y1 - y0
        den = dx * dx + dy * dy
        t = 0.0 if den < 1e-18 else max(0.0, min(1.0, (
            ((at[1] - x0) * k) * dx + (at[0] - y0) * dy) / den))
        p = (y0 + (y1 - y0) * t, x0 + (x1 - x0) * t)
        d = dist_m(at, p)
        if d < bd:
            best, bd = p, d
    return best


def midpoint(pts):
    """Punkt w połowie długości polilinii — dobra kotwica etykiety ulicy."""
    seg = [dist_m(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    half, acc = sum(seg) / 2.0, 0.0
    for i, s in enumerate(seg):
        if acc + s >= half:
            f = (half - acc) / s if s else 0.0
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f,
                    pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)
        acc += s
    return pts[len(pts) // 2]


def match_poi(pid, name, at, cands, max_m=700.0):
    """Najbliższy obiekt OSM o zgodnym rodzaju i nazwie.

    Promień jest duży, bo ręczny szkic potrafił się mylić o kilkaset metrów;
    przed fałszywym trafieniem broni wymóg zgodności rodzaju i zawierania nazw.
    """
    kind, want = norm(POI_ALIAS.get(pid, name))
    if not want:
        return None
    best, score = None, 0.0
    for nm, pts, src_kind in cands:
        okind, have = norm(nm)
        if not have or not (want <= have or have <= want):
            continue
        # Rodzaj musi się zgadzać: „Bal. de Santo Domingo" to nie „Plaza…",
        # nie „Edificio Santo Domingo" i nie „Calle de Santo Domingo".
        if kind != okind:
            continue
        # Etykieta ulicy ma zostać tam, gdzie postawił ją autor — tylko
        # przysuwamy ją do osi jezdni. Jeśli punkt w ogóle nie leży przy tej
        # ulicy, to znaczy, że w wycinku mamy tylko jej fragment: odpuszczamy.
        if src_kind == "ulica" and kind == "ulica":
            pos, limit = nearest_on(pts, at), LINEAR_SNAP
        else:
            pos, limit = centroid(pts), max_m
        d = dist_m(at, pos)
        if d > limit:
            continue
        s = len(want & have) / max(len(want | have), 1) + 0.3 * (1 - d / max_m)
        if s > score:
            best, score = (nm, pos, src_kind, d), s
    return best if score >= 0.5 else None


def build_pois(detail, lookup):
    src_of = {}
    # celowo z listy źródłowej, nie z geo.POIS — inaczej każde uruchomienie
    # startowałoby od wyniku poprzedniego
    from geo import _POI_BASE as POIS
    out, report = {}, []
    cands = candidates(detail, lookup)
    for pid, name, la, lo, cat, _anchor in POIS:
        at = (la, lo)
        if pid in POI_FROM_LOOKUP:
            v = lookup.get(POI_FROM_LOOKUP[pid])
            if v and v["rings"]:
                c = centroid(v["rings"][0])
                out[pid] = [round(c[0], 5), round(c[1], 5)]
                src_of[pid] = "osm"
                report.append((pid, name, v["name"], "lookup", dist_m(at, c)))
                continue
        if pid in POI_QUERY:
            res = osm.nominatim(POI_QUERY[pid], limit=1)
            if res:
                c = (float(res[0]["lat"]), float(res[0]["lon"]))
                if dist_m(at, c) < 3000:
                    out[pid] = [round(c[0], 5), round(c[1], 5)]
                    src_of[pid] = "osm"
                    report.append((pid, name, res[0].get("name", ""),
                                   "nominatim", dist_m(at, c)))
                    continue
        m = match_poi(pid, name, at, cands)
        if m:
            nm, pos, src, d = m
            out[pid] = [round(pos[0], 5), round(pos[1], 5)]
            src_of[pid] = "osm"
            report.append((pid, name, nm, src, d))
        else:
            # bez dopasowania zostaje współrzędna ze szkicu (geo._POI_BASE)
            report.append((pid, name, "—", "bez zmian", 0.0))
    _shift_unmatched(POIS, out, report, src_of)
    return out, report, src_of


def _shift_unmatched(base, out, report, src_of, radius_m=500.0, need=3):
    """Punkty, których OSM nie zna, przesuwamy razem z sąsiadami.

    Ręczny szkic był lokalnie spójny, ale przesunięty wobec rzeczywistości.
    Kiedy sąsiednie punkty trafiły na swoje miejsca w OSM, ten sam wektor
    stosujemy do nieodnalezionych — inaczej brama zostałaby obok muru,
    który właśnie przesunął się o 150 m.
    """
    fixed = {pid: (la, lo) for pid, _n, la, lo, _c, _a in base if pid in out}
    rep = {r[0]: r for r in report}
    for pid, _nm, la, lo, _cat, _anc in base:
        if pid in out:
            continue
        deltas = [(out[q][0] - qla, out[q][1] - qlo)
                  for q, (qla, qlo) in fixed.items()
                  if dist_m((la, lo), (qla, qlo)) <= radius_m]
        if len(deltas) < need:
            continue
        deltas.sort(key=lambda d: d[0])
        dla = deltas[len(deltas) // 2][0]
        deltas.sort(key=lambda d: d[1])
        dlo = deltas[len(deltas) // 2][1]
        out[pid] = [round(la + dla, 5), round(lo + dlo, 5)]
        src_of[pid] = "sasiedzi"
        if pid in rep:
            r = rep[pid]
            report[report.index(r)] = (pid, r[1], f"korekta z {len(deltas)} sąsiadów",
                                       "sąsiedzi", dist_m((la, lo), out[pid]))


# ------------------------------------------------------------------- main
def main():
    print("1/3  wycinek szczegółowy (Stare Miasto + Getsemaní)")
    detail = load_detail()
    det = extract_detail(detail)
    print(f"     ulic={len(det['streets'])} budynków={len(det['buildings'])} "
          f"murów={len(det['walls'])} placów={len(det['squares'])} "
          f"linii brzegowej={len(det['coast'])}")

    print("2/3  obiekty nazwane (Nominatim /lookup)")
    lookup = load_lookup()
    print(f"     {len(lookup)} obiektów")

    print("3/3  współrzędne POI")
    pois, report, poi_src = build_pois(detail, lookup)

    coastlines = []
    for key in ("R1343457",):
        for ring in lookup[key]["rings"]:
            for chunk in split_at_jumps(ring):
                coastlines.append(rnd(simplify(chunk, 12.0), 5))

    data = {
        "attribution": osm.ATTRIBUTION,
        "source": "api.openstreetmap.org/api/0.6 + nominatim.openstreetmap.org",
        "bbox": BBOX,
        "detail": det,
        "areas": {k: {"name": v["name"], "cat": v["cat"],
                      "rings": [rnd(simplify(r, 8.0), 5) for r in v["rings"]]}
                  for k, v in lookup.items()},
        "coastlines": coastlines,
        "pois": pois,
        "poi_source": poi_src,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), ensure_ascii=False)
    print(f"\n→ {os.path.relpath(OUT, HERE)}  "
          f"({os.path.getsize(OUT)//1024} KB)")

    print("\nDopasowanie POI do OSM (przesunięcie w metrach):")
    for pid, name, osm_name, src, d in sorted(report, key=lambda r: -r[4]):
        flag = "  <-- SPRAWDZIĆ" if d > 120 else ""
        print(f"  {pid:<5} {name[:30]:<32} {src:<10} {d:6.0f} m  "
              f"{osm_name[:34]}{flag}")


if __name__ == "__main__":
    main()
