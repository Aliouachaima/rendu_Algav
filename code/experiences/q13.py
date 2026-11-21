

import math
import os

from mesures_lzmw import compresser_avec_mesures

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER_TEXTES = os.path.join(ICI, "textes")
DOSSIER_RESULTATS = os.path.join(ICI, "resultats")
FICHIERS = ["fib41", "tm29", "rs.13"]
PHI = (1 + math.sqrt(5)) / 2                       # le nombre d'or


def plus_grand_prefixe(nom):
    """Renvoie le chemin du plus grand préfixe de `nom` présent dans textes/ (ou None)."""
    meilleur = None
    for nom_prefixe in os.listdir(DOSSIER_TEXTES):
        if nom_prefixe.rsplit("_", 1)[0] == nom:
            chemin = os.path.join(DOSSIER_TEXTES, nom_prefixe)
            if meilleur is None or os.path.getsize(chemin) > os.path.getsize(meilleur):
                meilleur = chemin
    return meilleur


def main():
    os.makedirs(DOSSIER_RESULTATS, exist_ok=True)
    sortie = os.path.join(DOSSIER_RESULTATS, "q13_artificiels.csv")
    with open(sortie, "w") as csv:
        csv.write("fichier;n;k;noeuds;log_phi_n\n")
        for nom in FICHIERS:
            chemin = plus_grand_prefixe(nom)
            if chemin is None:
                print(nom, ": aucun préfixe dans textes/ (lancer preparer_corpus.py)")
                continue
            with open(chemin, "rb") as f:
                texte = f.read()
            n = 1024                                 # on commence à 1 Kio
            while n <= len(texte):
                m = compresser_avec_mesures(texte[:n], 24)
                log_phi_n = math.log(n) / math.log(PHI)
                csv.write(f"{nom};{n};{m['k']};{m['noeuds']};{log_phi_n:.2f}\n")
                csv.flush()
                print(f"{nom:6s} n = {n:>9d}   k = {m['k']:>4d}   log_phi(n) = {log_phi_n:5.1f}"
                      f"   noeuds = {m['noeuds']:>9d}   n + 257 = {n + 257:>9d}")
                n = n * 2                            # 1 Kio, 2 Kio, 4 Kio, ...
    print("Résultats écrits dans", sortie)


if __name__ == "__main__":
    main()
