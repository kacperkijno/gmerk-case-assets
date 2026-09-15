# -*- coding: utf-8 -*-
"""Generator map wektorowych (SVG) do przewodnika.

Cała geometria — linia brzegowa, mury, ulice, kwartały, place, akweny, obrysy
wysp — pochodzi z OpenStreetMap (`maps/osm-data.json`, patrz `osm_build.py`).
Rysunkowe zostają tylko warstwy autorskie: strzałki ataków na mapie 1,
podwodna tama w Bocagrande, łańcuch w Bocachica, etykiety i trasy spacerów.

Dane: © OpenStreetMap contributors, licencja ODbL.
"""
import math

import geom
import route
from geo import (AREAS, ATTRIBUTION, BBOX, BUILDINGS, COAST, DISTRICTS,
                 GETSEMANI, LA_MATUNA, LAND_KEYS, POIS, ROUTES, SQUARES,
                 STREETS, WALLED_CITY, WALLS, WATER_KEYS, rings)

C = dict(
    paper="#FBF7EF", land="#F2EADA", land2="#E9DFCB", water="#CFE0DF",
    water2="#B9D2D2", wall="#8A4A2E", wallf="#D9BFA6", ink="#23201C",
    muted="#8A8175", accent="#B4593A", teal="#1F4E5A", gold="#A98430",
    grid="#E3D8C3", block="#DED0B2",
)
CAT = dict(hist="#B4593A", plaza="#A98430", fort="#7A3E22",
           view="#1F4E5A", life="#3F7A5E", gate="#6B4E9E")

P = {p[0]: p for p in POIS}

# Grubość kreski ulicy wg klasy z OSM.
STREET_W = {"main": 2.0, "mid": 1.15, "minor": 0.7, "foot": 0.55}


class Proj:
    def __init__(self, bbox, w, h, pad=14):
        (la0, lo0, la1, lo1) = bbox
        self.la0, self.lo0, self.la1, self.lo1 = la0, lo0, la1, lo1
        k = math.cos(math.radians((la0 + la1) / 2))
        dw, dh = (lo1 - lo0) * k, (la1 - la0)
        s = min((w - 2 * pad) / dw, (h - 2 * pad) / dh)
        self.s, self.k = s, k
        self.ox = pad + ((w - 2 * pad) - dw * s) / 2
        self.oy = pad + ((h - 2 * pad) - dh * s) / 2
        self.w, self.h = w, h

    def __call__(self, lat, lon):
        return (self.ox + (lon - self.lo0) * self.k * self.s,
                self.oy + (self.la1 - lat) * self.s)

    def metres(self, m):          # długość m metrów w jednostkach SVG
        return (m / 111320.0) * self.s

    @property
    def bbox(self):
        return (self.la0, self.lo0, self.la1, self.lo1)


def frame(bbox, w=560, wmin=460, hmin=440, hmax=650):
    """Płótno dopasowane do proporcji kadru.

    Najpierw próbujemy zwęzić rysunek (książka skaluje mapy do szerokości
    kolumny, a wysokość ma limit 122 mm); dopiero gdy zrobiłby się za wąski,
    poszerzamy sam kadr. Dzięki temu mapa wypełnia pole i nie zostaje pusty
    pas papieru.
    """
    s, lo0, n, lo1 = bbox
    k = math.cos(math.radians((s + n) / 2))
    hm, wm = (n - s), (lo1 - lo0) * k
    h = w * hm / wm
    if h > hmax:
        w2 = hmax * wm / hm
        if w2 >= wmin:
            return bbox, int(round(w2)), hmax
        need = hm * wmin / hmax / k
        c = (lo0 + lo1) / 2
        return (s, c - need / 2, n, c + need / 2), wmin, hmax
    if h < hmin:
        need = wm * hmin / w
        c = (s + n) / 2
        return (c - need / 2, lo0, c + need / 2, lo1), w, hmin
    return bbox, w, int(round(h))


