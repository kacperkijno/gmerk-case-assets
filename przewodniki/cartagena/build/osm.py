# -*- coding: utf-8 -*-
"""Pobieranie geometrii z OpenStreetMap (ODbL, © OpenStreetMap contributors).

Overpass bywa niedostępny w zamkniętych środowiskach, więc korzystamy wyłącznie
z oficjalnego API 0.6 (`/map?bbox=`) i z Nominatim. Duże obszary dzielimy na
kafle; z każdego kafla zapisujemy w cache'u już *przefiltrowane* obiekty, żeby
nie trzymać na dysku dziesiątek megabajtów XML-a.
"""
import json
import math
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from geom import chains, join_rings, signed_area  # noqa: F401

API = "https://api.openstreetmap.org/api/0.6"
# Instancje Overpass, w kolejności prób. Zapytania wysyłamy POST-em:
# GET na dłuższym zapytaniu potrafi dostać 504 od bramy pośredniczącej.
OVERPASS = ("https://overpass.kumi.systems/api/interpreter",
            "https://overpass-api.de/api/interpreter")
NOMINATIM = "https://nominatim.openstreetmap.org"
UA = "gmerk-cartagena-guide-mapbuild/1.0 (+https://gmerk.no)"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "osm-cache")

ATTRIBUTION = "© OpenStreetMap contributors (ODbL)"

# Klucze, których wartości w ogóle nas interesują przy rysowaniu map.
KEEP_KEYS = (
    "name", "highway", "natural", "waterway", "landuse", "leisure", "place",
    "barrier", "historic", "man_made", "building", "amenity", "tourism",
    "aeroway", "bridge", "tunnel", "area", "boundary", "admin_level", "type",
    "water", "wetland", "religion", "ref",
)


def _sleep(t):
    if t > 0:
        time.sleep(t)


def _fetch(url, tries=5, pause=1.0, data=None):
    """GET (albo POST, gdy podano `data`) z ponawianiem; zwraca bajty."""
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data,
                                         headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            _sleep(pause)
            return data
        except Exception as e:                                  # noqa: BLE001
            last = e
            _sleep(min(2 ** i, 16))
    raise RuntimeError(f"nie udało się pobrać {url}: {last}")


# ---------------------------------------------------------------- parsowanie
def _tags(el):
    t = {}
    for x in el.findall("tag"):
        k = x.get("k")
        if k in KEEP_KEYS:
            t[k] = x.get("v")
    return t


def parse_osm(xml_bytes, want):
    """XML OSM → {'nodes':{id:(lat,lon)}, 'ways':{id:{...}}, 'rels':{id:{...}}}.

    `want(tags)` decyduje, czy dany way/relację w ogóle zapisujemy.
    """
    root = ET.fromstring(xml_bytes)
    nodes, pnodes = {}, {}
    for n in root.findall("node"):
        nid = int(n.get("id"))
        nodes[nid] = (float(n.get("lat")), float(n.get("lon")))
        tg = _tags(n)
        if tg.get("name"):                       # samodzielne punkty (POI)
            pnodes[nid] = {"tags": tg, "at": nodes[nid]}

    ways, used = {}, set()
    for w in root.findall("way"):
        tg = _tags(w)
        refs = [int(x.get("ref")) for x in w.findall("nd")]
        if not want(tg):
            continue
        ways[int(w.get("id"))] = {"tags": tg, "nodes": refs}
        used.update(refs)

    rels = {}
    for r in root.findall("relation"):
        tg = _tags(r)
        if tg.get("type") != "multipolygon" or not want(tg):
            continue
        members = [(m.get("type"), int(m.get("ref")), m.get("role") or "outer")
                   for m in r.findall("member")]
        rels[int(r.get("id"))] = {"tags": tg, "members": members}
        for mt, mref, _ in members:
            if mt == "way" and mref in ways:
                used.update(ways[mref]["nodes"])

    # relacje mogą wskazywać na ways odfiltrowane wyżej — dociągamy ich geometrię
    for r in root.findall("way"):
        wid = int(r.get("id"))
        if wid in ways:
            continue
        refs = [int(x.get("ref")) for x in r.findall("nd")]
        for rel in rels.values():
            if any(mt == "way" and mref == wid for mt, mref, _ in rel["members"]):
                ways[wid] = {"tags": _tags(r), "nodes": refs}
                used.update(refs)
                break

    return {"nodes": {k: v for k, v in nodes.items() if k in used},
            "ways": ways, "rels": rels, "pois": pnodes}


