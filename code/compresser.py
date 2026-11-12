import os
import sys
import time

from lzmw import B_DEFAUT, B_MAX, B_MIN, compresser

def erreur(message):
    print("compresser : " + message, file=sys.stderr)
    print("Usage : compresser <entree> <sortie> [b]", file=sys.stderr)
    sys.exit(1)

def main():
    # 1. lire et verifier les arguments
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        erreur("nombre d'arguments incorrect")
    fichier_entree = sys.argv[1]
    fichier_sortie = sys.argv[2]
    b = B_DEFAUT
    if len(sys.argv) == 4:
        if not sys.argv[3].isdigit():
            erreur("b doit être un entier")
        b = int(sys.argv[3])
        if b < B_MIN or b > B_MAX:
            erreur("b doit être compris entre 9 et 24")
    if not os.path.isfile(fichier_entree):
        erreur("fichier introuvable : " + fichier_entree)

    # 2. compresser en mesurant le temps
    debut = time.perf_counter()
    k, taille_dico = compresser(fichier_entree, fichier_sortie, b)
    temps_ms = (time.perf_counter() - debut) * 1000

    # 3. ecrire une ligne dans le journal compression.txt
    taille_in = os.path.getsize(fichier_entree)
    taille_out = os.path.getsize(fichier_sortie)
    if taille_in == 0:
        taux = 0.0                      # texte vide : on évite la division par zéro
    else:
        taux = taille_out / taille_in
    ligne = (f"{fichier_entree};{fichier_sortie};{taille_in};{taille_out};"
             f"{taux:.5f};{temps_ms:.3f};{b};{k};{taille_dico}\n")
    with open("compression.txt", "a") as journal:
        journal.write(ligne)


if __name__ == "__main__":
    main()