def path(pr, pts, close=True):
    if len(pts) < 2:
        return ""
    d = "".join(("M" if i == 0 else "L") + f"{pr(*p)[0]:.1f},{pr(*p)[1]:.1f}"
                for i, p in enumerate(pts))
    return d + ("Z" if close else "")


def paths(pr, polys, close=True):
    return "".join(path(pr, p, close) for p in polys if len(p) > 1)


def smooth(pr, pts):
    """Łagodna polilinia (Catmull-Rom → Bézier) dla tras spacerowych."""
    q = [pr(*p) for p in pts]
    if len(q) < 3:
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in q)
    d = f"M{q[0][0]:.1f},{q[0][1]:.1f}"
    for i in range(len(q) - 1):
        p0 = q[i - 1] if i else q[0]
        p1, p2 = q[i], q[i + 1]
        p3 = q[i + 2] if i + 2 < len(q) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += (f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} "
              f"{p2[0]:.1f},{p2[1]:.1f}")
    return d


def marker(x, y, label, cat, r=8.2):
    col = CAT.get(cat, C["accent"])
    fs = 8.0 if len(label) <= 2 else 6.9
    return (f'<g><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" '
            f'stroke="{col}" stroke-width="1.9"/>'
            f'<text x="{x:.1f}" y="{y + fs*0.36:.1f}" text-anchor="middle" '
            f'font-family="Archivo, sans-serif" font-size="{fs}" '
            f'font-weight="600" fill="{col}">{label}</text></g>')


def area_label(x, y, t, size=10, col=None, ls=2.2, op=1.0, anchor="middle"):
    """Rozstrzelenie robimy WŁASNYMI spacjami, nie letter-spacing: renderery
    SVG liczą szerokość tekstu bez letter-spacing i psują wyśrodkowanie."""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-family="Archivo, sans-serif" font-size="{size}" '
            f'font-weight="600" letter-spacing="{ls}" fill-opacity="{op}" '
            f'fill="{col or C["muted"]}">{t}</text>')


def scalebar(pr, x, y, metres=200):
    L = pr.metres(metres)
    return (f'<g stroke="{C["ink"]}" stroke-width="1.1">'
            f'<line x1="{x}" y1="{y}" x2="{x+L:.1f}" y2="{y}"/>'
            f'<line x1="{x}" y1="{y-3}" x2="{x}" y2="{y+3}"/>'
            f'<line x1="{x+L:.1f}" y1="{y-3}" x2="{x+L:.1f}" y2="{y+3}"/></g>'
            f'<text x="{x+L/2:.1f}" y="{y-6}" text-anchor="middle" '
            f'font-family="Archivo, sans-serif" font-size="7.5" '
            f'fill="{C["muted"]}">{metres} m</text>')


def north(x, y):
    return (f'<g><path d="M{x},{y-13} L{x-4.5},{y+5} L{x},{y+1.6} '
            f'L{x+4.5},{y+5} Z" fill="{C["ink"]}"/>'
            f'<text x="{x}" y="{y+15}" text-anchor="middle" '
            f'font-family="Archivo, sans-serif" font-size="8" '
            f'font-weight="600" fill="{C["ink"]}">N</text></g>')


def credit(w, h):
    """Atrybucja wymagana licencją ODbL."""
    return (f'<text x="{w-8}" y="{h-7}" text-anchor="end" '
            f'font-family="Archivo, sans-serif" font-size="5.6" '
            f'fill="{C["muted"]}" fill-opacity=".85">{ATTRIBUTION}</text>')


