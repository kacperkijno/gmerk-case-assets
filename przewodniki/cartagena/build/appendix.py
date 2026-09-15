# -*- coding: utf-8 -*-
"""Przepisuje Dodatek F (tabelę współrzędnych) z aktualnych danych POI.

Tabela w markdownie musi zgadzać się z tym, co pokazują mapy — po każdym
uruchomieniu `osm_build.py` trzeba odświeżyć też Dodatek F:

    python3 appendix.py
"""
import os
import sys

import geo

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "..", "PRZEWODNIK-CARTAGENA.md")

CAT = {"hist": "zabytek / muzeum", "plaza": "plac", "fort": "fortyfikacja",
       "view": "punkt widokowy", "life": "życie miasta", "gate": "brama"}

HEAD = "| Nr | Miejsce | Rodzaj | Szer. / dł. geogr. |\n|---|---|---|---|\n"
NOTE_START = "**⚠️ UWAGA — dokładność.**"
NOTE_END = "**📍 W TERENIE.**"
NOTE = """**⚠️ UWAGA — dokładność.** Współrzędne pochodzą z **OpenStreetMap**
(© OpenStreetMap contributors, licencja ODbL) — z tych samych danych korzystają
aplikacje offline wymienione niżej, więc punkt z tabeli i punkt w telefonie to
to samo miejsce. Pozycje oznaczone kropką (·) są przybliżone, z błędem rzędu
100–200 metrów: OpenStreetMap nie zna tych obiektów pod nazwami używanymi
w książce, więc ustawiono je względem sąsiednich punktów. Jeżeli aplikacja
znajdzie miejsce po nazwie — zaufaj nazwie, nie tabeli.

"""


def table():
    verified = set(geo.VERIFIED)
    rows = []
    for pid, name, la, lo, cat, _anchor in geo.POIS:
        m, n = pid.split(".")
        mark = "" if pid in verified else " ·"
        rows.append(((int(m), int(n)),
                     f"| M{m}·{n} | {name}{mark} | {CAT[cat]} | "
                     f"{la:.4f}, {lo:.4f} |"))
    rows.sort(key=lambda r: r[0])
    return HEAD + "\n".join(r[1] for r in rows) + "\n", len(geo.POIS) - len(verified)


def main():
    with open(MD, encoding="utf-8") as f:
        md = f.read()

    a = md.index(HEAD.splitlines()[0])
    b = md.index("\n", md.rindex("\n| M", a, md.index("\n\n---", a))) + 1
    tbl, approx = table()
    md = md[:a] + tbl + md[b:]

    # „W TERENIE" pojawia się w całej książce — szukamy dopiero za notą.
    na = md.index(NOTE_START)
    nb = md.index(NOTE_END, na)
    if not na < nb:
        sys.exit("Dodatek F: nie znalazłem noty o dokładności")
    md = md[:na] + NOTE + md[nb:]

    with open(MD, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Dodatek F: {len(geo.POIS)} punktów, w tym {approx} przybliżonych")


if __name__ == "__main__":
    main()
