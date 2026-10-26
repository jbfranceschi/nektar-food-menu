#!/usr/bin/env python3
"""
Génère les pages HTML de la carte NEKTAR à partir des fichiers de données.

    python3 outils/generer.py

Lit   donnees/menu.json  -> écrit index.html
Lit   donnees/vins.json  -> écrit vins/index.html   (si le fichier existe)

Aucune dépendance : Python 3 standard suffit.
"""
import html
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Allergènes connus : clé utilisée dans les données -> (libellé, icône SVG)
# Pour en ajouter un, ajoute une entrée ici (le libellé suffit : sans icône,
# une pastille avec l'initiale est affichée).
# ---------------------------------------------------------------------------
ALLERGENES = {
    "gluten": ("Gluten", '<svg viewBox="0 0 24 24"><g transform="rotate(22 12 13)"><path d="M12 23V5"/><path d="M12 8.5q-3.8-.6-4.4-5 3.9.4 4.4 5zM12 8.5q3.8-.6 4.4-5-3.9.4-4.4 5zM12 13q-3.8-.6-4.4-5 3.9.4 4.4 5zM12 13q3.8-.6 4.4-5-3.9.4-4.4 5zM12 17.5q-3.8-.6-4.4-5 3.9.4 4.4 5zM12 17.5q3.8-.6 4.4-5-3.9.4-4.4 5zM12 5q-1.6-2 0-4.3 1.6 2.3 0 4.3z"/></g></svg>'),
    "oeufs": ("Œufs", '<svg viewBox="0 0 24 24"><path d="M12 2.5c-4 0-7 7-7 12 0 4.4 3 7 7 7s7-2.6 7-7c0-5-3-12-7-12z"/></svg>'),
    "lactose": ("Lactose", '<svg viewBox="0 0 24 24"><path d="M6 10v12h7V10z"/><path d="M13 10l5-1.5v12L13 22"/><path d="M6 10l3.5-5 3.5 5"/><path d="M9.5 5l5-1.5 3.5 5"/><path d="M9.5 5V2.8l5-1.3v2"/><path class="plein" d="M9.5 13.2c-1.3 1.7-1.9 2.7-1.9 3.5a1.9 1.9 0 0 0 3.8 0c0-.8-.6-1.8-1.9-3.5z"/></svg>'),
    "moutarde": ("Moutarde", '<svg viewBox="0 0 24 24"><path d="M7 2.5h10v3.5H7z"/><path d="M7.5 6C6.4 7 6 8 6 9.5v11c0 .8.7 1.5 1.5 1.5h9c.8 0 1.5-.7 1.5-1.5v-11C18 8 17.6 7 16.5 6"/><path d="M6 11h12"/><circle class="plein" cx="10" cy="15" r="1.3"/><circle class="plein" cx="14" cy="15.3" r="1.3"/><circle class="plein" cx="12" cy="18.4" r="1.3"/></svg>'),
    "poisson": ("Poisson", '<svg viewBox="0 0 32 24"><path d="M3 12c4-7 13-8 19 0-6 8-15 7-19 0z"/><path d="M22 12l7-6-2 6 2 6z"/><circle cx="8" cy="11" r="1.1"/><path d="M11.5 7.5q2 4.5 0 9"/></svg>'),
    "fruits_a_coque": ("Fruits à coque", None),
    "arachide": ("Arachide", None),
    "crustaces": ("Crustacés", None),
    "mollusques": ("Mollusques", None),
    "celeri": ("Céleri", None),
    "soja": ("Soja", None),
    "sesame": ("Sésame", None),
    "sulfites": ("Sulfites", None),
    "lupin": ("Lupin", None),
}


def icone(cle):
    libelle, svg = ALLERGENES[cle]
    if svg is None:
        svg = ('<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9.5"/>'
               f'<text x="12" y="16.2" text-anchor="middle">{html.escape(libelle[0])}</text></svg>')
    return svg


def e(texte):
    return html.escape(texte or "", quote=True)


