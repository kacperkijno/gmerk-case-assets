# Skład przewodnika po Cartagenie

Pipeline zamienia `../PRZEWODNIK-CARTAGENA.md` w książkowy PDF w formacie A5
(`../Cartagena-przewodnik.pdf`) wraz z czterema rysowanymi mapami.

## Uruchomienie

```bash
pip install weasyprint markdown pyphen requests
python3 fetch_fonts.py    # Playfair Display, Source Serif 4, Archivo (OFL)
python3 maps.py           # generuje maps/mapa1..4.svg
python3 build.py          # składa PDF
```

## Pliki

| Plik | Rola |
|---|---|
| `geo.py` | dane geograficzne: obrysy, 58 punktów POI, trasy spacerów |
| `maps.py` | generator map wektorowych (SVG) |
| `prep.py` | obróbka markdownu: ramki, odnośniki do map, numery przystanków |
| `build.py` | montaż HTML → PDF (okładka, spis treści, mapy, metadane) |
| `book.css` | skład: format A5, pagina, ramki, tabele, mapy |
| `fetch_fonts.py` | pobiera kroje pisma z Google Fonts |

## Mapy

Mapy są **rysowane od zera**, w przybliżonych proporcjach — służą do orientacji,
nie do nawigacji. Współrzędne punktów (Dodatek F w książce) mają dokładność rzędu
100 m.

Żeby zastąpić je prawdziwą geometrią OpenStreetMap, trzeba mieć w środowisku
dostęp sieciowy do `overpass-api.de`; wtedy obrysy w `geo.py` można wygenerować
zapytaniem Overpass zamiast wpisywać ręcznie (licencja ODbL wymaga atrybucji
„© OpenStreetMap contributors").

## Pułapki, na które już się nadziałem

- `opacity` na `<text>` w SVG psuje pozycjonowanie w WeasyPrint — używać
  `fill-opacity`.
- Python-Markdown wymaga pustej linii przed listą; `prep.normalize_lists`
  ją dopisuje.
- Emoji nie składają się w druku — `prep.inline_labels` zamienia je na
  etykiety tekstowe.
