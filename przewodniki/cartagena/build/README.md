# Skład przewodnika po Cartagenie

Pipeline zamienia `../PRZEWODNIK-CARTAGENA.md` w książkowy PDF w formacie A5
(`../Cartagena-przewodnik.pdf`) wraz z czterema mapami rysowanymi na danych
**OpenStreetMap**.

## Uruchomienie

```bash
pip install weasyprint markdown pyphen requests
python3 fetch_fonts.py    # Playfair Display, Source Serif 4, Archivo (OFL)
python3 osm_build.py      # pobiera OSM -> maps/osm-data.json  (wymaga sieci)
python3 appendix.py       # przepisuje Dodatek F z aktualnych współrzędnych
python3 maps.py           # generuje maps/mapa1..4.svg
python3 build.py          # składa PDF
```

`maps/osm-data.json` jest w repozytorium, więc **sam skład działa offline** —
`osm_build.py` trzeba uruchomić tylko wtedy, gdy chcemy odświeżyć dane z OSM.
Po każdym `osm_build.py` uruchom też `appendix.py`: tabela współrzędnych
w Dodatku F musi zgadzać się z tym, co pokazują mapy.

Podgląd map w PNG (nie wchodzi do książki, wymaga `pip install cairosvg`):

```bash
python3 preview.py /tmp/mapy
```

## Pliki

| Plik | Rola |
|---|---|
| `osm.py` | pobieranie danych z OpenStreetMap + cache na dysku |
| `geom.py` | geometria: przycinanie, linia brzegowa → ląd, upraszczanie |
| `osm_build.py` | z surowego OSM robi `maps/osm-data.json` (geometria + POI) |
| `geo.py` | warstwa redakcyjna: lista punktów, kategorie, trasy spacerów |
| `route.py` | prowadzenie tras spacerowych po siatce ulic (Dijkstra) |
| `maps.py` | generator map wektorowych (SVG) |
| `appendix.py` | przepisuje Dodatek F (tabelę współrzędnych) w markdownie |
| `prep.py` | obróbka markdownu: ramki, odnośniki do map, numery przystanków |
| `build.py` | montaż HTML → PDF (okładka, spis treści, mapy, metadane) |
| `book.css` | skład: format A5, pagina, ramki, tabele, mapy |
| `fetch_fonts.py` | pobiera kroje pisma z Google Fonts |
| `preview.py` | podgląd map w PNG (narzędzie pomocnicze) |

## Skąd biorą się mapy

Wszystko, co na mapach ma kształt, pochodzi z OpenStreetMap:

| Warstwa | Źródło w OSM |
|---|---|
| mury miejskie | `barrier=city_wall`, `historic=citywalls` |
| ulice, place, budynki | `highway=*`, `place=square`, `leisure=park`, `building=*` |
| linia brzegowa | `natural=coastline` (domykana do kadru w `geom.land_polygons`) |
| zatoki, laguny, ciénaga | relacje `natural=bay` / `natural=water` |
| dzielnice | `place=neighbourhood` i granice administracyjne |
| ląd na mapach 1–2 | granice gmin (Cartagena + sąsiednie) |
| współrzędne POI | dopasowanie po nazwie i rodzaju obiektu |

Autorskie zostają tylko warstwy, których w OSM nie ma: strzałki ataków na
mapie 1, *Escollera* i łańcuch w Bocachica, etykiety obszarów i kolejność
przystanków na trasach.

**Licencja danych: ODbL — każda mapa niesie podpis
„© OpenStreetMap contributors".**

### Skąd pobieramy

`osm_build.py` korzysta z dwóch punktów końcowych:

- `api.openstreetmap.org/api/0.6/map?bbox=` — pełny wycinek Starego Miasta
  i Getsemaní (ulice, budynki, mury, place);
- `nominatim.openstreetmap.org` (`/lookup`, `/search`) — geometria obiektów
  nazwanych: zatok, lagun, wzgórza La Popa, dzielnic, fortów, granic gmin.

Overpass byłby wygodniejszy, ale bywa niedostępny w środowiskach
z zamkniętą siecią — stąd oparcie o oficjalne API i Nominatim. Odpowiedzi
lądują w `osm-cache/` (poza repozytorium), więc kolejne uruchomienia nie
obciążają serwerów.

### Dopasowanie punktów

`osm_build.py` próbuje przypisać każdemu punktowi z `geo.py` obiekt z OSM.
Wymaga zgodności **rodzaju** (plac ≠ kościół ≠ bastion ≠ ulica — inaczej
„Bal. de Santo Domingo" skleiłby się z „Plaza de Santo Domingo") i zawierania
się nazw. Etykiety ulic tylko przysuwamy do osi jezdni, najwyżej o
`LINEAR_SNAP` metrów — mają zostać tam, gdzie postawił je autor.

Punkty bez odpowiednika w OSM przesuwamy o medianę przesunięcia sąsiadów:
gdy mur przesunął się o 150 m, brama nie może zostać w starym miejscu.
Skrypt wypisuje raport z dopasowania — warto przejrzeć pozycje oznaczone
`<-- SPRAWDZIĆ`. Lista punktów przybliżonych trafia do `geo.APPROX`, a stamtąd
do noty pod mapą i do Dodatku F (kropka przy nazwie).

## Pułapki, na które już się nadziałem

- `opacity` na `<text>` w SVG psuje pozycjonowanie w WeasyPrint — używać
  `fill-opacity`.
- Python-Markdown wymaga pustej linii przed listą; `prep.normalize_lists`
  ją dopisuje.
- Emoji nie składają się w druku — `prep.inline_labels` zamienia je na
  etykiety tekstowe.
- Douglas–Peucker na ulicach kasuje węzły skrzyżowań i graf rozpada się na
  kawałki; `osm_build.simplify_keeping` chroni węzły wspólne dla kilku ulic.
- Linia brzegowa w OSM jest skierowana (ląd po lewej) i nie jest zamknięta —
  trzeba ją przyciąć do kadru i domknąć po obwodzie, idąc przeciwnie do
  ruchu wskazówek zegara.
- Ulica o jednej nazwie to w OSM kilka odcinków; środek jednego z nich nie
  jest środkiem ulicy — `candidates()` skleja je przed dopasowaniem.
