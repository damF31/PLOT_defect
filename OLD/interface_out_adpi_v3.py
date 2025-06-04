import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
import os
from io import StringIO

class DefectPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Défauts ponctuels – Visualiseur de concentrations")
        self.root.geometry("900x520")
        self.root.minsize(750, 400)

        self.system_name = tk.StringVar(value="TiN_adpi")
        self.num_atoms = tk.IntVar(value=3)
        self.num_sites = tk.IntVar(value=2)  # Ajout du nombre de sites
        self.atom_entries = []
        self.output_basename = tk.StringVar(value="conc_plot")
        self.title_text = tk.StringVar(value="Ti$_{0.51}$N$_{0.49}$ + H à 1000K")

        self.show_vacancies = tk.BooleanVar(value=True)
        self.show_substitutions = tk.BooleanVar(value=True)
        self.show_hydrogens = tk.BooleanVar(value=True)

        self.create_widgets()

    def create_widgets(self):
        # Saisie des paramètres
        param_frame = tk.LabelFrame(self.root, text="Paramètres système", padx=8, pady=4)
        param_frame.grid(row=0, column=0, sticky='nsew', padx=8, pady=5, columnspan=5)

        tk.Label(param_frame, text="Nom du système :").grid(row=0, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.system_name).grid(row=0, column=1, sticky='ew', columnspan=2)

        tk.Label(param_frame, text="Nombre d'atomes :").grid(row=1, column=0, sticky='e')
        num_atoms_entry = tk.Entry(param_frame, textvariable=self.num_atoms, width=5)
        num_atoms_entry.grid(row=1, column=1, sticky='w')
        tk.Button(param_frame, text="Mettre à jour", command=self.update_atom_inputs).grid(row=1, column=2, sticky='w')

        # Nouveau champ pour le nombre de sites
        tk.Label(param_frame, text="Nombre de sites réseau :").grid(row=1, column=3, sticky='e')
        tk.Entry(param_frame, textvariable=self.num_sites, width=5).grid(row=1, column=4, sticky='w')

        self.atom_frame = tk.Frame(param_frame)
        self.atom_frame.grid(row=2, column=0, columnspan=5, sticky='ew')
        self.update_atom_inputs()

        tk.Label(param_frame, text="Titre du graphique :").grid(row=3, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.title_text).grid(row=3, column=1, sticky='ew', columnspan=4)

        tk.Label(param_frame, text="Nom du fichier de sortie :").grid(row=4, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.output_basename).grid(row=4, column=1, sticky='ew', columnspan=2)
        tk.Button(param_frame, text="Sauvegarder", command=self.save_plot_dialog).grid(row=4, column=3, sticky='w')

        # Options de visualisation
        options_frame = tk.LabelFrame(self.root, text="Défauts à afficher", padx=8, pady=4)
        options_frame.grid(row=1, column=0, sticky='ew', padx=8, pady=0, columnspan=5)
        tk.Checkbutton(options_frame, text="Vacances", variable=self.show_vacancies).grid(row=0, column=0, sticky='w')
        tk.Checkbutton(options_frame, text="Substitutions", variable=self.show_substitutions).grid(row=0, column=1, sticky='w')
        # Option hydrogènes désactivée car non adaptée au nombre de sites générique, mais gardée si besoin
        tk.Checkbutton(options_frame, text="Défauts de l'atome 3", variable=self.show_hydrogens).grid(row=0, column=2, sticky='w')

        # Boutons principaux
        action_frame = tk.Frame(self.root)
        action_frame.grid(row=2, column=0, columnspan=5, pady=5)
        tk.Button(action_frame, text="Générer le graphique", command=self.generate_plot).pack(side='left', padx=10)
        tk.Button(action_frame, text="Quitter", command=self.root.quit).pack(side='left', padx=10)

        # Prévisualisation des fichiers lus
        self.preview_label = tk.Label(self.root, text="Fichiers lus :")
        self.preview_label.grid(row=3, column=0, sticky='w', padx=8, pady=2, columnspan=5)

        self.preview_text = tk.Text(self.root, height=8, width=100, state='disabled', wrap='none')
        self.preview_text.grid(row=4, column=0, columnspan=5, sticky='nsew', padx=8, pady=2)

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        param_frame.grid_columnconfigure(1, weight=1)
        param_frame.grid_columnconfigure(4, weight=1)

    def update_atom_inputs(self):
        for widget in self.atom_frame.winfo_children():
            widget.destroy()
        self.atom_entries.clear()
        try:
            n = int(self.num_atoms.get())
            if n < 1 or n > 10:  # limite raisonnable
                raise ValueError
        except Exception:
            messagebox.showwarning("Entrée invalide", "Le nombre d’atomes doit être un entier positif raisonnable (1-10).")
            self.num_atoms.set(3)
            n = 3

        # Noms par défaut pour les 3 premiers atomes
        default_names = ["Ti", "N", "H"]
        for i in range(n):
            tk.Label(self.atom_frame, text=f"Atome {i+1} :").grid(row=i, column=0, sticky='e')
            entry = tk.Entry(self.atom_frame)
            entry.insert(0, default_names[i] if i < 3 else "")
            entry.grid(row=i, column=1, sticky='ew')
            self.atom_entries.append(entry)
        self.atom_frame.grid_columnconfigure(1, weight=1)

    def read_data(self, filepath):
        # Retourne None, None si le fichier n'existe pas
        if not os.path.isfile(filepath):
            return None, None
        try:
            with open(filepath, encoding='latin1') as f:
                lines = f.readlines()
            start_index = None
            for i, line in enumerate(lines):
                tokens = line.strip().split()
                if len(tokens) >= 8:
                    try:
                        _ = [float(tok) for tok in tokens[:8]]
                        start_index = i
                        break
                    except ValueError:
                        continue
            if start_index is None:
                return None, None
            data_str = "".join(lines[start_index:])
            data = np.loadtxt(StringIO(data_str))
            if data.ndim == 1:
                data = np.expand_dims(data, axis=0)
            if data.shape[1] < 7:
                return None, None
            return data[:, 5], data[:, 6]
        except Exception as e:
            return None, None

    def generate_plot(self, savepath=None, silent=False):
        plt.figure(figsize=(8, 7.2))
        plt.grid(color="#C0C0C0")
        plt.yscale("log")
        plt.ylim(1e-12, 1)
        plt.xlim(0, 0.05)
        plt.xlabel("C[H]", fontsize=15, fontweight='bold')
        plt.ylabel("Concentration de défauts ponctuels", fontsize=15, fontweight='bold')
        plt.tick_params(axis='both', which='both', direction='in', top=True, right=True)
        plt.text(0.03, 0.2, self.title_text.get(), fontsize=14, fontweight='bold', ha='center')

        base = self.system_name.get()
        try:
            n_sites = int(self.num_sites.get())
        except Exception:
            n_sites = 2
        atoms = [entry.get().strip() for entry in self.atom_entries if entry.get().strip()]

        if len(atoms) < n_sites:
            messagebox.showerror("Erreur", "Le nombre d'atomes renseigné doit être au moins égal au nombre de sites.")
            plt.close()
            return

        # Génération dynamique des couleurs et styles
        import itertools
        color_list = ['blue', 'black', 'green', 'red', 'orange', 'purple', 'brown', 'cyan', 'magenta', 'grey']
        style_list = ['-', '--', '-.', ':']
        color_cycle = itertools.cycle(color_list)
        style_cycle = itertools.cycle(style_list)

        file_templates = []

        # Lacunes et substitutions
        for k in range(1, n_sites+1):
            # Vacancies
            if self.show_vacancies.get():
                file_templates.append((
                    f"{base}_L_r_{k}",
                    f"V_{{{atoms[k-1]}}}",
                    next(color_cycle), next(style_cycle)
                ))
            # Substitutions
            if self.show_substitutions.get():
                for i in range(1, n_sites+1):
                    if i != k:
                        file_templates.append((
                            f"{base}_{i}_r_{k}",
                            f"{atoms[i-1]}_{{{atoms[k-1]}}}",
                            next(color_cycle), next(style_cycle)
                        ))

        # (Optionnel) Hydrogènes
        if self.show_hydrogens.get() and len(atoms) >= 3:
            for k in range(1, n_sites+1):
                file_templates.append((
                    f"{base}_3_r_{k}",
                    f"{atoms[2]}_{{{atoms[k-1]}}}",
                    next(color_cycle), next(style_cycle)
                ))

        # Affichage des fichiers dans la prévisualisation
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        found_data = False
        missing_files = []

        for tpl in file_templates:
            fname, label, color, style = tpl
            self.preview_text.insert(tk.END, f"{fname}\n")
            x, y = self.read_data(fname)
            if x is not None and y is not None:
                found_data = True
                plt.plot(x, y, label=label, color=color, linestyle=style, linewidth=2)
            else:
                missing_files.append(fname)

        self.preview_text.config(state='disabled')

        if missing_files:
            msg = "Les fichiers suivants sont manquants ou invalides :\n" + "\n".join(missing_files)
            messagebox.showerror("Fichiers manquants", msg)
            plt.close()
            return

        if not found_data:
            if not silent:
                messagebox.showwarning("Aucun fichier", "Aucun fichier de données valide trouvé.")
            plt.close()
            return

        plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=12, frameon=True)
        plt.tight_layout()
        if savepath:
            plt.savefig(savepath, dpi=300)
            plt.close()
        else:
            plt.show()

    def save_plot_dialog(self):
        fmt = filedialog.asksaveasfilename(defaultextension=".png",
                                           filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("PDF", "*.pdf")],
                                           title="Enregistrer le graphique sous...",
                                           initialfile=self.output_basename.get())
        if fmt:
            ext = os.path.splitext(fmt)[1][1:]
            if ext in ["png", "jpg", "pdf"]:
                self.generate_plot(savepath=fmt, silent=True)
                messagebox.showinfo("Succès", f"Graphique sauvegardé sous {fmt}")
            else:
                messagebox.showerror("Erreur", "Format non supporté")

if __name__ == "__main__":
    root = tk.Tk()
    app = DefectPlotterApp(root)
    root.mainloop()
