"""
Affichage et sauvegarde du graphique matplotlib.

Responsabilités principales :
- Récupère la liste des fichiers, labels et données depuis defect_logic et data_loader.
- Affiche la figure, la met en forme, affiche la légende et gère la sauvegarde.
- Gère la traduction dynamique pour les messages d'erreur/infos.
- Prend en compte les bornes et échelles des axes configurées par l'utilisateur.
- Trace uniquement les atomes/sites sélectionnés (via defect_logic).
- Permet de tracer la concentration selon n'importe quel mu_atX ou x_atX choisi par l'utilisateur.
"""

import matplotlib.pyplot as plt
from data_loader import read_data, check_files_exist, get_n_species, get_colnames
import config
import os

class Plotter:
    def __init__(self, app):
        """
        Initialise le plotter avec une référence à l'application principale (app).
        """
        self.app = app
        self.debug = False  # Mettre à True pour activer les prints de debug

    def get_plot_limits_and_scales(self, xaxis_type='x'):
        """
        Récupère et vérifie les bornes et échelles des axes depuis l'UI utilisateur.

        xaxis_type : str
            'x' pour tracer en fonction de x_*, 'mu' pour mu_*
        Retour :
            xmin, xmax, ymin, ymax, xscale, yscale : valeurs prêtes à passer à matplotlib
        """
        def safe_float(val, default):
            try:
                return float(val)
            except Exception:
                return default
        # Gestion des bornes X selon le type d’axe
        if xaxis_type == 'mu':
            xmin = safe_float(self.app.xmin.get(), -11)
            xmax = safe_float(self.app.xmax.get(), 0)
            xscale = "linear"
        else:
            xmin = safe_float(self.app.xmin.get(), 0)
            xmax = safe_float(self.app.xmax.get(), 0.05)
            xscale = self.app.xscale.get() if self.app.xscale.get() in ("linear", "log") else "linear"
        ymin = safe_float(self.app.ymin.get(), 1e-12)
        ymax = safe_float(self.app.ymax.get(), 1)
        yscale = self.app.yscale.get() if self.app.yscale.get() in ("linear", "log") else "log"
        return xmin, xmax, ymin, ymax, xscale, yscale

    def get_xcol_ycol(self, fname):
        """
        Retourne les indices de colonnes sélectionnées via l'interface utilisateur.

        fname : str
            Chemin du fichier de données (utilisé ici pour retrouver la liste des colonnes)
        Retour :
            x_col, y_col : indices numériques des colonnes à tracer
            x_label : label de l'abscisse
            all_colnames : liste de tous les labels possibles (dans l'ordre du fichier)
        Exception :
            ValueError si les labels sélectionnés ne correspondent à aucune colonne connue
        """
        x_label = self.app.xaxis_choice_var.get()
        y_label = self.app.yaxis_choice_var.get()
        all_colnames = self.app.all_colnames  # Liste des noms de colonnes (UI)
        if x_label not in all_colnames or y_label not in all_colnames:
            raise ValueError(f"Colonne inconnue: {x_label} ou {y_label}. Vérifiez les atomes définis.")
        x_col = all_colnames.index(x_label)
        y_col = all_colnames.index(y_label)
        return x_col, y_col, x_label, all_colnames

    def generate_plot(self):
        """
        Gère l'affichage interactif du graphique :
        - Récupère la liste de fichiers/labels à tracer
        - Récupère le choix utilisateur pour les axes
        - Lit les données (x, y) à tracer pour chaque courbe
        - Met en forme la figure, affiche la légende, gère les erreurs et l'aperçu
        """
        logic = self.app.logic
        file_labels = logic.generate_file_list_and_labels()
        premier_fichier = file_labels[0][0] if file_labels else None
        if premier_fichier:
            # Met à jour dynamiquement la liste des axes si besoin
            self.app.update_axis_choices(premier_fichier)

        colors = iter(config.COLORS * 20)
        styles = iter(config.STYLES * 50)

        plt.figure(figsize=(13, 8))
        plt.grid(color="#C0C0C0")

        # Détermine la nature de l'abscisse pour le scaling
        ref_fname = file_labels[0][0] if file_labels else None
        x_col, y_col, xaxis_type, all_names = self.get_xcol_ycol(ref_fname)

        xmin, xmax, ymin, ymax, xscale, yscale = self.get_plot_limits_and_scales(xaxis_type)
        plt.xscale(xscale)
        plt.yscale(yscale)
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)

        # Labels axes
        absc_label = self.app.xaxis_choice.get()
        if absc_label.startswith("x_"):
            at_name = absc_label[2:]
            xlabel = f"Fraction {at_name}" if self.app.language == "fr" else f"Fraction {at_name}"
        elif absc_label.startswith("mu_"):
            at_name = absc_label[3:]
            xlabel = fr"$\mu_{{{at_name}}}$ (eV)"
        else:
            xlabel = absc_label
        plt.xlabel(xlabel, fontsize=15, fontweight='bold')
        plt.ylabel(self.app.tr('ylabel_defects'), fontsize=15, fontweight='bold')
        plt.tick_params(axis='both', which='both', direction='in', top=True, right=True)

        # Titre automatique
        base_title = self.app.title_text.get().strip() or config.DEFAULT_TITLE
        temperature = self.app.temperature.get().strip()
        added_atoms = [e.get().strip() for e in self.app.added_atom_entries if e.get().strip()]
        added_atoms_str = ""
        if self.app.show_added_atoms.get() and added_atoms:
            added_atoms_str = " + " + " + ".join(added_atoms)
        full_title = f"{base_title}{added_atoms_str} à {temperature}K" if self.app.language == "fr" else f"{base_title}{added_atoms_str} at {temperature}K"
        plt.text(0.03, 0.2, full_title, fontsize=14, fontweight='bold', ha='center')

        # Aperçu des fichiers lus dans la fenêtre application
        self.app.preview_text.config(state='normal')
        self.app.preview_text.delete(1.0, 'end')
        found_data = False
        missing_files = []

        print("[DEBUG] file_labels dans plotter =", file_labels)
        for fname, label in file_labels:
            if self.debug:
                print(f"[DEBUG] Cherche fichier: {fname}")
                print(f"[DEBUG] Présent ? {os.path.exists(fname)}")
                try:
                    with open(fname, 'r', encoding='latin1') as f:
                        lines = f.readlines()
                    print(f"[DEBUG] {fname} : {len(lines)} lignes")
                    print(f"[DEBUG] Premières lignes : {lines[:6]}")
                except Exception as e:
                    print(f"[DEBUG] Erreur lecture {fname} : {e}")
            self.app.preview_text.insert('end', f"{fname}\n")
            x, y = read_data(fname, x_col=x_col, y_col=y_col)
            color = next(colors)
            style = next(styles)
            if x is not None and y is not None and len(x) > 0 and len(y) > 0:
                found_data = True
                plt.plot(x, y, label=label, color=color, linestyle=style, linewidth=2)
            else:
                missing_files.append(fname)

        self.app.preview_text.config(state='disabled')

        # Gestion des fichiers manquants
        if missing_files:
            import tkinter.messagebox as mb
            msg = self.app.tr('missing_files') + "\n" + "\n".join(missing_files)
            mb.showerror(self.app.tr('missing_files_title'), msg)
            plt.close()
            return

        # Gestion du cas où aucune donnée n'a pu être tracée
        if not found_data:
            import tkinter.messagebox as mb
            mb.showwarning(self.app.tr('no_file_title'), self.app.tr('no_file'))
            plt.close()
            return

        if self.debug: 
            print("[DEBUG] file_labels =", file_labels)
            for fname, label in file_labels:
                print(f"[DEBUG] Fichier {fname} avec label {label}")
        plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=12, frameon=True)
        plt.tight_layout()
        plt.show()

    def save_plot_dialog(self):
        """
        Boîte de dialogue pour sauvegarder le plot affiché (PNG, JPG, PDF).
        Affiche un message de confirmation ou d’erreur selon le succès.
        """
        from tkinter import filedialog, messagebox
        fmt = filedialog.asksaveasfilename(defaultextension=".png",
                                           filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("PDF", "*.pdf")],
                                           title=self.app.tr('save_dialog_title'),
                                           initialfile=self.app.output_basename.get())
        if fmt:
            ext = fmt.split('.')[-1]
            if ext in ["png", "jpg", "pdf"]:
                self._save_plot(fmt)
                messagebox.showinfo(self.app.tr('save_success_title'), f"{self.app.tr('save_success_msg')} {fmt}")
            else:
                messagebox.showerror(self.app.tr('error_title'), self.app.tr('unsupported_format'))

    def _save_plot(self, savepath):
        """
        Génère le plot et le sauvegarde à l'emplacement désigné.
        (quasiment identique à generate_plot mais sans interaction UI)
        """
        logic = self.app.logic
        file_labels = logic.generate_file_list_and_labels()
        colors = iter(config.COLORS * 20)
        styles = iter(config.STYLES * 50)

        plt.figure(figsize=(13, 8))
        plt.grid(color="#C0C0C0")

        ref_fname = file_labels[0][0] if file_labels else None
        x_col, y_col, xaxis_type, all_names = self.get_xcol_ycol(ref_fname) if ref_fname else (0, 0, 'x', [])

        xmin, xmax, ymin, ymax, xscale, yscale = self.get_plot_limits_and_scales(xaxis_type)
        plt.xscale(xscale)
        plt.yscale(yscale)
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)

        absc_label = self.app.xaxis_choice.get()
        if absc_label.startswith("x_"):
            at_name = absc_label[2:]
            xlabel = f"Fraction {at_name}" if self.app.language == "fr" else f"Fraction {at_name}"
        elif absc_label.startswith("mu_"):
            at_name = absc_label[3:]
            xlabel = fr"$\mu_{{{at_name}}}$ (eV)"
        else:
            xlabel = absc_label
        plt.xlabel(xlabel, fontsize=15, fontweight='bold')
        plt.ylabel(self.app.tr('ylabel_defects'), fontsize=15, fontweight='bold')
        plt.tick_params(axis='both', which='both', direction='in', top=True, right=True)

        base_title = self.app.title_text.get().strip() or config.DEFAULT_TITLE
        temperature = self.app.temperature.get().strip()
        added_atoms = [e.get().strip() for e in self.app.added_atom_entries if e.get().strip()]
        added_atoms_str = ""
        if self.app.show_added_atoms.get() and added_atoms:
            added_atoms_str = " + " + " + ".join(added_atoms)
        full_title = f"{base_title}{added_atoms_str} à {temperature}K" if self.app.language == "fr" else f"{base_title}{added_atoms_str} at {temperature}K"
        plt.text(0.03, 0.2, full_title, fontsize=14, fontweight='bold', ha='center')

        found_data = False
        for fname, label in file_labels:
            x, y = read_data(fname, x_col=x_col, y_col=y_col)
            color = next(colors)
            style = next(styles)
            if x is not None and y is not None and len(x) > 0 and len(y) > 0:
                found_data = True
                plt.plot(x, y, label=label, color=color, linestyle=style, linewidth=2)
        if not found_data:
            plt.close()
            return
        plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=12, frameon=True)
        plt.tight_layout()
        plt.savefig(savepath, dpi=300)
        plt.close()
