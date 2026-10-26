#!/usr/bin/env python3
"""
Produit un aperçu avant publication : captures ordinateur + mobile et un PDF A4.

    python3 outils/apercu.py            # menu
    python3 outils/apercu.py vins       # vins au verre

Nécessite Playwright (pip install playwright && playwright install chromium).
Les fichiers sont écrits dans apercu/ (ignoré par Git).
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parent.parent
page_cible = "vins/index.html" if len(sys.argv) > 1 and sys.argv[1] == "vins" else "index.html"
nom = "vins" if page_cible.startswith("vins") else "menu"
sortie = RACINE / "apercu"
sortie.mkdir(exist_ok=True)
url = (RACINE / page_cible).as_uri()

with sync_playwright() as p:
    nav = p.chromium.launch()
    for etiquette, largeur, hauteur, echelle in (("ordinateur", 1100, 900, 1.5), ("mobile", 390, 844, 3)):
        pg = nav.new_page(viewport={"width": largeur, "height": hauteur}, device_scale_factor=echelle)
        pg.goto(url)
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(sortie / f"{nom}-{etiquette}.png"), full_page=True)
        pg.close()
    pg = nav.new_page()
    pg.goto(url)
    pg.evaluate("document.fonts.ready")
    pg.pdf(path=str(sortie / f"{nom}.pdf"), format="A4", print_background=True, prefer_css_page_size=True)
    nav.close()

print(f"✓ Aperçus écrits dans {sortie}")
