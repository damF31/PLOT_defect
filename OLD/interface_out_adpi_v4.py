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
        self.root.geometry("1000x600")
        self.root.minsize(850, 450)

        self.system_name = tk.StringVar(value="TiN_adpi")
        self.num_network_atoms = tk.IntVar(value=2)
        self.num_added_atoms = tk.IntVar(value=1)
        self.network_atom_entries = []
        self.added_atom_entries = []
        self.output_basename = tk.StringVar(value="conc_plot")
        self.title_text = tk.StringVar(value="Ti$_{0.51}$N$_{0.49}$")

        self.show_vacancies = tk.BooleanVar(value=True)
        self.show_substitutions = tk.BooleanVar(value=True)
        self.temperature = tk.StringVar(value="1000")

        self.create_widgets()

    def create_widgets(self):
        param_frame = tk.LabelFrame(self.root, text="Paramètres système", padx=8, pady=4)
        param_frame.grid(row=0, column=0, sticky='nsew', padx=8, pady=5, columnspan=9)

        tk.Label(param_frame, text="Température (K) :").grid(row=5, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.temperature, width=8).grid(row=5, column=1, sticky='w')
        tk.Label(param_frame, text="Nom du système :").grid(row=0, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.system_name).grid(row=0, column=1, sticky='ew', columnspan=2)

        tk.Label(param_frame, text="Atomes du réseau :").grid(row=1, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.num_network_atoms, width=5).grid(row=1, column=1, sticky='w')
        tk.Button(param_frame, text="Mettre à jour", command=self.update_atom_inputs).grid(row=1, column=2, sticky='w')
        self.network_atoms_frame = tk.Frame(param_frame)
        self.network_atoms_frame.grid(row=2, column=0, columnspan=3, sticky='ew')

        tk.Label(param_frame, text="Atomes ajoutés :").grid(row=1, column=3, sticky='e')
        tk.Entry(param_frame, textvariable=self.num_added_atoms, width=5).grid(row=1, column=4, sticky='w')
        tk.Button(param_frame, text="Mettre à jour", command=self.update_atom_inputs).grid(row=1, column=5, sticky='w')
        self.added_atoms_frame = tk.Frame(param_frame)
        self.added_atoms_frame.grid(row=2, column=3, columnspan=3, sticky='ew')

        self.update_atom_inputs()

        tk.Label(param_frame, text="Titre du graphique :").grid(row=3, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.title_text).grid(row=3, column=1, sticky='ew', columnspan=8)

        tk.Label(param_frame, text="Nom du fichier de sortie :").grid(row=4, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.output_basename).grid(row=4, column=1, sticky='ew', columnspan=4)
        tk.Button(param_frame, text="Sauvegarder", command=self.save_plot_dialog).grid(row=4, column=5, sticky='w')

        options_frame = tk.LabelFrame(self.root, text="Défauts à afficher", padx=8, pady=4)
        options_frame.grid(row=1, column=0, sticky='ew', padx=8, pady=0, columnspan=9)
        tk.Checkbutton(options_frame, text="Vacances", variable=self.show_vacancies).grid(row=0, column=0, sticky='w')
        tk.Checkbutton(options_frame, text="Substitutions", variable=self.show_substitutions).grid(row=0, column=1, sticky='w')

        action_frame = tk.Frame(self.root)
        action_frame.grid(row=2, column=0, columnspan=9, pady=5)
        tk.Button(action_frame, text="Générer le graphique", command=self.generate_plot).pack(side='left', padx=10)
        tk.Button(action_frame, text="Quitter", command=self.root.quit).pack(side='left', padx=10)

        self.preview_label = tk.Label(self.root, text="Fichiers lus :")
        self.preview_label.grid(row=3, column=0, sticky='w', padx=8, pady=2, columnspan=9)

        self.preview_text = tk.Text(self.root, height=10, width=120, state='disabled', wrap='none')
        self.preview_text.grid(row=4, column=0, columnspan=9, sticky='nsew', padx=8, pady=2)

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        param_frame.grid_columnconfigure(1, weight=1)
        param_frame.grid_columnconfigure(4, weight=1)

    def update_atom_inputs(self):
        # Réseau
        for widget in self.network_atoms_frame.winfo_children():
            widget.destroy()
        self.network_atom_entries.clear()
        try:
            n_net = int(self.num_network_atoms.get())
            if n_net < 1 or n_net > 10:
                raise ValueError
        except Exception:
            messagebox.showwarning("Entrée invalide", "Le nombre d’atomes du réseau doit être un entier positif raisonnable (1-10).")
            self.num_network_atoms.set(2)
            n_net = 2
        default_names = ["Ti", "N"]
        for i in range(n_net):
            tk.Label(self.network_atoms_frame, text=f"Atome réseau {i+1} :").grid(row=i, column=0, sticky='e')
            entry = tk.Entry(self.network_atoms_frame)
            entry.insert(0, default_names[i] if i < 2 else "")
            entry.grid(row=i, column=1, sticky='ew')
            self.network_atom_entries.append(entry)
        self.network_atoms_frame.grid_columnconfigure(1, weight=1)
        # Ajoutés
        for widget in self.added_atoms_frame.winfo_children():
            widget.destroy()
        self.added_atom_entries.clear()
        try:
            n_add = int(self.num_added_atoms.get())
            if n_add < 0 or n_add > 10:
                raise ValueError
        except Exception:
            messagebox.showwarning("Entrée invalide", "Le nombre d’atomes ajoutés doit être un entier positif raisonnable (0-10).")
            self.num_added_atoms.set(1)
            n_add = 1
        default_add = ["H"]
        for i in range(n_add):
            tk.Label(self.added_atoms_frame, text=f"Ajouté {i+1} :").grid(row=i, column=0, sticky='e')
            entry = tk.Entry(self.added_atoms_frame)
            entry.insert(0, default_add[i] if i < 1 else "")
            entry.grid(row=i, column=1, sticky='ew')
            self.added_atom_entries.append(entry)
        self.added_atoms_frame.grid_columnconfigure(1, weight=1)

    def read_data(self, filepath):
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
        # Récupère le nom, la température et les atomes ajoutés
        base_title = self.title_text.get().strip() or "Ti$_{0.51}$N$_{0.49}$"
        temperature = self.temperature.get().strip()
        added_atoms = [e.get().strip() for e in self.added_atom_entries if e.get().strip()]
        added_atoms_str = ""
        if added_atoms:
            added_atoms_str = " + " + " + ".join(added_atoms)
        # Construction du titre
        full_title = f"{base_title}{added_atoms_str} à {temperature}K"

        plt.figure(figsize=(10, 7.2))
        plt.grid(color="#C0C0C0")
        plt.yscale("log")
        plt.ylim(1e-12, 1)
        plt.xlim(0, 0.05)
        plt.xlabel("C[H]", fontsize=15, fontweight='bold')
        plt.ylabel("Concentration de défauts ponctuels", fontsize=15, fontweight='bold')
        plt.tick_params(axis='both', which='both', direction='in', top=True, right=True)
        plt.text(0.03, 0.2, full_title, fontsize=14, fontweight='bold', ha='center')

        base = self.system_name.get()
        n_net = int(self.num_network_atoms.get())
        n_add = int(self.num_added_atoms.get())
        network_atoms = [e.get().strip() for e in self.network_atom_entries if e.get().strip()]
        added_atoms = [e.get().strip() for e in self.added_atom_entries if e.get().strip()]

        if len(network_atoms) < n_net or len(added_atoms) < n_add:
            messagebox.showerror("Erreur", "Veuillez renseigner tous les noms d'atomes réseau et ajoutés.")
            plt.close()
            return

        all_atoms = network_atoms + added_atoms
        n_total = len(all_atoms)

        import itertools
        color_list = ['blue', 'black', 'green', 'red', 'orange', 'purple', 'brown', 'cyan', 'magenta', 'grey']
        style_list = ['-', '--', '-.', ':']
        color_cycle = itertools.cycle(color_list)
        style_cycle = itertools.cycle(style_list)

        file_templates = []

        # Vacancies uniquement pour les atomes du réseau
        if self.show_vacancies.get():
            for k in range(1, n_net+1):
                file_templates.append((
                    f"{base}_L_r_{k}",
                    f"V_{{{network_atoms[k-1]}}}",
                    next(color_cycle), next(style_cycle)
                ))
        # Substitutions pour tous les atomes/sites, i != k
        if self.show_substitutions.get():
            for k in range(1, n_total+1):
                for i in range(1, n_total+1):
                    if i != k:
                        file_templates.append((
                            f"{base}_{i}_r_{k}",
                            f"{all_atoms[i-1]}_{{{all_atoms[k-1]}}}",
                            next(color_cycle), next(style_cycle)
                        ))

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
