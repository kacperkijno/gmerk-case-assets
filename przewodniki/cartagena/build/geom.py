# -*- coding: utf-8 -*-
"""Geometria map: przycinanie, domykanie linii brzegowej, łączenie odcinków.

Moduł jest czysto obliczeniowy — nie sięga do sieci, więc skład książki działa
offline na danych zapisanych w `maps/osm-data.json`.
"""
import math

# ------------------------------------------------- linia brzegowa → ląd
# W OSM `natural=coastline` jest skierowana: ląd po LEWEJ stronie kierunku
# rysowania. Żeby dostać wielokąty lądu w wycinku mapy, przycinamy łańcuchy
# do prostokąta i domykamy je po jego obwodzie, idąc przeciwnie do ruchu
# wskazówek zegara (wtedy ląd wciąż zostaje po lewej).

EPS = 1e-9


def _same(a, b, eps=1e-7):
    return abs(a[0] - b[0]) < eps and abs(a[1] - b[1]) < eps


def _lb(ax, ay, bx, by, xmin, ymin, xmax, ymax):
    """Liang–Barsky: zakres parametru odcinka wewnątrz prostokąta."""
    dx, dy = bx - ax, by - ay
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, ax - xmin), (dx, xmax - ax),
                 (-dy, ay - ymin), (dy, ymax - ay)):
        if abs(p) < EPS:
            if q < 0:
                return None
            continue
        t = q / p
        if p < 0:
            if t > t1:
                return None
            t0 = max(t0, t)
        else:
            if t < t0:
                return None
            t1 = min(t1, t)
    return (t0, t1) if t1 > t0 - EPS else None


def clip_polyline(pts, bbox):
    """Dzieli polilinię na kawałki leżące wewnątrz bboxa."""
    s, w, n, e = bbox
    out, cur = [], []
    for i in range(len(pts) - 1):
        (ay, ax), (by, bx) = pts[i], pts[i + 1]
        r = _lb(ax, ay, bx, by, w, s, e, n)
        if r is None:
            if len(cur) > 1:
                out.append(cur)
            cur = []
            continue
        t0, t1 = r
        p0 = (ay + (by - ay) * t0, ax + (bx - ax) * t0)
        p1 = (ay + (by - ay) * t1, ax + (bx - ax) * t1)
        if cur and _same(cur[-1], p0):
            cur.append(p1)
        else:
            if len(cur) > 1:
                out.append(cur)
            cur = [p0, p1]
        if t1 < 1.0 - 1e-9:                     # odcinek wychodzi z prostokąta
            if len(cur) > 1:
                out.append(cur)
            cur = []
    if len(cur) > 1:
        out.append(cur)
    return out


def _perim(p, bbox):
    """Parametr 0..4 po obwodzie bboxa, rosnący przeciwnie do wskazówek."""
    s, w, n, e = bbox
    la, lo = p
    d = {abs(la - s): 0, abs(lo - e): 1, abs(la - n): 2, abs(lo - w): 3}
    side = d[min(d)]
    if side == 0:
        return (lo - w) / (e - w)
    if side == 1:
        return 1 + (la - s) / (n - s)
    if side == 2:
        return 2 + (e - lo) / (e - w)
    return 3 + (n - la) / (n - s)


def signed_area(ring):
    a = 0.0
    for i in range(len(ring)):
        (y0, x0), (y1, x1) = ring[i], ring[(i + 1) % len(ring)]
        a += x0 * y1 - x1 * y0
    return a / 2.0


def land_polygons(coast_chains, bbox, all_land_fallback=True):
    """Łańcuchy linii brzegowej + bbox → wielokąty lądu (i dziury)."""
    s, w, n, e = bbox
    corners = [((s, w), 0.0), ((s, e), 1.0), ((n, e), 2.0), ((n, w), 3.0)]
    rings, segs = [], []
    for ch in coast_chains:
        for piece in clip_polyline(ch, bbox):
            if _same(piece[0], piece[-1]):
                rings.append(piece)
            else:
                segs.append((_perim(piece[0], bbox),
                             _perim(piece[-1], bbox), piece))

    if not segs:
        if rings:
            return rings
        return [[(s, w), (s, e), (n, e), (n, w)]] if all_land_fallback else []

    polys, unused = list(rings), set(range(len(segs)))
    while unused:
        start = min(unused)
        ring, i = [], start
        while True:
            unused.discard(i)
            ring += segs[i][2]
            t_out = segs[i][1]
            cand = unused | {start}
            best = min(cand, key=lambda j: (segs[j][0] - t_out) % 4.0)
            gap = (segs[best][0] - t_out) % 4.0
            for cp, ct in sorted(corners, key=lambda c: (c[1] - t_out) % 4.0):
                if EPS < (ct - t_out) % 4.0 < gap:
                    ring.append(cp)
            i = best
            if i == start:
                break
        if len(ring) > 2:
            polys.append(ring)
    return polys


