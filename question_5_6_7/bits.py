
TAILLE_TAMPON = 1 << 16          # 64 Ko : taille des blocs lus / ecrits sur le disque



# Question 5 : affichage d'un fichier binaire sous forme de chaine de bits
def lecture(fichier_bin):
    
    with open(fichier_bin, "rb") as f:
        contenu = f.read()
    chaine = "".join(format(octet, "08b") for octet in contenu)
    print(chaine)
    return chaine


#print("Question 5 : contenu de fichier.bin")
#resultat = lecture("fichier.bin")
#print("Attendu    :", "1001101110100000")
#print("Correct ?  :", resultat == "1001101110100000")

# les commandes pour voir le contenue de fichier.bin : 
#ls -l fichier.bin      # la taille affichée doit être 2 (octets)
#xxd fichier.bin        # affiche le contenu en hexadécimal : 9ba0   (155 160)

# Question 6 : fichier texte de '0'/'1'  ->  fichier binaire
def ecriture(fichier_chaine, fichier_bin):
    with open(fichier_chaine, "r") as f:
        chaine = f.read().strip() #(strip pour enlever les espaces et les sauts de ligne)
    for c in chaine: # si au moins un caractère n'est ni 0 ni 1
        if c != "0" and c != "1":
            raise ValueError("le fichier doit contenir uniquement des 0 et des 1")
    chaine += "0" * (-len(chaine) % 8)                 # bourrage
    liste = []                              # liste vide qui va recevoir les nombres
    i = 0                                   # position du début de l'octet courant
    while i < len(chaine):
        morceau = chaine[i:i + 8]           # les 8 caractères à partir de la position i
        nombre = int(morceau, 2)            # (lecture en base 2)
        liste.append(nombre)                # on ajoute le nombre à la fin de la liste
        i = i + 8                           # on passe aux 8 caractères suivants
    octets = bytes(liste)                   # les vrais octets
    with open(fichier_bin, "wb") as f:
        f.write(octets)

#print("Question 6 : fichier_chaine.txt -> fichier2.bin")
#ecriture("fichier_chaine.txt", "fichier2.bin")
#resultat = lecture("fichier2.bin")
#print("Attendu    :", "1001101110100000")
#print("Correct ?  :", resultat == "1001101110100000")
#print()

# Question 7 : écriture / lecture d'entiers de largeur w, avec tampon

class EcrivainBits:

    def __init__(self, f):
        self.f = f              #fichier
        self.acc = 0            # bits en attente (moins de 8 après chaque appel)
        self.nbits = 0          # nombre de bits en attente
        self.tampon = bytearray() # accumule les octets complets

#on ne peut écrire dans un fichier que des octets entiers (8 bits), alors que les codes font 9, 10, 11… bits. 
#La fonction doit donc garder de côté les bits qui ne forment pas encore un octet complet, en attendant le code suivant.
    def ecrire_code(self, c, w):
       # ÉTAPE 1 : ajouter le nouveau code derrière les bits qui attendaient
        self.acc = (self.acc << w) | c  #on décale acc par w bits et on ajoute le c 
        self.nbits += w # on ajoute les w bits qu'on a ajouter 
        # ÉTAPE 2 : sortir tous les octets complets
        while self.nbits >= 8:
            self.nbits -= 8
            self.tampon.append((self.acc >> self.nbits) & 0xFF)
        #Après la boucle, il reste moins de 8 bits qui n’ont pas pu former un octet. 
        #on garde ce reste et efface les bits déjà envoyés dans le panier.    
        self.acc = self.acc % (2 ** self.nbits)
        # ÉTAPE 3 : si le panier est plein, l'envoyer sur le disque
        if len(self.tampon) >= TAILLE_TAMPON:
            self.f.write(self.tampon)
            self.tampon = bytearray()

    def fermer(self):
        #Complète le dernier octet par des 0 et vide le tampon
        if self.nbits > 0:
            self.tampon.append((self.acc << (8 - self.nbits)) & 0xFF)
            self.acc = self.nbits = 0
        self.f.write(self.tampon)
        self.tampon = bytearray()


class LecteurBits:

    def __init__(self, f):
        self.f = f
        self.tampon = b""
        self.pos = 0            # position dans le tampon
        self.acc = 0            # bits déjà extraits du tampon mais non consommés
        self.nbits = 0

    def lire_code(self, w):
        # ÉTAPE 1 : remplir la réserve jusqu'à avoir au moins w bits
        while self.nbits < w:
            if self.pos >= len(self.tampon):
                self.tampon = self.f.read(TAILLE_TAMPON) #on cherche dans le tampon,on ne va pas sur le disque à chaque octet, comme ecriture.
                self.pos = 0 #debut
                if not self.tampon:
                    return None #read ne renvoie rien, fin fichier que bourrage
            self.acc = (self.acc << 8) | self.tampon[self.pos]
            self.pos += 1
            self.nbits += 8
        # ÉTAPE 2 : prendre les w premiers bits = le code    
        self.nbits -= w
        c = self.acc >> self.nbits
        # ÉTAPE 3 : garder le reste pour la prochaine fois
        self.acc = self.acc % (2 ** self.nbits)
        return c

#pour le test
def ecrire_codes(fichier_bin, codes, largeurs):
    """Écrit la suite `codes` avec les `largeurs` données (utile pour la Q7)."""
    with open(fichier_bin, "wb") as f:
        e = EcrivainBits(f)
        for c, w in zip(codes, largeurs):
            e.ecrire_code(c, w)
        e.fermer()

if __name__ == "__main__":
    print("Question 7 : vérification avec la fonction lecture")
    codes    = [97, 98, 256, 256, 256, 97, 258, 97]
    largeurs = [8,  8,  9,   9,   9,   9,  9,   9]
    ecrire_codes("q7.bin", codes, largeurs)      # écriture avec la question 7
    resultat = lecture("q7.bin")                 # affichage avec la question 5
    attendu = ("01100001" "01100010" "100000000" "100000000" "100000000"
               "001100001" "100000010" "001100001" "00")
    print("Attendu    :", attendu)
    print("Correct ?  :", resultat == attendu)

    print()
    print("Question 7 : relecture des codes avec lire_code")
    with open("q7.bin", "rb") as f:
        lecteur = LecteurBits(f)
        relus = []
        for w in largeurs:
            relus.append(lecteur.lire_code(w))
        fin = lecteur.lire_code(9)
    print("Codes relus :", relus)
    print("Attendu     :", codes)
    print("Correct ?   :", relus == codes)
    print("Code après la fin (doit être None) :", fin)
#print (bin(0b101 >> 2))    