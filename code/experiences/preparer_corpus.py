import gzip
import os
import sys
import urllib.request

ADRESSE = "https://pizzachili.dcc.uchile.cl/repcorpus/"
MIO = 1024 * 1024                       # 1 Mio = 2^20 octets (taille d'une copie du corpus)

# Les fichiers choisis
FICHIERS = [
    ("artificial", "fib41"),
    ("artificial", "tm29"),
    ("artificial", "rs.13"),
    ("pseudo-real", "dblp.xml.0001.1"),
    ("pseudo-real", "dblp.xml.0001.2"),
    ("pseudo-real", "dna.001.1"),
    ("real", "Escherichia_Coli"),
    ("real", "einstein.en.txt"),
]

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER_CORPUS = os.path.join(ICI, "corpus")    # si le téléchargement automatqiue échoue
DOSSIER_TEXTES = os.path.join(ICI, "textes")    # le script écrit les préfixes ici 

# Elle lit par blocs de 1 Mio, jusqu’à avoir taille octets.
def lire_debut(flux, taille):
    morceaux = []
    deja_lu = 0
    while deja_lu < taille:
        bloc = flux.read(min(MIO, taille - deja_lu))
        if not bloc:                     # si le fichier est plus petit que taille
            break
        morceaux.append(bloc)
        deja_lu = deja_lu + len(bloc)
    return b"".join(morceaux)

# télécharger et decompresser et appeler la fonction lire_debut et retourne les 16 MO
def debut_du_fichier(famille, nom, taille):
    # 1) fichier déjà présent dans corpus/ (téléchargé à la main)
    for chemin in (os.path.join(DOSSIER_CORPUS, nom), os.path.join(DOSSIER_CORPUS, nom + ".gz")):
        if os.path.isfile(chemin):
            print("   fichier local :", chemin)
            if chemin.endswith(".gz"):
                with gzip.open(chemin, "rb") as f:
                    return lire_debut(f, taille)
            with open(chemin, "rb") as f:
                return lire_debut(f, taille)
    # 2) sinon, téléchargement du .gz, décompressé au fur et à mesure
    url = ADRESSE + famille + "/" + nom + ".gz"
    print("   téléchargement :", url)
    with urllib.request.urlopen(url) as reponse:
        with gzip.GzipFile(fileobj=reponse) as f:
            return lire_debut(f, taille)


def main():
    taille_max = 16
    if len(sys.argv) > 1:
        taille_max = int(sys.argv[1])
    os.makedirs(DOSSIER_TEXTES, exist_ok=True)

    for famille, nom in FICHIERS:
        print(nom)
        # tailles des préfixes : 1, 2, 4, 8, ... jusqu'à taille_max Mio
        tailles = []
        t = 1
        while t <= taille_max:
            tailles.append(t)
            t = t * 2
        # préfixes déjà tous présents : rien à faire
        manquants = [t for t in tailles
                     if not os.path.isfile(os.path.join(DOSSIER_TEXTES, f"{nom}_{t}M"))]
        if not manquants:
            print("   déjà prêt")
            continue
        try:
            debut = debut_du_fichier(famille, nom, tailles[-1] * MIO)
        except Exception as e:           # réseau, fichier introuvable...
            print("   ERREUR :", e)
            print("   -> télécharger", nom, "à la main et le placer dans", DOSSIER_CORPUS)
            continue
        for t in tailles:
            if t * MIO > len(debut):     # le fichier est plus petit que ce préfixe
                break
            chemin = os.path.join(DOSSIER_TEXTES, f"{nom}_{t}M")
            with open(chemin, "wb") as f:
                f.write(debut[:t * MIO])
            print(f"   {nom}_{t}M : {t * MIO} octets, {len(set(debut[:t * MIO]))} octets distincts")


if __name__ == "__main__":
    main()
