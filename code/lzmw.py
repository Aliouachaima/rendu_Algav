"""Compression et décompression LZMW."""
import math
from bits import LecteurBits, EcrivainBits

B_DEFAUT = 24          # valeur de b si l'utilisateur n'en donne pas
B_MIN, B_MAX = 9, 24   # valeurs de b autorisées par l'énoncé

def decompresser(fichier_compresse, fichier_sortie):
    with open(fichier_compresse, mode='rb') as f_i, open(fichier_sortie, "wb") as f_o:
        D = [bytes([v]) for v in range(256)]
        mots_vus = set(D)
        P = b''
        b = f_i.read(1)[0]
        lire = LecteurBits(f_i)
        while True:
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

def largeur(taille):
    return (taille - 1).bit_length()

class Trie:
  #Le dictionnaire sous forme d'arbre prefixe.

    def __init__(self):
        self.fils = {}           # fils[x * 256 + o] = nœud atteint depuis x par l'octet o
        self.code = [-1]         # code[x] = code du nœud x, ou -1 s'il n'est pas valide
                                 # le nœud 0 est la racine (mot vide) : pas une entrée
        for v in range(256):     # au départ, D contient les 256 octets
            self.fils[0 * 256 + v] = v + 1    # la flèche "v" part de la racine vers le nœud v + 1
            self.code.append(v)               # le nœud v + 1 est valide, avec le code v
        self.taille = 256        # |D| = 256 entrées au départ


    def plus_longue_phrase(self, texte, i):
        noeud = 0                # on part de la racine
        j = i                    # position de la prochaine lettre à lire
        dernier = -1             # dernier nœud valide rencontré
        fin = i                  # position juste après ce dernier nœud valide
        while j < len(texte):
            suivant = self.fils.get(noeud * 256 + texte[j])
            if suivant is None:  # pas de flèche pour cette lettre : on s'arrête
                break
            noeud = suivant      # on descend d'un cran
            j = j + 1            # et on avance d'une lettre
            if self.code[noeud] >= 0:   # nœud valide : on le retient
                dernier = noeud
                fin = j
        return dernier, fin, j - i  

    def ajouter(self, noeud_p, texte, debut, fin):     
        x = noeud_p                         # on part du nœud de P (son chemin existe déjà)
        for pos in range(debut, fin):       # on suit les lettres de M
            cle = x * 256 + texte[pos]
            y = self.fils.get(cle)
            if y is None:                   # le nœud n'existe pas : on le crée
                y = len(self.code)          # son numéro = le prochain numéro libre
                self.fils[cle] = y          # on crée la flèche qui y mène
                self.code.append(-1)        # nouveau nœud, pas encore valide
            x = y                           # on descend
        if self.code[x] >= 0:               # déjà valide : P·M est déjà dans D
            return False                    # doublon, on n'ajoute rien
        self.code[x] = self.taille          # le nœud devient valide, avec le code |D|
        self.taille = self.taille + 1       # D a une entrée de plus
        return True

def compresser(fichier_entree, fichier_sortie, b=B_DEFAUT):
    with open(fichier_entree, "rb") as f:
        texte = f.read()                          # tout le texte, sous forme d'octets
    taille_max = 2 ** b                           # taille maximale du dictionnaire
    trie = Trie()                                 # ligne 1 : D <- les 256 octets
    k = 0                                         # nombre de codes écrits
    with open(fichier_sortie, "wb") as f_sortie:
        f_sortie.write(bytes([b]))                # l'octet d'en-tête
        ecrivain = EcrivainBits(f_sortie)         # question 7
        i = 0                                     # ligne 3 : position dans le texte
        noeud_p = -1                              # ligne 2 : P <- mot vide
        while i < len(texte):                     # ligne 4
            noeud_m, fin, visites = trie.plus_longue_phrase(texte, i)
            ecrivain.ecrire_code(trie.code[noeud_m], largeur(trie.taille))
            k = k + 1
            if noeud_p >= 0 and trie.taille < taille_max:
                trie.ajouter(noeud_p, texte, i, fin)
            noeud_p = noeud_m                     # ligne 10 : P <- M
            i = fin                               # ligne 11 : on avance après M
        ecrivain.fermer()                         # bourrage + écriture du reste
    return k, trie.taille
