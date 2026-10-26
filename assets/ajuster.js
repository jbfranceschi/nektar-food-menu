/* Ajuste la carte pour qu'elle tienne TOUJOURS sur une seule page A4 :
   1. cherche la plus grande taille de texte (--s) où tout rentre,
      sans qu'aucun nom de plat (avec ses allergènes) ne passe à la ligne ;
   2. répartit l'espace restant entre les articles (--pad) ;
   3. à l'écran, agrandit/réduit la feuille pour remplir la largeur (--z). */
(function () {
  var feuille = document.getElementById("feuille");
  var contenu = document.getElementById("contenu");
  if (!feuille || !contenu) return;
  var LARGEUR = 1050, S_MIN = 0.4, S_MAX = 1.12;

  function deborde(el) {
    return el.scrollWidth > el.clientWidth + 0.5;
  }

  function tientSurLaPage() {
    if (contenu.scrollHeight > contenu.clientHeight + 0.5) return false;
    var lignes = feuille.querySelectorAll(".ligne");
    for (var i = 0; i < lignes.length; i++) if (deborde(lignes[i])) return false;
    return true;
  }

  function ajusterLegende() {
    var legende = feuille.querySelector(".legende");
    if (!legende) return;
    var ul = legende.querySelector("ul"), l = 1;
    legende.style.setProperty("--l", 1);
    while (deborde(ul) && l > 0.4) {
      l -= 0.04;
      legende.style.setProperty("--l", l.toFixed(2));
    }
  }

  function ajuster() {
    ajusterLegende();
    feuille.style.setProperty("--pad", "0px");
    var bas = S_MIN, haut = S_MAX;
    feuille.style.setProperty("--s", haut);
    if (!tientSurLaPage()) {
      for (var i = 0; i < 20; i++) {
        var m = (bas + haut) / 2;
        feuille.style.setProperty("--s", m);
        if (tientSurLaPage()) bas = m; else haut = m;
      }
      feuille.style.setProperty("--s", bas.toFixed(4));
    }
    var n = contenu.querySelectorAll(".article").length;
    var reste = contenu.clientHeight - contenu.scrollHeight;
    if (n && reste > 0) feuille.style.setProperty("--pad", (reste / (2 * n) - 0.05).toFixed(2) + "px");
  }

  function zoomer() {
    var w = Math.min(document.documentElement.clientWidth, 1100);
    feuille.style.setProperty("--z", (w / LARGEUR).toFixed(4));
  }

  function tout() {
    feuille.style.setProperty("--z", 1);
    ajuster();
    zoomer();
    feuille.classList.add("prete");
  }

  var pret = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  pret.then(tout, tout);
  window.addEventListener("resize", zoomer);
})();