# ------------------------------------------------------ łączenie odcinków
def join_rings(segs):
    """Łączy odcinki (listy kluczy węzłów) w pierścienie / dłuższe łańcuchy."""
    segs = [s for s in segs if len(s) > 1]
    out = []
    while segs:
        cur = segs.pop(0)
        changed = True
        while changed and cur[0] != cur[-1]:
            changed = False
            for i, s in enumerate(segs):
                if s[0] == cur[-1]:
                    cur += s[1:]
                elif s[-1] == cur[-1]:
                    cur += s[::-1][1:]
                elif s[-1] == cur[0]:
                    cur = s[:-1] + cur
                elif s[0] == cur[0]:
                    cur = s[::-1][:-1] + cur
                else:
                    continue
                segs.pop(i)
                changed = True
                break
        out.append(cur)
    return out


chains = join_rings


def join_coords(polylines, nd=6):
    """To samo, ale dla list współrzędnych (lat, lon) — po zaokrągleniu końców."""
    key = {}
    segs = []
    for line in polylines:
        ids = []
        for la, lo in line:
            k = (round(la, nd), round(lo, nd))
            key.setdefault(k, k)
            ids.append(k)
        segs.append(ids)
    return [[tuple(k) for k in ring] for ring in join_rings(segs)]


def simplify(pts, tol_m):
    """Douglas–Peucker w metrach (przybliżenie płaskie, lokalnie wystarczające)."""
    if len(pts) < 3:
        return pts
    tol = tol_m / 111320.0
    k = math.cos(math.radians(pts[0][0]))

    def rec(a, b):
        if b - a < 2:
            return []
        (y0, x0), (y1, x1) = pts[a], pts[b]
        dx, dy = (x1 - x0) * k, y1 - y0
        den = math.hypot(dx, dy)
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            (y, x) = pts[i]
            if den < 1e-12:
                d = math.hypot((x - x0) * k, y - y0)
            else:
                d = abs(dy * (x - x0) * k - dx * (y - y0)) / den
            if d > best:
                best, bi = d, i
        if best <= tol:
            return []
        return rec(a, bi) + [bi] + rec(bi, b)

    return [pts[i] for i in [0] + rec(0, len(pts) - 1) + [len(pts) - 1]]


def dist_m(a, b):
    k = math.cos(math.radians(a[0]))
    return math.hypot((a[1] - b[1]) * k, a[0] - b[0]) * 111320.0


def centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def bounds(pts):
    la = [p[0] for p in pts]
    lo = [p[1] for p in pts]
    return min(la), min(lo), max(la), max(lo)


def hits(pts, bbox, pad=0.0):
    """Czy polilinia w ogóle dotyka prostokąta (s, w, n, e)?"""
    s, w, n, e = bbox
    s0, w0, n0, e0 = bounds(pts)
    return not (n0 < s - pad or s0 > n + pad or e0 < w - pad or w0 > e + pad)


def clip_polygon(ring, bbox):
    """Sutherland–Hodgman: wielokąt przycięty do prostokąta (s, w, n, e)."""
    s, w, n, e = bbox
    out = list(ring)
    for side, keep, inter in (
            ("s", lambda p: p[0] >= s, lambda a, b: (s, _lerp(a[1], b[1], (s - a[0]) / (b[0] - a[0])))),
            ("n", lambda p: p[0] <= n, lambda a, b: (n, _lerp(a[1], b[1], (n - a[0]) / (b[0] - a[0])))),
            ("w", lambda p: p[1] >= w, lambda a, b: (_lerp(a[0], b[0], (w - a[1]) / (b[1] - a[1])), w)),
            ("e", lambda p: p[1] <= e, lambda a, b: (_lerp(a[0], b[0], (e - a[1]) / (b[1] - a[1])), e))):
        if not out:
            return []
        cur, out = out, []
        for i, b in enumerate(cur):
            a = cur[i - 1]
            if keep(b):
                if not keep(a):
                    out.append(inter(a, b))
                out.append(b)
            elif keep(a):
                out.append(inter(a, b))
    return out


def _lerp(a, b, t):
    return a + (b - a) * t


def visible_centroid(rings, bbox):
    """Środek największego fragmentu widocznego w kadrze — kotwica etykiety."""
    best, area = None, 0.0
    for r in rings:
        if len(r) < 3:
            continue
        c = clip_polygon(r, bbox)
        if len(c) < 3:
            continue
        a = abs(signed_area(c))
        if a > area:
            best, area = c, a
    return centroid(best) if best else None
