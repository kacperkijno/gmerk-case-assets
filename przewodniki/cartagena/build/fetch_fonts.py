# -*- coding: utf-8 -*-
"""Pobiera kroje pisma (OFL) z Google Fonts i zapisuje lokalny fonts.css."""
import re, os, hashlib, requests

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
FAMILIES = [
    "Playfair+Display:ital,wght@0,400;0,500;0,700;1,400",
    "Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400",
    "Archivo:wght@400;500;600",
]

def main():
    out = os.path.join(HERE, "fonts")
    os.makedirs(out, exist_ok=True)
    css = []
    for fam in FAMILIES:
        src = requests.get(f"https://fonts.googleapis.com/css2?family={fam}",
                           headers=UA, timeout=30).text
        def repl(m):
            url = m.group(1)
            name = hashlib.md5(url.encode()).hexdigest()[:10] + ".woff2"
            path = os.path.join(out, name)
            if not os.path.exists(path):
                open(path, "wb").write(requests.get(url, timeout=60).content)
            return f"url(fonts/{name})"
        css.append(re.sub(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", repl, src))
    open(os.path.join(HERE, "fonts.css"), "w").write("\n".join(css))
    print("fonts.css gotowy;", len(os.listdir(out)), "plików woff2")

if __name__ == "__main__":
    main()