def verifier(donnees, fichier):
    erreurs = []
    for s in donnees["sections"]:
        for a in s["articles"]:
            for champ in ("nom", "prix"):
                if not str(a.get(champ, "")).strip():
                    erreurs.append(f"« {a.get('nom', '?')} » : champ « {champ} » manquant")
            for cle in a.get("allergenes", []):
                if cle not in ALLERGENES:
                    erreurs.append(f"« {a['nom']} » : allergène inconnu « {cle} » "
                                   f"(valeurs possibles : {', '.join(ALLERGENES)})")
    if erreurs:
        sys.exit(f"Erreurs dans {fichier} :\n  - " + "\n  - ".join(erreurs))


def normaliser(donnees):
    """Accepte soit une liste d'articles, soit des sections titrées."""
    if "sections" not in donnees:
        donnees["sections"] = [{"titre": None, "articles": donnees.get("articles", [])}]
    return donnees


def article_html(a):
    icones = "".join(
        f'<span class="ico" role="img" aria-label="{e(ALLERGENES[c][0])}" title="{e(ALLERGENES[c][0])}">{icone(c)}</span>'
        for c in a.get("allergenes", [])
    )
    desc = f'<p class="desc">{e(a["description"])}</p>' if a.get("description") else ""
    return f"""
      <li class="article">
        <div class="ligne">
          <h3 class="nom">{e(a["nom"])}{f'<span class="icos">{icones}</span>' if icones else ''}</h3>
          <span class="prix">{e(a["prix"]).replace("/", '<span class="sep">/</span>')}</span>
        </div>
        {desc}
      </li>"""


def page_html(donnees, prefixe=""):
    titre = donnees.get("titre", "Menu")
    sections = ""
    utilises = []
    for s in donnees["sections"]:
        for a in s["articles"]:
            for c in a.get("allergenes", []):
                if c not in utilises:
                    utilises.append(c)
        t = f'<h2 class="section">{e(s["titre"])}</h2>' if s.get("titre") else ""
        sections += f'\n    <section>{t}\n      <ul class="articles">{"".join(article_html(a) for a in s["articles"])}\n      </ul>\n    </section>'

    # Légende : ordre du catalogue, uniquement les allergènes présents sur la carte
    legende = ""
    ordre = [c for c in ALLERGENES if c in utilises]
    if ordre:
        items = "".join(f'<li><span class="ico">{icone(c)}</span>{e(ALLERGENES[c][0])}</li>' for c in ordre)
        legende = f'\n    <footer class="legende">\n      <h2><span>Allergènes</span></h2>\n      <ul>{items}</ul>\n    </footer>'

    note = f'<p class="note">{e(donnees["note"])}</p>' if donnees.get("note") else ""

    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#001223">
  <title>{e(titre)} · NEKTAR</title>
  <meta name="description" content="{e(donnees.get('description_page', titre + ' du bar à vin NEKTAR à Paris'))}">
  <link rel="preload" href="{prefixe}assets/polices/EBGaramond.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{prefixe}assets/polices/CormorantGaramond.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{prefixe}assets/carte.css">
  <script>document.documentElement.className += " js";</script>
</head>
<body>
  <div class="ecran">
    <main class="feuille" id="feuille">
      <header class="entete">
        <h1>{e(titre)}</h1>
        <img class="logo" src="{prefixe}assets/logo-nektar.svg" alt="NEKTAR, cave · bar à vin, Paris">
      </header>
      <div class="contenu" id="contenu">{sections}{note}
      </div>{legende}
    </main>
  </div>
  <script src="{prefixe}assets/ajuster.js"></script>
</body>
</html>
"""


PAGES = [
    ("donnees/menu.json", "index.html", ""),
    ("donnees/vins.json", "vins/index.html", "../"),
]


def main():
    for src, dest, prefixe in PAGES:
        chemin = RACINE / src
        if not chemin.exists():
            continue
        donnees = normaliser(json.loads(chemin.read_text(encoding="utf-8")))
        verifier(donnees, src)
        sortie = RACINE / dest
        sortie.parent.mkdir(parents=True, exist_ok=True)
        sortie.write_text(page_html(donnees, prefixe), encoding="utf-8")
        n = sum(len(s["articles"]) for s in donnees["sections"])
        print(f"✓ {dest} généré ({n} articles)")


if __name__ == "__main__":
    main()
