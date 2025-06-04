import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

def load_and_plot(filename, label, color, linestyle='-', linewidth=3, annotate=True):
    try:
        with open(filename, encoding='latin1') as f:
            lines = f.readlines()

        # Trouver la première ligne 100 % numérique avec au moins 8 colonnes
        start_index = None
        for i, line in enumerate(lines):
            tokens = line.strip().split()
            if len(tokens) < 8:
                continue
            try:
                _ = [float(tok) for tok in tokens[:8]]
                start_index = i
                break
            except ValueError:
                continue

        if start_index is None:
            print(f"[Avertissement] Aucune ligne de données détectée dans {filename}")
            return

        data_str = "".join(lines[start_index:])
        data = np.loadtxt(StringIO(data_str))

        if data.ndim == 1:
            data = np.expand_dims(data, axis=0)

        if data.shape[1] < 7:
            print(f"[Avertissement] Données insuffisantes dans {filename}")
            return

        x = data[:, 5]  # colonne 6
        y = data[:, 6]  # colonne 7

        plt.plot(x, y, label=label, color=color,
                 linestyle=linestyle, linewidth=linewidth)

        if annotate:
            # Annotation à droite du dernier point de la courbe
            plt.annotate(label,
                         xy=(x[-1], y[-1]),
                         xytext=(5, 0),
                         textcoords='offset points',
                         color=color,
                         fontsize=12,
                         va='center')

    except Exception as e:
        print(f"[ERREUR] Fichier {filename} : {e}")


def plot_all(courbes, title=None, xlabel=None, ylabel=None, annotate=True):
    plt.figure(figsize=(8, 7.2))
    plt.grid(color="#C0C0C0")
    plt.yscale("log")
    plt.ylim(1e-12, 1)
    plt.xlim(0, 0.05)
    plt.tick_params(axis='both', which='both', direction='in', top=True, right=True)

    if xlabel:
        plt.xlabel(xlabel, fontsize=15, fontweight='bold')
    else:
        plt.xlabel("C[H]", fontsize=15, fontweight='bold')

    if ylabel:
        plt.ylabel(ylabel, fontsize=15, fontweight='bold')
    else:
        plt.ylabel("Point defect concentrations", fontsize=15, fontweight='bold')

    if title:
        # Equivalent to "set label" centered at (0.03, 0.2)
        plt.text(0.03, 0.2, title,
                 fontsize=14, fontweight='bold', ha='center')

    for fichier, etiquette, couleur, *style in courbes:
        linestyle = style[0] if len(style) > 0 else '-'
        linewidth = style[1] if len(style) > 1 else 3
        load_and_plot(fichier, etiquette, couleur, linestyle, linewidth, annotate)

    plt.tight_layout()

    # Si annotations, on n'affiche pas la légende globale,
    # sinon on peut la mettre (à gauche ou à droite)
    if not annotate:
        plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5),
                   fontsize=12, frameon=True)

    plt.savefig("conc_tin_d_H.eps", format='eps')
    plt.savefig("conc_tin_d_H.pdf", format='pdf')
    plt.savefig("conc_tin_d_H.jpg", format='jpg', dpi=300)
    plt.show()


# Liste des courbes : (fichier, label, couleur, [linestyle, linewidth])
courbes = [
    ('TiN_adpi_L_r_1', r"$V_{N}$", "blue"),
    ('TiN_adpi_1_r_2', r"$N_{Ti}$", "black"),
    ('TiN_adpi_1_r_3', r"$N_{8c}$", "black", '--', 2),
    ('TiN_adpi_L_r_2', r"$V_{Ti}$", "green"),
    ('TiN_adpi_2_r_1', r"$Ti_{N}$", "red"),
    ('TiN_adpi_2_r_3', r"$Ti_{8c}$", "red", '--', 2),
    ('TiN_adpi_3_r_1', r"$H_{N}$", "orange"),
    ('TiN_adpi_3_r_2', r"$H_{Ti}$", "purple"),
    ('TiN_adpi_3_r_3', r"$H_{8c}$", "purple", '--', 2)
]

plot_all(
    courbes,
    title=r"$\mathrm{Ti_{0.51}N_{0.49} + H\ at\ 1000K}$",
    xlabel="C[H]",
    ylabel="Point defect concentrations",
    annotate=True  # Passe à False pour légende classique
)

