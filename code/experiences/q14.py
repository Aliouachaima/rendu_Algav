
import os
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, ".."))      # pour trouver lzmw.py, dans code/
from lzmw import compresser                        # noqa: E402

DOSSIER_TEXTES = os.path.join(ICI, "textes")
DOSSIER_RESULTATS = os.path.join(ICI, "resultats")
FICHIERS = ["dblp.xml.0001.1", "dblp.xml.0001.2", "dna.001.1",
            "Escherichia_Coli", "einstein.en.txt"]
KIO = 1024

# Tailles mesurées : 64 Kio, 96 Kio, 128 Kio, 192 Kio, ... 12 Mio, 16 Mio.
# Les tailles intermédiaires (x 1,5) donnent plus de points autour de 1 Mio,
# là où se termine la première copie des textes pseudo-réels.
TAILLES = sorted([2 ** e for e in range(16, 25)] + [3 * 2 ** e for e in range(15, 23)])


def plus_grand_prefixe(nom):
    """Renvoie le chemin du plus grand préfixe de `nom` présent dans textes/ (ou None)."""
    meilleur = None
    for nom_prefixe in os.listdir(DOSSIER_TEXTES):
        if nom_prefixe.rsplit("_", 1)[0] == nom:
            chemin = os.path.join(DOSSIER_TEXTES, nom_prefixe)
            if meilleur is None or os.path.getsize(chemin) > os.path.getsize(meilleur):
                meilleur = chemin
    return meilleur


def taille_compressee(texte):
    """Compresse `texte` avec notre compresseur (b = 24) et renvoie la taille du résultat."""
    dossier_tmp = tempfile.mkdtemp()
    entree = os.path.join(dossier_tmp, "prefixe.txt")
    sortie = os.path.join(dossier_tmp, "prefixe.lzmw")
    with open(entree, "wb") as f:
        f.write(texte)
    compresser(entree, sortie, 24)
    taille = os.path.getsize(sortie)
    os.remove(entree)
    os.remove(sortie)
    os.rmdir(dossier_tmp)
    return taille


def main():
    os.makedirs(DOSSIER_RESULTATS, exist_ok=True)
    sortie = os.path.join(DOSSIER_RESULTATS, "q14_taux.csv")
    with open(sortie, "w") as csv:
        csv.write("fichier;n;taille_compressee;taux\n")
        for nom in FICHIERS:
            chemin = plus_grand_prefixe(nom)
            if chemin is None:
                print(nom, ": aucun préfixe dans textes/ (lancer preparer_corpus.py)")
                continue
            with open(chemin, "rb") as f:
                texte = f.read()
            for n in TAILLES:
                if n > len(texte):
                    break
                t = taille_compressee(texte[:n])
                taux = t / n
                csv.write(f"{nom};{n};{t};{taux:.5f}\n")
                csv.flush()
                print(f"{nom:18s} n = {n // KIO:>6d} Kio   taille compressée = {t:>9d}   taux = {taux:.4f}")
    print("Résultats écrits dans", sortie)


if __name__ == "__main__":
    main()