def head(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">'
            f'<defs><pattern id="hatch" width="5" height="5" '
            f'patternTransform="rotate(45)" patternUnits="userSpaceOnUse">'
            f'<line x1="0" y1="0" x2="0" y2="5" stroke="{C["wall"]}" '
            f'stroke-width="1.5" opacity=".30"/></pattern>'
            f'<pattern id="wave" width="14" height="10" '
            f'patternUnits="userSpaceOnUse">'
            f'<path d="M0,5 q3.5,-3.4 7,0 t7,0" fill="none" '
            f'stroke="{C["water2"]}" stroke-width="1.05"/></pattern></defs>'
            f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')


# ============================ warstwy z OSM ============================
def land_water(pr, use_coast=False):
    """Tło: ląd i woda.

    Dla map przeglądowych maską lądu są obrysy gmin (granica Cartageny biegnie
    po linii brzegowej), dla map szczegółowych — `natural=coastline`.
    """
    s = []
    s.append(f'<rect width="{pr.w}" height="{pr.h}" fill="{C["water"]}"/>')
    s.append(f'<rect width="{pr.w}" height="{pr.h}" fill="url(#wave)" '
             f'opacity=".45"/>')
    if use_coast:
        chains = geom.join_coords(COAST)
        land = geom.land_polygons(chains, pr.bbox)
    else:
        land = [r for key in LAND_KEYS for r in rings(key) if len(r) > 3]
    s.append(f'<path fill-rule="nonzero" fill="{C["land"]}" '
             f'd="{paths(pr, land)}"/>')
    wet = [r for key in WATER_KEYS for r in rings(key)
           if len(r) > 3 and geom.hits(r, pr.bbox, 0.004)]
    if wet:
        s.append(f'<path fill-rule="evenodd" fill="{C["water"]}" '
                 f'stroke="{C["water2"]}" stroke-width="0.6" '
                 f'd="{paths(pr, wet)}"/>')
        s.append(f'<path fill-rule="evenodd" fill="url(#wave)" opacity=".45" '
                 f'd="{paths(pr, wet)}"/>')
    return "".join(s)


def blocks(pr, pad=0.0008, op=0.85):
    """Rzuty budynków — plan miasta czyta się jak plan Nolliego."""
    sel = [b for b in BUILDINGS if geom.hits(b, pr.bbox, pad)]
    if not sel:
        return ""
    return (f'<path d="{paths(pr, sel)}" fill="{C["block"]}" '
            f'fill-opacity="{op}" stroke="none"/>')


def street_net(pr, pad=0.0008, classes=("main", "mid", "minor", "foot")):
    """Rzeczywista siatka ulic z OSM zamiast rysowanej kratki."""
    out = []
    for cls in ("foot", "minor", "mid", "main"):
        if cls not in classes:
            continue
        sel = [w for k, w in STREETS if k == cls and geom.hits(w, pr.bbox, pad)]
        if not sel:
            continue
        out.append(f'<path d="{paths(pr, sel, close=False)}" fill="none" '
                   f'stroke="{C["muted"]}" stroke-width="{STREET_W[cls]}" '
                   f'stroke-linecap="round" stroke-linejoin="round" '
                   f'opacity="{0.42 if cls in ("foot", "minor") else 0.6}"/>')
    return "".join(out)


def squares_svg(pr, pad=0.0004):
    sel = [w for _n, w in SQUARES if geom.hits(w, pr.bbox, pad)]
    if not sel:
        return ""
    return (f'<path d="{paths(pr, sel)}" fill="{C["land2"]}" '
            f'stroke="{C["muted"]}" stroke-width="0.6" opacity=".95"/>')


def walls_svg(pr, hatch=True):
    """Mury miejskie — `barrier=city_wall` / `historic=citywalls` z OSM."""
    sel = [w for w in WALLS if geom.hits(w, pr.bbox, 0.001)]
    if not sel:
        return ""
    d = paths(pr, sel, close=False)
    out = []
    if hatch:
        out.append(f'<path d="{d}" fill="none" stroke="url(#hatch)" '
                   f'stroke-width="7"/>')
        out.append(f'<path d="{d}" fill="none" stroke="{C["wall"]}" '
                   f'stroke-width="4.6" opacity=".5" stroke-linejoin="round"/>')
    out.append(f'<path d="{d}" fill="none" stroke="{C["wall"]}" '
               f'stroke-width="{1.3 if hatch else 2.2}" '
               f'stroke-linejoin="round" stroke-linecap="round"/>')
    return "".join(out)


def district(pr, name, fill, stroke=None, sw=0.7, op=1.0, dash=None):
    poly = DISTRICTS.get(name)
    if not poly:
        return ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return (f'<path d="{path(pr, poly)}" fill="{fill}" fill-opacity="{op}"'
            f'{st}{da}/>')


def old_town(pr, fill, stroke=None, sw=2.4, op=1.0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return (f'<path fill-rule="nonzero" d="{paths(pr, WALLED_CITY)}" '
            f'fill="{fill}" fill-opacity="{op}"{st}/>')


def routes_svg(pr, keys, dash=True, streets=True):
    """Trasy spacerów. Na mapach szczegółowych prowadzone po siatce ulic
    z OSM, na przeglądowej — wygładzoną linią między przystankami."""
    cols = {"I": "#B4593A", "II": "#1F4E5A", "III": "#A98430",
            "IV": "#3F7A5E", "V": "#6B4E9E"}
    out = []
    for k in keys:
        pts = [(P[i][2], P[i][3]) for i in ROUTES[k] if i in P]
        if len(pts) < 2:
            continue
        if streets:
            d = path(pr, route.walk(STREETS, pts), close=False)
        else:
            d = smooth(pr, pts)
        out.append(f'<path d="{d}" fill="none" stroke="#fff" '
                   f'stroke-width="5.4" stroke-linecap="round" '
                   f'stroke-linejoin="round" opacity=".75"/>')
        da = ' stroke-dasharray="7 4.5"' if dash else ''
        out.append(f'<path d="{d}" fill="none" stroke="{cols[k]}" '
                   f'stroke-width="2.4" stroke-linecap="round" '
                   f'stroke-linejoin="round"{da}/>')
    return "".join(out)


def decluster(pts, rmin=19.0, iters=140):
    """Rozsuwa nachodzące znaczniki, zachowując pozycję zbliżoną do oryginału."""
    cur = [list(p) for p in pts]
    for _ in range(iters):
        moved = False
        for i in range(len(cur)):
            for j in range(i + 1, len(cur)):
                dx = cur[j][0] - cur[i][0]
                dy = cur[j][1] - cur[i][1]
                d = math.hypot(dx, dy) or 0.01
                if d < rmin:
                    push = (rmin - d) / 2 * 0.62
                    ux, uy = dx / d, dy / d
                    cur[i][0] -= ux * push; cur[i][1] -= uy * push
                    cur[j][0] += ux * push; cur[j][1] += uy * push
                    moved = True
        for k, (ox, oy) in enumerate(pts):        # lekkie przyciąganie do źródła
            cur[k][0] += (ox - cur[k][0]) * 0.05
            cur[k][1] += (oy - cur[k][1]) * 0.05
        if not moved:
            break
    return [tuple(p) for p in cur]


def markers(pr, items, rmin=19.0):
    """items: [(etykieta, lat, lon, kategoria)]"""
    orig = [pr(la, lo) for _lab, la, lo, _c in items]
    new = decluster(orig, rmin=rmin)
    out = []
    for (ox, oy), (nx, ny) in zip(orig, new):
        if math.hypot(nx - ox, ny - oy) > 3.5:
            out.append(f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{nx:.1f}" '
                       f'y2="{ny:.1f}" stroke="{C["muted"]}" '
                       f'stroke-width="0.7" opacity=".7"/>')
            out.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="1.5" '
                       f'fill="{C["muted"]}"/>')
    for (lab, _la, _lo, cat), (nx, ny) in zip(items, new):
        out.append(marker(nx, ny, lab, cat))
    return "".join(out)


def label_district(pr, name, text, size=9, col=None, ls=2.2, op=1.0, dy=0.0):
    """Etykieta w środku widocznej części kwartału (geometria z OSM)."""
    poly = DISTRICTS.get(name)
    if not poly:
        return ""
    c = geom.visible_centroid([poly], pr.bbox)
    if not c:
        return ""
    x, y = pr(*c)
    return area_label(x, y + dy, text, size, col or C["muted"], ls, op)


def label_area(pr, key, text, size=7, col=None, ls=0.8, op=0.85, dy=0.0):
    """Etykieta w środku widocznej części obiektu z OSM (akwen, wzgórze…)."""
    c = geom.visible_centroid(rings(key), pr.bbox)
    if not c:
        return ""
    x, y = pr(*c)
    return area_label(x, y + dy, text, size, col or C["teal"], ls, op)


def markers_block(pr, prefix, rmin=19.0):
    items = [(p[0].split(".")[1], p[2], p[3], p[4])
             for p in POIS if p[0].startswith(prefix)]
    return markers(pr, items, rmin)


# ===================== MAPA 1 — obrona zatoki =====================
def _muni_rings():
    rs = [r for r in rings("R1343457") if len(r) > 3]
    return sorted(rs, key=lambda r: -abs(geom.signed_area(r)))


def tip_bocagrande():
    """Południowy cypel Bocagrande (granica dzielnicy z OSM)."""
    return min(rings("R1643328")[0], key=lambda p: p[0])


def tip_tierrabomba_n():
    """Północny kraniec Tierrabomby (drugi pierścień granicy gminy)."""
    return max(_muni_rings()[1], key=lambda p: p[0])


def chain_bocachica(length_m=900.0):
    """Odcinek łańcucha: od fortu San Fernando w stronę Barú."""
    a = (P["1.3"][2], P["1.3"][3])
    south = min(_muni_rings()[1], key=lambda p: p[0])
    b = min((p for p in _muni_rings()[0] if p[0] < south[0]),
            key=lambda p: geom.dist_m(a, p), default=None)
    if not b:
        return a, (a[0] - 0.006, a[1])
    d = geom.dist_m(a, b) or 1.0
    t = min(1.0, length_m / d)
    return a, (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)



def map1():
    bbox, w, h = frame(BBOX["1"])
    pr = Proj(bbox, w, h, pad=16)
    s = [head(w, h), land_water(pr)]

    # Stare Miasto jako punkt odniesienia w skali zatoki
    s.append(old_town(pr, C["wallf"], C["wall"], 1.4))

    # Escollera de Bocagrande (podwodna tama, 1771–1778) — poprowadzona
    # między realnymi cyplami: Bocagrande i północnym krańcem Tierrabomby.
    a, b = pr(*tip_bocagrande()), pr(*tip_tierrabomba_n())
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
             f'y2="{b[1]:.1f}" stroke="{C["accent"]}" stroke-width="3.2" '
             f'stroke-dasharray="2 3.2"/>')
    # Łańcuch rozpinany w cieśninie Bocachica — krótki odcinek przy forcie
    # San Fernando (szerokość przesmyku jest poniżej rozdzielczości tej mapy).
    a, b = chain_bocachica()
    a, b = pr(*a), pr(*b)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
             f'y2="{b[1]:.1f}" stroke="{C["accent"]}" stroke-width="2.4" '
             f'stroke-dasharray="1.6 2.4"/>')

    def arrow(pts, col, lab, lx, ly, anchor="start"):
        d = smooth(pr, pts)
        s.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.1" '
                 f'stroke-dasharray="9 5" opacity=".9"/>')
        x, y = pr(*pts[-1])
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{col}"/>')
        px, py = pr(lx, ly)
        s.append(f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="{anchor}" '
                 f'font-family="Archivo, sans-serif" font-size="7.8" '
                 f'font-weight="600" fill="{col}">{lab}</text>')
    arrow([(10.4180,-75.6100),(10.4080,-75.5900),(10.3985,-75.5760),
           (10.3980,-75.5680),(10.4060,-75.5600),(10.4180,-75.5530)],
          C["teal"], "DRAKE 1586 → Bocagrande", 10.4270, -75.6130)
    arrow([(10.3000,-75.6000),(10.3180,-75.5790),(10.3290,-75.5692),
           (10.3500,-75.5520),(10.3800,-75.5470),(10.4080,-75.5455),
           (10.4180,-75.5470)],
          "#7A3E22", "VERNON 1741 · POINTIS 1697 → Bocachica", 10.4185, -75.6130)

    items = []
    for pid in ("1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7"):
        _, _, la, lo, cat, _ = P[pid]
        if pr.la0 <= la <= pr.la1 and pr.lo0 <= lo <= pr.lo1:
            items.append((pid.split(".")[1], la, lo, cat))
    # punkty z mapy 2 widoczne też w skali zatoki
    items += [("A", P["2.1"][2], P["2.1"][3], "fort"),
              ("B", P["2.3"][2], P["2.3"][3], "view"),
              ("C", P["2.7"][2], P["2.7"][3], "fort")]
    s.append(markers(pr, items, rmin=20))

    s.append(area_label(*pr(10.4390,-75.5960), "MORZE", 9.4, C["teal"], 2.6, .85))
    s.append(area_label(*pr(10.4330,-75.5960), "KARAIBSKIE", 9.4, C["teal"], 2.6, .85))
    s.append(area_label(*pr(10.3720,-75.5430), "BAHÍA DE", 9, C["teal"], 2.2, .8))
    s.append(area_label(*pr(10.3660,-75.5430), "CARTAGENA", 9, C["teal"], 2.2, .8))
    s.append(area_label(*pr(10.3560,-75.5720), "TIERRABOMBA", 7.8, C["muted"], 1.8))
    s.append(area_label(*pr(10.2980,-75.5900), "BARÚ", 7.8, C["muted"], 1.8))
    s.append(area_label(*pr(10.4105,-75.5600), "Bocagrande", 7, C["muted"], .8))
    s.append(area_label(*pr(10.4330,-75.5540), "Stare Miasto", 7.4, C["wall"], .8))
    s.append(area_label(*pr(10.4180,-75.5120), "LĄD STAŁY", 8.4, C["muted"], 2.4))
    s.append(area_label(*pr(10.2900,-75.5380), "↓ Islas del Rosario · Playa Blanca", 7, C["teal"], .6, .9))
    s.append(scalebar(pr, 30, h - 26, 5000))
    s.append(north(w - 32, 40))
    s.append(credit(w, h))
    s.append('</svg>')
    return "".join(s)


