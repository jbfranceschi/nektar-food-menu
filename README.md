# Carte NEKTAR

Menu en ligne du bar à vin NEKTAR : https://food.menu.nektar-paris.com

## Organisation

| Fichier | Rôle |
|---|---|
| `donnees/menu.json` | **Le contenu du menu** : la seule chose à modifier au quotidien |
| `assets/carte.css` | Le design (couleurs, polices, mise en page) |
| `assets/ajuster.js` | Fait tenir la carte sur **une seule page A4** : la taille du texte s'adapte au nombre d'articles, et chaque nom de plat reste sur une ligne avec ses allergènes |
| `assets/logo-nektar.svg`, `assets/polices/` | Logo vectoriel et polices hébergés localement |
| `outils/generer.py` | Régénère `index.html` à partir des données |
| `outils/apercu.py` | Produit des aperçus PNG (ordinateur, mobile) et un PDF A4 |
| `index.html` | Page publiée (générée, ne pas modifier à la main) |

## Mettre à jour le menu

1. Modifier `donnees/menu.json`. Un article ressemble à ceci :

   ```json
   {
     "nom": "Mousse au chocolat",
     "description": "Chocolat noir de caractère accompagné de sa fleur de sel.",
     "prix": "8 €",
     "allergenes": ["oeufs", "lactose"]
   }
   ```

   Allergènes possibles : `gluten`, `oeufs`, `lactose`, `moutarde`, `poisson`,
   `fruits_a_coque`, `arachide`, `crustaces`, `mollusques`, `celeri`, `soja`,
   `sesame`, `sulfites`, `lupin`. La légende en bas de page n'affiche que ceux
   présents sur la carte.

2. Générer la page : `python3 outils/generer.py`
3. Aperçu : `python3 outils/apercu.py` → dossier `apercu/` (PNG haute définition + PDF A4 d'une page ; le script s'arrête en erreur si le PDF dépasse une page)
4. Publier : commit + push, puis mise en ligne sur l'hébergement.

## Vins au verre

Créer `donnees/vins.json` (même format, avec des sections) : le script
générera automatiquement `vins/index.html`.

```json
{
  "titre": "Vins au verre",
  "sections": [
    { "titre": "Blancs", "articles": [
      { "nom": "Domaine X — Chablis 2023", "description": "Notes de dégustation…", "prix": "9 €" }
    ]}
  ]
}
```
