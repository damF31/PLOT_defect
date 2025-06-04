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
        self.root.geometry("1250x780")
        self.root.minsize(1000, 600)

        # Saisie de la structure
        self.system_name = tk.StringVar(value="TiN_adpi")
        # Réseau
        self.num_network_sites = tk.IntVar(value=2)
        self.network_site_entries = []
        self.num_network_atoms = tk.IntVar(value=2)
        self.network_atom_entries = []
        # Interstitiels
        self.num_inter_sites = tk.IntVar(value=1)
        self.inter_site_entries = []
        # Atomes ajoutés
        self.num_added_atoms = tk.IntVar(value=1)
        self.added_atom_entries = []

        self.output_basename = tk.StringVar(value="conc_plot")
        self.title_text = tk.StringVar(value="Ti$_{0.51}$N$_{0.49}$")
        self.temperature = tk.StringVar(value="1000")

        self.show_vacancies = tk.BooleanVar(value=True)
        self.show_substitutions = tk.BooleanVar(value=True)
        self.show_inter_sites = tk.BooleanVar(value=True)
        self.show_network_atoms = tk.BooleanVar(value=True)
        self.show_added_atoms = tk.BooleanVar(value=True)

        self.create_widgets()

    def create_widgets(self):
        param_frame = tk.LabelFrame(self.root, text="Paramètres système", padx=8, pady=4)
        param_frame.grid(row=0, column=0, sticky='nsew', padx=8, pady=5, columnspan=14)

        tk.Label(param_frame, text="Nom du système :").grid(row=0, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.system_name).grid(row=0, column=1, sticky='ew', columnspan=2)

        # SITES ET ATOMES DU RÉSEAU
        tk.Label(param_frame, text="Nb sites réseau (avec lacunes)").grid(row=1, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.num_network_sites, width=5).grid(row=1, column=1, sticky='w')
        tk.Button(param_frame, text="Mettre à jour", command=self.update_site_atom_inputs).grid(row=1, column=2, sticky='w')
        self.network_sites_frame = tk.Frame(param_frame)
        self.network_sites_frame.grid(row=2, column=0, columnspan=3, sticky='ew')

        tk.Label(param_frame, text="Nb atomes réseau").grid(row=1, column=3, sticky='e')
        tk.Entry(param_frame, textvariable=self.num_network_atoms, width=5).grid(row=1, column=4, sticky='w')
        tk.Button(param_frame, text="Mettre à jour", command=self.update_site_atom_inputs).grid(row=1, column=5, sticky='w')
        self.network_atoms_frame = tk.Frame(param_frame)
        self.network_atoms_frame.grid(row=2, column=3, columnspan=3, sticky='ew')

        # SITES INTERSTITIELS
        tk.Label(param_frame, text="Nb sites interstitiels").grid(row=1, column=6, sticky='e')
        tk.Entry(param_frame, textvariable=self.num_inter_sites, width=5).grid(row=1, column=7, sticky='w')
        tk.Button(param_frame, text="Mettre à jour", command=self.update_site_atom_inputs).grid(row=1, column=8, sticky='w')
        self.inter_sites_frame = tk.Frame(param_frame)
        self.inter_sites_frame.grid(row=2, column=6, columnspan=3, sticky='ew')

        # ATOMES AJOUTÉS
        tk.Label(param_frame, text="Nb atomes ajoutés").grid(row=1, column=9, sticky='e')
        tk.Entry(param_frame, textvariable=self.num_added_atoms, width=5).grid(row=1, column=10, sticky='w')
        tk.Button(param_frame, text="Mettre à jour", command=self.update_site_atom_inputs).grid(row=1, column=11, sticky='w')
        self.added_atoms_frame = tk.Frame(param_frame)
        self.added_atoms_frame.grid(row=2, column=9, columnspan=3, sticky='ew')

        self.update_site_atom_inputs()

        # Titre automatique + température
        tk.Label(param_frame, text="Nom système (pour le titre) :").grid(row=3, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.title_text).grid(row=3, column=1, sticky='ew', columnspan=3)
        tk.Label(param_frame, text="Température (K) :").grid(row=3, column=4, sticky='e')
        tk.Entry(param_frame, textvariable=self.temperature, width=8).grid(row=3, column=5, sticky='w')

        tk.Label(param_frame, text="Nom du fichier de sortie :").grid(row=4, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.output_basename).grid(row=4, column=1, sticky='ew', columnspan=4)
        tk.Button(param_frame, text="Sauvegarder", command=self.save_plot_dialog).grid(row=4, column=5, sticky='w')

        # Options d'affichage avancées
        options_frame = tk.LabelFrame(self.root, text="Défauts & Objets à afficher", padx=8, pady=4)
        options_frame.grid(row=1, column=0, sticky='ew', padx=8, pady=0, columnspan=14)
        tk.Checkbutton(options_frame, text="Vacances", variable=self.show_vacancies).grid(row=0, column=0, sticky='w')
        tk.Checkbutton(options_frame, text="Substitutions", variable=self.show_substitutions).grid(row=0, column=1, sticky='w')
        tk.Checkbutton(options_frame, text="Afficher sites interstitiels", variable=self.show_inter_sites).grid(row=0, column=2, sticky='w')
        tk.Checkbutton(options_frame, text="Afficher atomes réseau", variable=self.show_network_atoms).grid(row=0, column=3, sticky='w')
        tk.Checkbutton(options_frame, text="Afficher atomes ajoutés", variable=self.show_added_atoms).grid(row=0, column=4, sticky='w')

        action_frame = tk.Frame(self.root)
        action_frame.grid(row=2, column=0, columnspan=14, pady=5)
        tk.Button(action_frame, text="Générer le graphique", command=self.generate_plot).pack(side='left', padx=10)
        tk.Button(action_frame, text="Quitter", command=self.root.quit).pack(side='left', padx=10)

        self.preview_label = tk.Label(self.root, text="Fichiers lus :")
        self.preview_label.grid(row=3, column=0, sticky='w', padx=8, pady=2, columnspan=14)
        self.preview_text = tk.Text(self.root, height=14, width=150, state='disabled', wrap='none')
        self.preview_text.grid(row=4, column=0, columnspan=14, sticky='nsew', padx=8, pady=2)

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        param_frame.grid_columnconfigure(1, weight=1)
        param_frame.grid_columnconfigure(4, weight=1)

    def update_site_atom_inputs(self):
        # Sites réseau
        for widget in self.network_sites_frame.winfo_children():
            widget.destroy()
        self.network_site_entries.clear()
        try:
            n_net_sites = int(self.num_network_sites.get())
            if n_net_sites < 1 or n_net_sites > 10:
                raise ValueError
        except Exception:
            messagebox.showwarning("Entrée invalide", "Le nombre de sites réseau doit être entre 1 et 10.")
            self.num_network_sites.set(2)
            n_net_sites = 2
        default_sites = ["Ti", "N"]
        for i in range(n_net_sites):
            tk.Label(self.network_sites_frame, text=f"Site réseau {i+1} :").grid(row=i, column=0, sticky='e')
            entry = tk.Entry(self.network_sites_frame)
            entry.insert(0, default_sites[i] if i < len(default_sites) else "")
            entry.grid(row=i, column=1, sticky='ew')
            self.network_site_entries.append(entry)
        self.network_sites_frame.grid_columnconfigure(1, weight=1)

        # Atomes réseau
        for widget in self.network_atoms_frame.winfo_children():
            widget.destroy()
        self.network_atom_entries.clear()
        try:
            n_net_atoms = int(self.num_network_atoms.get())
            if n_net_atoms < 1 or n_net_atoms > 10:
                raise ValueError
        except Exception:
            messagebox.showwarning("Entrée invalide", "Le nombre d’atomes du réseau doit être entre 1 et 10.")
            self.num_network_atoms.set(2)
            n_net_atoms = 2
        default_atoms = ["Ti", "N"]
        for i in range(n_net_atoms):
            tk.Label(self.network_atoms_frame, text=f"Atome réseau {i+1} :").grid(row=i, column=0, sticky='e')
            entry = tk.Entry(self.network_atoms_frame)
            entry.insert(0, default_atoms[i] if i < len(default_atoms) else "")
            entry.grid(row=i, column=1, sticky='ew')
            self.network_atom_entries.append(entry)
        self.network_atoms_frame.grid_columnconfigure(1, weight=1)

        # Sites interstitiels
        for widget in self.inter_sites_frame.winfo_children():
            widget.destroy()
        self.inter_site_entries.clear()
        try:
            n_inter_sites = int(self.num_inter_sites.get())
            if n_inter_sites < 0 or n_inter_sites > 10:
                raise ValueError
        except Exception:
            messagebox.showwarning("Entrée invalide", "Le nombre de sites interstitiels doit être entre 0 et 10.")
            self.num_inter_sites.set(1)
            n_inter_sites = 1
        default_inters = ["8c"]
        for i in range(n_inter_sites):
            tk.Label(self.inter_sites_frame, text=f"Site interstitiel {i+1} :").grid(row=i, column=0, sticky='e')
            entry = tk.Entry(self.inter_sites_frame)
            entry.insert(0, default_inters[i] if i < len(default_inters) else "")
            entry.grid(row=i, column=1, sticky='ew')
            self.inter_site_entries.append(entry)
        self.inter_sites_frame.grid_columnconfigure(1, weight=1)

        # Atomes ajoutés
        for widget in self.added_atoms_frame.winfo_children():
            widget.destroy()
        self.added_atom_entries.clear()
        try:
            n_add = int(self.num_added_atoms.get())
            if n_add < 0 or n_add > 10:
                raise ValueError
        except Exception:
            messagebox.showwarning("Entrée invalide", "Le nombre d’atomes ajoutés doit être entre 0 et 10.")
            self.num_added_atoms.set(1)
            n_add = 1
        default_add = ["H"]
        for i in range(n_add):
            tk.Label(self.added_atoms_frame, text=f"Atome ajouté {i+1} :").grid(row=i, column=0, sticky='e')
            entry = tk.Entry(self.added_atoms_frame)
            entry.insert(0, default_add[i] if i < len(default_add) else "")
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
        plt.figure(figsize=(13, 8))
        plt.grid(color="#C0C0C0")
        plt.yscale("log")
        plt.ylim(1e-12, 1)
        plt.xlim(0, 0.05)
        plt.xlabel("C[H]", fontsize=15, fontweight='bold')
        plt.ylabel("Concentration de défauts ponctuels", fontsize=15, fontweight='bold')
        plt.tick_params(axis='both', which='both', direction='in', top=True, right=True)

        # Titre auto
        base_title = self.title_text.get().strip() or "Ti$_{0.51}$N$_{0.49}$"
        temperature = self.temperature.get().strip()
        added_atoms_full = [e.get().strip() for e in self.added_atom_entries if e.get().strip()]
        added_atoms_str = ""
        if self.show_added_atoms.get() and added_atoms_full:
            added_atoms_str = " + " + " + ".join(added_atoms_full)
        full_title = f"{base_title}{added_atoms_str} à {temperature}K"
        plt.text(0.03, 0.2, full_title, fontsize=14, fontweight='bold', ha='center')

        base = self.system_name.get()
        network_sites = [e.get().strip() for e in self.network_site_entries if e.get().strip()]
        network_atoms_full = [e.get().strip() for e in self.network_atom_entries if e.get().strip()]
        inter_sites_full = [e.get().strip() for e in self.inter_site_entries if e.get().strip()]
        added_atoms_full = [e.get().strip() for e in self.added_atom_entries if e.get().strip()]

        # Sélection selon options d'affichage
        network_atoms = network_atoms_full if self.show_network_atoms.get() else []
        added_atoms = added_atoms_full if self.show_added_atoms.get() else []
        inter_sites = inter_sites_full if self.show_inter_sites.get() else []

        all_atoms = network_atoms + added_atoms
        all_sites = network_sites + inter_sites
        n_net_sites = len(network_sites)
        n_all_sites = len(all_sites)
        n_all_atoms = len(all_atoms)

        # Contrôle des champs
        if len(network_sites) != int(self.num_network_sites.get()) or \
           len(network_atoms_full) != int(self.num_network_atoms.get()) or \
           len(inter_sites_full) != int(self.num_inter_sites.get()) or \
           len(added_atoms_full) != int(self.num_added_atoms.get()):
            messagebox.showerror("Erreur", "Veuillez renseigner tous les noms d'atomes/sites réseau, interstitiels et ajoutés.")
            plt.close()
            return

        import itertools
        color_list = ['blue', 'black', 'green', 'red', 'orange', 'purple', 'brown', 'cyan', 'magenta', 'grey']
        style_list = ['-', '--', '-.', ':']
        color_cycle = itertools.cycle(color_list)
        style_cycle = itertools.cycle(style_list)

        file_templates = []
        # Vacancies uniquement sur sites réseau !
        if self.show_vacancies.get():
            for k in range(1, n_net_sites+1):
                file_templates.append((
                    f"{base}_L_r_{k}",
                    f"V_{{{network_sites[k-1]}}}",
                    next(color_cycle), next(style_cycle)
                ))
        # Substitutions (i != k) + i_r_i pour les atomes ajoutés sur sites interstitiels
        if self.show_substitutions.get() and n_all_sites > 0 and n_all_atoms > 0:
            # (1) _i_r_k, i != k pour tous atomes/sites sélectionnés
            for k in range(1, n_all_sites+1):
                for i in range(1, n_all_atoms+1):
                    if i != k:
                        file_templates.append((
                            f"{base}_{i}_r_{k}",
                            f"{all_atoms[i-1]}_{{{all_sites[k-1]}}}",
                            next(color_cycle), next(style_cycle)
                        ))
            # (2) _i_r_i pour chaque atome ajouté sur chaque site interstitiel affiché
            if inter_sites and added_atoms:
                for idx_site, site in enumerate(inter_sites, start=len(network_sites)+1):  # index absolu dans all_sites
                    for idx_atom, atom in enumerate(added_atoms, start=len(network_atoms)+1):  # index absolu dans all_atoms
                        file_templates.append((
                            f"{base}_{idx_atom}_r_{idx_site}",
                            f"{atom}_{{{site}}}",
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
