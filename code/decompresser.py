#!/usr/bin/env python3
import os
import sys
import time
from lzmw import decompresser

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 decompresser.py <entree.lzmw> <sortie.txt>", file=sys.stderr)
        sys.exit(1)

    fichier_entree = sys.argv[1]
    fichier_sortie = sys.argv[2]

    debut = time.time()
    
    decompresser(fichier_entree, fichier_sortie)
    
    fin = time.perf_counter()
    temps_ms = (fin - debut) * 1000.0

    with open(fichier_entree, "rb") as f:
        taille_in = os.path.getsize(fichier_entree)
    with open(fichier_sortie, "rb") as f:
        taille_out = os.path.getsize(fichier_sortie)

    ligne_log = f"{fichier_entree};{fichier_sortie};{taille_in};{taille_out};{temps_ms:.3f}\n"
    with open("decompression.txt", "a") as log:
        log.write(ligne_log)

if __name__ == "__main__":
    main()