def merge(dst, src):
    for k in ("nodes", "ways", "rels", "pois"):
        dst.setdefault(k, {}).update(src.get(k, {}))
    return dst


def empty():
    return {"nodes": {}, "ways": {}, "rels": {}, "pois": {}}


# ------------------------------------------------------------------ pobrania
def fetch_bbox(s, w, n, e, want, tag=""):
    """Jeden prostokąt z /map?bbox= — z cache'em przefiltrowanego wyniku."""
    os.makedirs(CACHE, exist_ok=True)
    key = f"{tag}_{s:.5f}_{w:.5f}_{n:.5f}_{e:.5f}.json"
    p = os.path.join(CACHE, key)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        return _keyed(d)

    url = f"{API}/map?bbox={w:.6f},{s:.6f},{e:.6f},{n:.6f}"
    data = parse_osm(_fetch(url), want)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    return data


def _keyed(d):
    return {"nodes": {int(k): tuple(v) for k, v in d["nodes"].items()},
            "ways": {int(k): v for k, v in d["ways"].items()},
            "rels": {int(k): v for k, v in d["rels"].items()},
            "pois": {int(k): v for k, v in d.get("pois", {}).items()}}


def fetch_area(bbox, want, tag="", tile=0.012, quiet=False):
    """Duży obszar w kaflach (limit API: 0,25 deg^2 i 50 000 węzłów na żądanie)."""
    s, w, n, e = bbox
    ny = max(1, math.ceil((n - s) / tile))
    nx = max(1, math.ceil((e - w) / tile))
    out, total = empty(), nx * ny
    for iy in range(ny):
        for ix in range(nx):
            s0 = s + (n - s) * iy / ny
            n0 = s + (n - s) * (iy + 1) / ny
            w0 = w + (e - w) * ix / nx
            e0 = w + (e - w) * (ix + 1) / nx
            merge(out, fetch_bbox(s0, w0, n0, e0, want, tag))
            if not quiet:
                i = iy * nx + ix + 1
                print(f"\r  {tag}: kafel {i}/{total}  "
                      f"ways={len(out['ways'])}", end="", flush=True)
    if not quiet:
        print()
    return out


def overpass(query, tag, tries=2, timeout=240):
    """Zapytanie Overpass QL → elementy JSON, z cache'em na dysku.

    Publiczne instancje bywają przeciążone i potrafią przyjąć połączenie,
    a potem milczeć — stąd krótkie ponawianie, twardy limit czasu i wypisywanie
    postępu, żeby nie wyglądało to na zawieszenie.
    """
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, f"ovp_{_slug(tag)}.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    body = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for url in OVERPASS:
        host = urllib.parse.urlparse(url).netloc
        for i in range(tries):
            t0 = time.time()
            print(f"     Overpass: {host}, próba {i + 1}/{tries}…",
                  end="", flush=True)
            try:
                req = urllib.request.Request(url, data=body,
                                             headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    raw = r.read()
                els = json.loads(raw)["elements"]
            except Exception as e:                              # noqa: BLE001
                last = e
                print(f" nie wyszło po {time.time() - t0:.0f} s "
                      f"({type(e).__name__})")
                _sleep(5)
                continue
            print(f" {len(els)} elementów w {time.time() - t0:.0f} s")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(els, f, separators=(",", ":"))
            return els
    raise RuntimeError(f"Overpass nie odpowiedział: {last}")


def from_overpass(els, want):
    """Elementy Overpass (`out body geom`) → ta sama struktura co parse_osm."""
    nodes, ways, pois = {}, {}, {}
    for e in els:
        tg = {k: v for k, v in (e.get("tags") or {}).items() if k in KEEP_KEYS}
        if e["type"] == "node":
            nodes[e["id"]] = (e["lat"], e["lon"])
            if tg.get("name"):
                pois[e["id"]] = {"tags": tg, "at": (e["lat"], e["lon"])}
        elif e["type"] == "way" and e.get("geometry") and want(tg):
            ids = e.get("nodes") or list(range(len(e["geometry"])))
            for i, g in zip(ids, e["geometry"]):
                nodes[i] = (g["lat"], g["lon"])
            ways[e["id"]] = {"tags": tg, "nodes": list(ids)}
    return {"nodes": nodes, "ways": ways, "rels": {}, "pois": pois}


def nominatim(query, limit=3):
    """Wyszukanie w Nominatim z geometrią (polygon_geojson)."""
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, "nom_" + _slug(query) + ".json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    qs = urllib.parse.urlencode({
        "q": query, "format": "jsonv2", "polygon_geojson": 1,
        "limit": limit, "addressdetails": 0})
    data = json.loads(_fetch(f"{NOMINATIM}/search?{qs}", pause=1.2))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    return data


