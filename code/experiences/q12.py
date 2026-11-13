import os
import sys
import tempfile
ICI = os.path.dirname(os.path.abspath(__file__))     # le dossier de ce script : code/experiences/
sys.path.insert(0, os.path.join(ICI, ".."))          # on ajoute code/ aux dossiers où Python cherche
from lzmw import compresser, decompresser             # noqa: E402

DOSSIER_TEXTES = os.path.join(ICI, "textes")          # les préfixes (fabriqués par preparer_corpus.py)
DOSSIER_RESULTATS = os.path.join(ICI, "resultats")    # le fichier CSV des résultats

#Renvoie la liste des (nom du fichier du corpus, chemin du préfixe) triée par fichier puis par taille
def liste_des_prefixes():
    prefixes = []
    for nom_prefixe in os.listdir(DOSSIER_TEXTES):
        if nom_prefixe.startswith("."):              # fichiers cachés (.DS_Store...) : on les ignore
            continue
        chemin = os.path.join(DOSSIER_TEXTES, nom_prefixe)
        nom = nom_prefixe.rsplit("_", 1)[0]          # "fib41_4M" -> "fib41"
        taille = os.path.getsize(chemin)
        prefixes.append((nom, taille, chemin))
    prefixes.sort()                                  # trie par nom, puis par taille
    resultat = []
    for nom, taille, chemin in prefixes:             # on enlève la taille, qui ne servait qu'au tri
        resultat.append((nom, chemin))
    return resultat

# Compresse puis décompresse, Renvoie True si on retrouve exactement le fichier de départ
def aller_retour(chemin):
    dossier_tmp = tempfile.mkdtemp()                         # un dossier temporaire vide
    compresse = os.path.join(dossier_tmp, "prefixe.lzmw")    # le fichier compressé
    retrouve = os.path.join(dossier_tmp, "prefixe.txt")      # le fichier décompressé
    compresser(chemin, compresse, 24)                        # ta compression (b = 24)
    decompresser(compresse, retrouve)                        # la décompression de ta binôme
    with open(chemin, "rb") as f1, open(retrouve, "rb") as f2:
        identique = f1.read() == f2.read()                   # comparaison octet par octet
    os.remove(compresse)                                     # on nettoie
    os.remove(retrouve)
    os.rmdir(dossier_tmp)
    return identique

def main():
    os.makedirs(DOSSIER_RESULTATS, exist_ok=True)            # crée resultats/ s'il n'existe pas
    sortie = os.path.join(DOSSIER_RESULTATS, "q12_corpus.csv")
    with open(sortie, "w") as csv:
        csv.write("fichier;n;octets_distincts;aller_retour_ok\n")   # ligne d'en-tête
        for nom, chemin in liste_des_prefixes():
            with open(chemin, "rb") as f:
                texte = f.read()
            n = len(texte)                                   # taille du préfixe en octets
            distincts = len(set(texte))                      # nombre d'octets différents
            ok = aller_retour(chemin)                        # compression puis décompression
            csv.write(f"{nom};{n};{distincts};{ok}\n")
            csv.flush()                                      # écrit la ligne tout de suite sur le disque
            print(f"{nom:20s} n = {n:>9d}   octets distincts = {distincts:3d}   "
                  f"aller-retour : {'OK' if ok else 'ECHEC'}")
    print("Résultats écrits dans", sortie)

if __name__ == "__main__":
    main()