# ===================== MAPA 2 — plan miasta =====================
DISTRICT_AREAS = (("R1643328", "BOCAGRANDE"), ("R1643334", "EL LAGUITO"),
                  ("R1643329", "CASTILLOGRANDE"), ("R19110567", "MANGA"),
                  ("R19110390", "PIE DE LA POPA"), ("R19135837", "EL CABRERO"))


def map2():
    bbox, w, h = frame(BBOX["2"])
    pr = Proj(bbox, w, h, pad=16)
    s = [head(w, h), land_water(pr)]

    # dzielnice z granic administracyjnych OSM
    poly = [r for key, _n in DISTRICT_AREAS for r in rings(key) if len(r) > 3]
    s.append(f'<path d="{paths(pr, poly)}" fill="{C["land2"]}" '
             f'fill-opacity=".55" stroke="{C["muted"]}" stroke-width="0.5" '
             f'stroke-opacity=".6"/>')
    # wzgórze La Popa (natural=wood) i lotnisko
    s.append(f'<path d="{paths(pr, rings("W25841555"))}" fill="{C["land2"]}" '
             f'stroke="{C["muted"]}" stroke-width="0.8"/>')
    s.append(f'<path d="{paths(pr, rings("W100101180"))}" fill="{C["land2"]}" '
             f'fill-opacity=".8" stroke="{C["muted"]}" stroke-width="0.6"/>')
    # główne ulice tam, gdzie mamy dane szczegółowe
    s.append(street_net(pr, pad=0.0, classes=("main",)))

    s.append(district(pr, "Getsemaní", C["land2"], C["wall"], 0.9, .9, "3 2"))
    s.append(old_town(pr, C["wallf"], None, 0, .85))
    s.append(walls_svg(pr, hatch=False))
    s.append(routes_svg(pr, ["V"], streets=False))

    items = []
    for pid in ("2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9"):
        _, _, la, lo, cat, _ = P[pid]
        la = min(max(la, pr.la0 + 0.0035), pr.la1 - 0.0035)
        lo = min(max(lo, pr.lo0 + 0.0035), pr.lo1 - 0.0035)
        items.append((pid.split(".")[1], la, lo, cat))
    s.append(markers(pr, items, rmin=20))

    x, y = pr(*geom.centroid(DISTRICTS["Centro"]))
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{C["wall"]}"/>'
             f'<text x="{x:.1f}" y="{y+3.3:.1f}" text-anchor="middle" '
             f'font-family="Archivo, sans-serif" font-size="8.6" '
             f'font-weight="600" fill="#fff">SM</text>')
    x, y = pr(*geom.centroid(GETSEMANI))
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.8" fill="{C["accent"]}"/>'
             f'<text x="{x:.1f}" y="{y+3.0:.1f}" text-anchor="middle" '
             f'font-family="Archivo, sans-serif" font-size="7.6" '
             f'font-weight="600" fill="#fff">GE</text>')

    s.append(area_label(*pr(10.4430,-75.5620), "MORZE", 9.2, C["teal"], 2.6, .85))
    s.append(area_label(*pr(10.4395,-75.5620), "KARAIBSKIE", 9.2, C["teal"], 2.6, .85))
    s.append(area_label(*pr(10.3990,-75.5508), "BAHÍA DE", 8.2, C["teal"], 2, .8))
    s.append(area_label(*pr(10.3955,-75.5508), "CARTAGENA", 8.2, C["teal"], 2, .8))
    s.append(label_area(pr, "R1643328", "BOCAGRANDE", 8, C["muted"], 2, 1.0))
    s.append(label_area(pr, "R1643334", "EL LAGUITO", 6.6, C["muted"], 1, 1.0))
    s.append(label_area(pr, "R19110567", "MANGA", 7.2, C["muted"], 1.4, 1.0))
    s.append(label_area(pr, "R19135837", "EL CABRERO", 6.8, C["muted"], 1.2, 1.0))
    s.append(label_area(pr, "W25841555", "LA POPA", 7, C["muted"], 1.4, 1.0))
    s.append(label_area(pr, "R19110390", "PIE DE LA POPA", 6.6, C["muted"], 1.2, 1.0))
    s.append(area_label(*pr(10.4530,-75.5140), "La Boquilla ↗", 7, C["teal"], .6, .9, "end"))
    s.append(area_label(*pr(10.3935,-75.5120), "Turbaco · Barranquilla ↘", 6.8, C["muted"], .6, .85, "end"))
    s.append(scalebar(pr, 30, h - 26, 1000))
    s.append(north(34, 40))
    s.append(credit(w, h))
    s.append('</svg>')
    return "".join(s)


