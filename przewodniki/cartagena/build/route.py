# -*- coding: utf-8 -*-
"""Prowadzenie tras spacerowych po rzeczywistej siatce ulic z OpenStreetMap.

Trasy w książce to listy przystanków. Rysowanie prostej między przystankami
przecinało kwartały; tutaj każdy odcinek jest najkrótszą drogą po ulicach
(Dijkstra na grafie z `geo.STREETS`).
"""
import heapq
import math

from geom import dist_m

# Ulice, po których realnie idzie pieszy.
WALKABLE = {"main", "mid", "minor", "foot"}
# Koszt względny: chodnikami i deptakami chodzi się chętniej niż arterią.
COST = {"foot": 0.9, "minor": 1.0, "mid": 1.0, "main": 1.35}

_GRAPH = None


def _key(p, nd=5):
    return (round(p[0], nd), round(p[1], nd))


def graph(streets):
    """{węzeł: [(sąsiad, koszt)]} — węzły sklejane po zaokrąglonych współrzędnych."""
    g = {}
    for cls, line in streets:
        if cls not in WALKABLE:
            continue
        w = COST.get(cls, 1.0)
        for i in range(len(line) - 1):
            a, b = _key(line[i]), _key(line[i + 1])
            if a == b:
                continue
            d = dist_m(a, b) * w
            g.setdefault(a, []).append((b, d))
            g.setdefault(b, []).append((a, d))
    return g


def _ensure(streets):
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = graph(streets)
    return _GRAPH


def nearest_node(g, pt, limit_m=140.0):
    best, bd = None, limit_m
    for n in g:
        d = dist_m(pt, n)
        if d < bd:
            best, bd = n, d
    return best


def shortest(g, a, b, cap=None):
    """Dijkstra; `cap` ucina przeszukiwanie, gdy droga robi się absurdalna."""
    if a == b:
        return [a]
    dist = {a: 0.0}
    prev = {}
    pq = [(0.0, a)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == b:
            break
        if d > dist.get(u, math.inf):
            continue
        if cap and d > cap:
            return None
        for v, w in g.get(u, ()):
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if b not in dist:
        return None
    out, cur = [b], b
    while cur != a:
        cur = prev[cur]
        out.append(cur)
    return out[::-1]


def walk(streets, stops, detour=2.0):
    """Lista przystanków → polilinia po ulicach.

    Gdy odcinka nie da się poprowadzić ulicami (dziura w danych) albo droga
    wychodzi ponad `detour` × odległość w linii prostej, zostaje prosta —
    lepiej pokazać kierunek niż objazd przez pół miasta.
    """
    g = _ensure(streets)
    out = []
    for i in range(len(stops) - 1):
        a, b = stops[i], stops[i + 1]
        na, nb = nearest_node(g, a), nearest_node(g, b)
        seg = None
        if na and nb:
            straight = max(dist_m(a, b), 1.0)
            p = shortest(g, na, nb, cap=straight * detour * 1.6)
            if p:
                length = sum(dist_m(p[k], p[k + 1]) for k in range(len(p) - 1))
                if length <= straight * detour:
                    seg = [a] + p + [b]
        if seg is None:
            seg = [a, b]
        out += seg if not out else seg[1:]
    return out
