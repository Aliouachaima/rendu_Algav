
import csv
import os

import matplotlib
matplotlib.use("Agg")                    
import matplotlib.pyplot as plt          
import matplotlib.ticker                

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER_RESULTATS = os.path.join(ICI, "resultats")
DOSSIER_FIGURES = os.path.join(ICI, "figures")


STYLE = {
    "fib41": ("#2a78d6", "o"), "tm29": ("#eb6834", "s"), "rs.13": ("#1baf7a", "^"),
    "dblp.xml.0001.1": ("#eda100", "D"), "dblp.xml.0001.2": ("#e87ba4", "v"),
    "dna.001.1": ("#008300", "P"), "Escherichia_Coli": ("#6250d6", "X"),
    "einstein.en.txt": ("#e34948", "*"),
}
TAILLES = [2 ** e for e in range(10, 25, 2)]  


def nom_taille(n):
    """1024 -> '1 Kio', 1048576 -> '1 Mio'."""
    if n >= 2 ** 20:
        return f"{n // 2 ** 20} Mio"
    return f"{n // 2 ** 10} Kio"


def lire(nom_fichier):
    """Lit un CSV de resultats/ et renvoie {fichier: [lignes triées par n]}, ou None."""
    chemin = os.path.join(DOSSIER_RESULTATS, nom_fichier)
    if not os.path.isfile(chemin):
        return None
    donnees = {}
    with open(chemin) as f:
        for ligne in csv.DictReader(f, delimiter=";"):
            donnees.setdefault(ligne["fichier"], []).append(ligne)
    for lignes in donnees.values():
        lignes.sort(key=lambda l: int(l["n"]))
    return donnees


def axe_des_tailles(ax):
    """Échelle logarithmique (base 2) pour la taille des préfixes, avec des graduations lisibles."""
    ax.set_xscale("log", base=2)
    ax.set_xticks(TAILLES)
    ax.set_xticklabels([nom_taille(n) for n in TAILLES])
    ax.set_xlabel("taille n du préfixe (échelle logarithmique)")
    ax.grid(True, color="#e4e3df", linewidth=0.6)


def enregistrer(fig, nom):
    os.makedirs(DOSSIER_FIGURES, exist_ok=True)
    for extension in ("png", "pdf"):
        fig.savefig(os.path.join(DOSSIER_FIGURES, f"{nom}.{extension}"), bbox_inches="tight", dpi=160)
    plt.close(fig)
    print("figure écrite :", nom)


def courbes_q13():
    donnees = lire("q13_artificiels.csv")
    if donnees is None:
        return

    # Figure 1 : nombre de phrases k, comparé à la borne log_phi(n) de la question 4
    fig, ax = plt.subplots(figsize=(6.4, 4))
    for fichier, lignes in donnees.items():
        couleur, marqueur = STYLE.get(fichier, ("#555555", "o"))
        ax.plot([int(l["n"]) for l in lignes], [int(l["k"]) for l in lignes],
                color=couleur, marker=marqueur, markersize=4, linewidth=1.6, label=fichier)
    lignes = next(iter(donnees.values()))
    ax.plot([int(l["n"]) for l in lignes], [float(l["log_phi_n"]) for l in lignes],
            color="black", linestyle="--", linewidth=1.2, label="log_φ n (borne de la question 4)")
    axe_des_tailles(ax)
    ax.set_ylabel("nombre de phrases k")
    ax.set_title("Textes artificiels : nombre de phrases (b = 24)")
    ax.legend(frameon=False)
    enregistrer(fig, "q13_phrases")

    # Figure 2 : nombre de nœuds du trie rapporté à la borne n + 257 de la question 3
    fig, ax = plt.subplots(figsize=(6.4, 4))
    for fichier, lignes in donnees.items():
        couleur, marqueur = STYLE.get(fichier, ("#555555", "o"))
        ax.plot([int(l["n"]) for l in lignes],
                [int(l["noeuds"]) / (int(l["n"]) + 257) for l in lignes],
                color=couleur, marker=marqueur, markersize=4, linewidth=1.6, label=fichier)
    ax.axhline(1, color="black", linestyle="--", linewidth=1.2, label="borne de la question 3")
    axe_des_tailles(ax)
    ax.set_ylim(0.7, 1.05)
    ax.set_ylabel("nœuds du trie / (n + 257)")
    ax.set_title("Textes artificiels : taille du trie (b = 24)")
    ax.legend(frameon=False, loc="lower right")
    enregistrer(fig, "q13_noeuds")


def courbes_q14():
    donnees = lire("q14_taux.csv")
    if donnees is None:
        return
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for fichier, lignes in donnees.items():
        couleur, marqueur = STYLE.get(fichier, ("#555555", "o"))
        ax.plot([int(l["n"]) for l in lignes], [float(l["taux"]) for l in lignes],
                color=couleur, marker=marqueur, markersize=4, linewidth=1.6, label=fichier)
    # repère : fin de la première copie (1 Mio) des textes pseudo-réels
    ax.axvline(2 ** 20, color="#888784", linestyle=":", linewidth=1.2)
    ax.text(2 ** 20 * 1.08, 0.012, "fin de la 1re copie\n(pseudo-réels)", fontsize=7.5, color="#555555")
    axe_des_tailles(ax)
    ax.set_xlim(2 ** 16 / 1.3, 2 ** 24 * 1.3)
    ax.set_xticks([2 ** e for e in range(16, 25, 2)])
    ax.set_xticklabels([nom_taille(2 ** e) for e in range(16, 25, 2)])
    ax.set_yscale("log")
    ax.set_yticks([0.01, 0.02, 0.05, 0.1, 0.2, 0.5])
    ax.set_yticklabels(["0,01", "0,02", "0,05", "0,1", "0,2", "0,5"])
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())  
    ax.set_ylabel("taux de compression\n(taille compressée / taille du préfixe)")
    ax.set_title("Textes réels et pseudo-réels : taux de compression (b = 24)")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    enregistrer(fig, "q14_taux")


if __name__ == "__main__":
    courbes_q13()
    courbes_q14()