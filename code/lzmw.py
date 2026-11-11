import math
import sys
import os

from question_5_6_7 import bits

def decompresser(fichier_compresse, fichier_sortie):
    with open(fichier_compresse, mode='rb') as f_i, open(fichier_sortie, "wb") as f_o:
        D = [bytes([v]) for v in range(256)]
        mots_vus = set(D)
        P = b''
        b = f_i.read(1)[0]
        lire = bits.LecteurBits(f_i)
        while(True):
            w = min(b, math.ceil(math.log2(len(D))))
            c = lire.lire_code(w)
            if c is None:
                break
            M = D[c]
            f_o.write(M)
            if P:
                PM = P + M
                if len(D) < 2**b and PM not in mots_vus:
                    D.append(PM)
                    mots_vus.add(PM)
            P = M
