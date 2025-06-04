import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, Checkbutton, BooleanVar, filedialog
import os
from io import StringIO

# Pour stocker la figure globalement
current_fig = None

def load_data(filename):
    try:
        with open(filename, encoding='latin1') as f:
            lines = f.readlines()

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
            print(f"[Avertissement] Aucune ligne de données dans {filename}")
            return None, None

        data_str = "".join(lines[start_index:])
        data = np.loadtxt(StringIO(data_str))

        if data.ndim == 1:
            data = np.expand_dims(data, axis=0)

        if data.shape[1] < 7:
            print(f"[Avertissement] Colonnes insuffisantes dans {filename}")
            return None, None

        return data[:, 5], data[:, 6]

    except Exception as e:
        print(f"[ERREUR] {filename} : {e}")
        return None, None

def plot_and_return_figure(file_prefix, title, xlabel, ylabel, annotate):
    fig, ax = plt.subplots(figsize=(8, 7.2))
    ax.grid(color="#C0C0C0")
    ax.set_yscale("log")
    ax.set_ylim(1e-12, 1)
    ax.set_xlim(0, 0.05)
    ax.set_xlabel(xlabel, fontsize=15, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=15, fontweight='bold')
    ax.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    ax.text(0.03, 0.2, title, fontsize=14, fontweight='bold', ha='center')

    courbes = [
        ('L_r_1', r"$V_{N}$", "blue", '-', 3),
        ('1_r_2', r"$N_{Ti}$", "black", '-', 3),
        ('1_r_3', r"$N_{8c}$", "black", '--', 2),
        ('L_r_2', r"$V_{Ti}$", "green", '-', 3),
        ('2_r_1', r"$Ti_{N}$", "red", '-', 3),
        ('2_r_3', r"$Ti_{8c}$", "red", '--', 2),
        ('3_r_1', r"$H_{N}$", "orange", '-', 3),
        ('3_r_2', r"$H_{Ti}$", "purple", '-', 3),
        ('3_r_3', r"$H_{8c}$", "purple", '--', 2)
    ]

    plotted = False
    for suffix, label, color, style, width in courbes:
        filename = f"{file_prefix}_{suffix}"
        x, y = load_data(filename)
        if x is None or y is None:
            continue
        ax.plot(x, y, label=label, color=color, linestyle=style, linewidth=width)
        if annotate:
            ax.annotate(label, xy=(x[-1], y[-1]), xytext=(5, 0),
                        textcoords='offset points', fontsize=10, color=color, va='center')
        plotted = True

    if not plotted:
        print("[ERREUR] Aucun fichier valide trouvé.")
        return None

    if not annotate:
        ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=12, frameon=True)

    fig.tight_layout()
    return fig

def run_plot():
    global current_fig
    prefix = file_prefix_entry.get().strip()
    title = title_entry.get().strip()
    xlabel = xlabel_entry.get().strip()
    ylabel = ylabel_entry.get().strip()
    current_fig = plot_and_return_figure(prefix, title, xlabel, ylabel, annotate_var.get())
    if current_fig:
        current_fig.show()

def save_figure():
    global current_fig
    if current_fig is None:
        print("[INFO] Aucun graphique à sauvegarder.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                             filetypes=[
                                                 ("PDF", "*.pdf"),
                                                 ("JPG", "*.jpg"),
                                                 ("PNG", "*.png"),
                                                 ("EPS", "*.eps")
                                             ])
    if file_path:
        ext = os.path.splitext(file_path)[1][1:]  # sans le point
        current_fig.savefig(file_path, format=ext, dpi=300 if ext == 'jpg' else None)
        print(f"[OK] Fichier sauvegardé : {file_path}")

def browse_prefix():
    path = filedialog.askopenfilename()
    if path:
        base = os.path.splitext(os.path.basename(path))[0]
        file_prefix_entry.delete(0, 'end')
        file_prefix_entry.insert(0, base.rsplit('_', 2)[0])

# Interface Tkinter
root = Tk()
root.title("Traceur de concentrations TiN")

Label(root, text="Préfixe fichiers (ex: TiN_adpi)").grid(row=0, column=0, sticky='e')
file_prefix_entry = Entry(root, width=30)
file_prefix_entry.grid(row=0, column=1)
Button(root, text="Parcourir", command=browse_prefix).grid(row=0, column=2)

Label(root, text="Titre du graphique").grid(row=1, column=0, sticky='e')
title_entry = Entry(root, width=30)
title_entry.insert(0, r"$\mathrm{Ti_{0.51}N_{0.49} + H\ at\ 1000K}$")
title_entry.grid(row=1, column=1)

Label(root, text="Label axe X").grid(row=2, column=0, sticky='e')
xlabel_entry = Entry(root, width=30)
xlabel_entry.insert(0, "C[H]")
xlabel_entry.grid(row=2, column=1)

Label(root, text="Label axe Y").grid(row=3, column=0, sticky='e')
ylabel_entry = Entry(root, width=30)
ylabel_entry.insert(0, "Point defect concentrations")
ylabel_entry.grid(row=3, column=1)

annotate_var = BooleanVar(value=True)
Checkbutton(root, text="Annoter les courbes (à côté)", variable=annotate_var).grid(row=4, column=1, sticky='w')

Button(root, text="Tracer", command=run_plot, bg="#4CAF50", fg="white").grid(row=5, column=1, pady=5)
Button(root, text="Sauvegarder…", command=save_figure, bg="#2196F3", fg="white").grid(row=6, column=1, pady=5)

root.mainloop()

