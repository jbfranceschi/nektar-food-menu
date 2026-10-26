#!/usr/bin/env python3
"""
Produit un aperçu avant publication, en haute définition :
  - menu-ordinateur.png et menu-mobile.png (rendu du lien, net, ×3)
  - menu.pdf (A4, une seule page, vectoriel : idéal pour l'impression)

    python3 outils/apercu.py            # menu
    python3 outils/apercu.py vins       # vins au verre

Nécessite Playwright (pip install playwright && playwright install chromium).
Les fichiers sont écrits dans apercu/ (ignoré par Git).
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parent.parent
nom = "vins" if len(sys.argv) > 1 and sys.argv[1] == "vins" else "menu"
page_cible = "vins/index.html" if nom == "vins" else "index.html"
sortie = RACINE / "apercu"
sortie.mkdir(exist_ok=True)
url = (RACINE / page_cible).as_uri()


def ouvrir(nav, **kw):
    pg = nav.new_page(**kw)
    pg.goto(url)
    pg.wait_for_selector(".feuille.prete")
    pg.wait_for_timeout(400)  # laisse finir le fondu d’apparition (0,2 s)
    return pg


with sync_playwright() as p:
    nav = p.chromium.launch()
    for etiquette, largeur, hauteur in (("ordinateur", 1100, 1600), ("mobile", 390, 600)):
        pg = ouvrir(nav, viewport={"width": largeur, "height": hauteur}, device_scale_factor=3)
        pg.screenshot(path=str(sortie / f"{nom}-{etiquette}.png"), full_page=True)
        pg.close()
    pg = ouvrir(nav)
    infos = pg.evaluate("""() => { const f = document.getElementById('feuille');
        return { s: getComputedStyle(f).getPropertyValue('--s'), n: f.querySelectorAll('.article').length }; }""")
    pg.pdf(path=str(sortie / f"{nom}.pdf"), prefer_css_page_size=True, print_background=True)
    nav.close()

pdf = (sortie / f"{nom}.pdf").read_bytes()
pages = pdf.count(b"/Type /Page") - pdf.count(b"/Type /Pages")
print(f"✓ Aperçus écrits dans {sortie}")
print(f"  {infos['n']} articles · taille du texte {float(infos['s']) * 100:.0f} % · PDF : {pages} page(s)")
if pages != 1:
    sys.exit("⚠ Le PDF ne tient pas sur une page : à corriger avant publication.")