# ================= MAPA 3 — Stare Miasto w murach =================
def map3():
    bbox, w, h = frame(BBOX["3"])
    pr = Proj(bbox, w, h, pad=16)
    s = [head(w, h), land_water(pr, use_coast=True)]

    s.append(district(pr, "La Matuna", C["land2"], C["muted"], 0.6, .8))
    s.append(district(pr, "Getsemaní", C["land2"], C["muted"], 0.7, .75))
    s.append(district(pr, "El Cabrero", C["land2"], C["muted"], 0.6, .7))
    s.append(old_town(pr, C["land"]))
    s.append(blocks(pr, op=0.9))
    s.append(squares_svg(pr))
    s.append(street_net(pr))
    s.append(walls_svg(pr))
    s.append(routes_svg(pr, ["I", "II", "III"]))
    s.append(markers_block(pr, "3."))

    s.append(label_district(pr, "San Diego", "SAN DIEGO", 9, C["muted"], 3, .38))
    s.append(label_district(pr, "Centro", "EL CENTRO", 9, C["muted"], 3, .38))
    s.append(label_district(pr, "La Matuna", "LA MATUNA", 6.4, C["muted"], 1.4, .8))
    s.append(label_district(pr, "Getsemaní", "GETSEMANÍ", 7, C["muted"], 1.6, .8))
    s.append(area_label(*pr(10.42980,-75.55390), "MORZE", 8.4, C["teal"], 2.2, .85))
    s.append(area_label(*pr(10.42890,-75.55390), "KARAIBSKIE", 8.4, C["teal"], 2.2, .85))
    s.append(area_label(*pr(10.42090,-75.55330), "BAHÍA DE", 7, C["teal"], 1.6, .8))
    s.append(area_label(*pr(10.42020,-75.55330), "LAS ÁNIMAS", 7, C["teal"], 1.6, .8))
    s.append(label_area(pr, "W25896749", "Laguna del Cabrero", 6.2, C["teal"], .6, .8))
    s.append(scalebar(pr, w - 185, h - 46, 200))
    s.append(north(w - 32, 40))
    s.append(credit(w, h))
    s.append('</svg>')
    return "".join(s)


