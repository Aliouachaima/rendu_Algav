"""Mesures internes au compresseur, pour l'étude expérimentale (questions 13, 15 et 16).

On ne modifie pas lzmw.py : on refait ici la même boucle de compression, avec le même
Trie (importé de lzmw.py), mais sans écrire de fichier, et en comptant ce qu'on veut mesurer.
"""
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, ".."))      # pour trouver lzmw.py, dans code/
from lzmw import Trie                              # noqa: E402


def compresser_avec_mesures(texte, b=24):
    """Fait la compression LZMW de `texte` (des octets) avec le dictionnaire limité à 2^b
    entrées, sans rien écrire, et renvoie un dictionnaire Python avec :
      k        : le nombre de phrases (= nombre de codes écrits),
      taille   : la taille finale du dictionnaire,
      noeuds   : le nombre de nœuds du trie à la fin (question 13),
      visites  : le nombre total de nœuds visités pendant les recherches (question 16),
      pos_gel  : la position du texte où le dictionnaire devient plein, -1 si jamais (question 15).
    """
    taille_max = 2 ** b
    trie = Trie()
    k = 0
    visites_total = 0 # POUR la question 16
    pos_gel = -1 # position ou le dictionnaire devient plein (pour la question 15)
    i = 0
    noeud_p = -1
    while i < len(texte):
        noeud_m, fin, visites = trie.plus_longue_phrase(texte, i)
        visites_total = visites_total + visites
        k = k + 1                                  # le compresseur écrirait ici le code de M
        if noeud_p >= 0 and trie.taille < taille_max:
            trie.ajouter(noeud_p, texte, i, fin)
            if trie.taille == taille_max:          # le dictionnaire vient d'être rempli
                pos_gel = fin
        noeud_p = noeud_m
        i = fin
    return {"k": k, "taille": trie.taille, "noeuds": len(trie.code),
            "visites": visites_total, "pos_gel": pos_gel}


if __name__ == "__main__":
    # Vérification : on doit trouver les mêmes k et |D| que le compresseur de lzmw.py
    import tempfile
    from lzmw import compresser
    dossier_tests = os.path.join(ICI, "..", "tests")
    sortie = os.path.join(tempfile.mkdtemp(), "verif.lzmw")
    for nom, b in [("t3_abab", 24), ("t4_a20", 24), ("t5_abracadabra", 24),
                   ("t6_gel", 24), ("t6_gel", 10), ("t6_gel", 9)]:
        chemin = os.path.join(dossier_tests, nom + ".txt")
        with open(chemin, "rb") as f:
            texte = f.read()
        m = compresser_avec_mesures(texte, b)
        k, taille = compresser(chemin, sortie, b)
        identique = (m["k"] == k and m["taille"] == taille)
        print(f"{nom:15s} b = {b:2d} : {m}   même k et |D| que compresser : {identique}")