def _slug(t):
    return "".join(c if c.isalnum() else "-" for c in t.lower())[:70]


# ------------------------------------------------------------- geometria
def way_coords(data, wid):
    w = data["ways"].get(wid)
    if not w:
        return []
    nd = data["nodes"]
    return [nd[i] for i in w["nodes"] if i in nd]


def is_closed(data, wid):
    w = data["ways"].get(wid)
    return bool(w) and len(w["nodes"]) > 3 and w["nodes"][0] == w["nodes"][-1]


def rings_of_relation(data, rid, role="outer"):
    """Składa pierścienie multipoligonu z członków-ways."""
    rel = data["rels"].get(rid)
    if not rel:
        return []
    segs = [list(data["ways"][ref]["nodes"])
            for mt, ref, rl in rel["members"]
            if mt == "way" and ref in data["ways"] and rl == role]
    return [[data["nodes"][i] for i in ring if i in data["nodes"]]
            for ring in join_rings(segs)]


# ----------------------------------------------------------- Nominatim
def nominatim_lookup(osm_ids, tag="lookup"):
    """Geometria konkretnych obiektów OSM (np. 'R18430278,W25896749').

    /lookup przyjmuje do 50 identyfikatorów naraz, więc jedno wywołanie
    wystarcza na całą mapę — to mieści się w zasadach użycia Nominatim.
    """
    os.makedirs(CACHE, exist_ok=True)
    ids = ",".join(osm_ids) if not isinstance(osm_ids, str) else osm_ids
    p = os.path.join(CACHE, f"nomlookup_{_slug(tag)}.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    out = []
    lst = ids.split(",")
    for i in range(0, len(lst), 45):
        qs = urllib.parse.urlencode({
            "osm_ids": ",".join(lst[i:i + 45]), "format": "jsonv2",
            "polygon_geojson": 1, "polygon_threshold": 0})
        out += json.loads(_fetch(f"{NOMINATIM}/lookup?{qs}", pause=1.2))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    return out


def geojson_rings(geo):
    """GeoJSON (Polygon/MultiPolygon/LineString/...) → listy punktów (lat, lon)."""
    if not geo:
        return []
    t, c = geo.get("type"), geo.get("coordinates")
    if t == "Point":
        return [[(c[1], c[0])]]
    if t == "LineString":
        return [[(p[1], p[0]) for p in c]]
    if t == "MultiLineString":
        return [[(p[1], p[0]) for p in line] for line in c]
    if t == "Polygon":
        return [[(p[1], p[0]) for p in ring] for ring in c]
    if t == "MultiPolygon":
        return [[(p[1], p[0]) for p in ring] for poly in c for ring in poly]
    return []


def outer_ring(geo):
    """Największy pierścień — zwykle obrys zewnętrzny."""
    rings = geojson_rings(geo)
    return max(rings, key=lambda r: abs(signed_area(r)) if len(r) > 2 else 0,
               default=[])