# ===================== MAPA 4 — Getsemaní =====================
def map4():
    bbox, w, h = frame(BBOX["4"])
    pr = Proj(bbox, w, h, pad=16)
    s = [head(w, h), land_water(pr, use_coast=True)]

    s.append(district(pr, "La Matuna", C["land2"], C["muted"], 0.6, .8))
    s.append(old_town(pr, C["land2"], C["wall"], 3.0, .8))
    s.append(district(pr, "Getsemaní", C["land"], None, 0, 1.0))
    s.append(blocks(pr, op=0.9))
    s.append(squares_svg(pr))
    s.append(street_net(pr))
    s.append(f'<path d="{path(pr, GETSEMANI)}" fill="none" '
             f'stroke="{C["wall"]}" stroke-width="1.6" '
             f'stroke-dasharray="6 3"/>')
    s.append(walls_svg(pr))
    s.append(routes_svg(pr, ["IV"]))
    s.append(markers_block(pr, "4."))

    x, y = pr(P["3.1"][2], P["3.1"][3])
    s.append(marker(x, y, "★", "gate", 9))
    s.append(label_district(pr, "Getsemaní", "GETSEMANÍ", 9, C["muted"], 2.6))
    s.append(label_district(pr, "La Matuna", "LA MATUNA", 6.4, C["muted"], 1.4, .8))
    s.append(area_label(*pr(10.42560,-75.54880), "STARE MIASTO", 7.4, C["wall"], 1.6, .9))
    s.append(label_area(pr, "R20607558", "BAHÍA DE LAS ÁNIMAS", 7, C["teal"], 1.4, .8))
    s.append(scalebar(pr, 30, h - 26, 150))
    s.append(north(w - 32, 38))
    s.append(credit(w, h))
    s.append('</svg>')
    return "".join(s)


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "maps"), exist_ok=True)
    for n, fn in ((1, map1), (2, map2), (3, map3), (4, map4)):
        p = os.path.join(here, f"maps/mapa{n}.svg")
        open(p, "w", encoding="utf-8").write(fn())
        print(f"mapa {n}: {os.path.getsize(p)//1024} KB")
