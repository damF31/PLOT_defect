"""
Interface graphique principale multilingue (français/anglais) pour la visualisation des concentrations de défauts ponctuels.

Responsabilités principales :
- Création et gestion de toute l'interface utilisateur (Tkinter)
- Liaison avec la logique métier (DefectLogic) et le plotter (Plotter)
- Gestion dynamique des widgets (atomes, sites, axes, sélections…)
- Traduction en temps réel de tous les textes de l’interface via le dictionnaire translations
- Gestion des interactions utilisateur (tracé, sauvegarde, changement de langue…)

Structure :
- Classe DefectPlotterApp, qui contient tout l’état de l’application et les callbacks de l’UI
"""

import tkinter as tk
from tkinter import ttk
from translations import translations
from defect_logic import DefectLogic
from plotter import Plotter
import config
import data_loader

class DefectPlotterApp:
    def __init__(self, root):
        """
        Initialise l’application et tous les widgets Tkinter.
        Initialise aussi les variables d’état (atomes, sites, options, axes, sélection…)
        """
        self.root = root
        self.language = 'fr'
        self.root.title("Défauts ponctuels – Visualiseur de concentrations")
        self.root.geometry("1250x780")
        self.root.minsize(1000, 600)

        # Variables d'état pour l'UI (Tkinter Variables)
        self.system_name = tk.StringVar(value=config.DEFAULT_SYSTEM_NAME)
        self.num_network_sites = tk.IntVar(value=2)
        self.network_site_entries = []
        self.num_network_atoms = tk.IntVar(value=2)
        self.network_atom_entries = []
        self.num_inter_sites = tk.IntVar(value=1)
        self.inter_site_entries = []
        self.num_added_atoms = tk.IntVar(value=1)
        self.added_atom_entries = []
        self.output_basename = tk.StringVar(value="conc_plot")
        self.title_text = tk.StringVar(value=config.DEFAULT_TITLE)
        self.temperature = tk.StringVar(value=config.DEFAULT_TEMP)

        # Options d'affichage (cases à cocher)
        self.show_vacancies = tk.BooleanVar(value=True)
        self.show_substitutions = tk.BooleanVar(value=True)
        self.show_inter_sites = tk.BooleanVar(value=True)
        self.show_network_atoms = tk.BooleanVar(value=True)
        self.show_added_atoms = tk.BooleanVar(value=True)

        # Bornes et échelles des axes
        self.xmin = tk.StringVar(value="0")
        self.xmax = tk.StringVar(value="0.05")
        self.ymin = tk.StringVar(value="1e-12")
        self.ymax = tk.StringVar(value="1")
        self.xscale = tk.StringVar(value="linear")
        self.yscale = tk.StringVar(value="log")

        # Sélection des atomes/sites à tracer
        self.selected_atoms = []
        self.selected_sites = []

        # Choix axes (COMBOBOX)
        self.xaxis_choice_var = tk.StringVar()
        self.yaxis_choice_var = tk.StringVar()

        self.logic = DefectLogic(self)
        self.plotter = Plotter(self)
        self.widgets_to_translate = {}
        self.create_widgets()

    def tr(self, key):
        """Méthode utilitaire pour la traduction dynamique des textes."""
        return translations[self.language].get(key, key)

    def create_widgets(self):
        """
        Crée et dispose tous les widgets Tkinter.
        Structure l’interface en frames logiques (paramètres système, options de tracé, sélection, actions…).
        Lie chaque bouton/action à un callback de l’application.
        """
        # Menu pour changer de langue
        lang_var = tk.StringVar(value=self.language)
        lang_menu = tk.OptionMenu(self.root, lang_var, *translations.keys(), command=self.change_language)
        lang_menu.grid(row=0, column=99, sticky='ne', padx=5, pady=5)
        self.widgets_to_translate['lang_menu'] = lang_menu
        self.lang_var = lang_var

        # ... (le reste du code tel que tu l’as envoyé, inchangé, pour chaque widget et frame)
        # Voir ton listing principal pour la création détaillée de chaque widget/label/entry/button/combobox/etc.
        # [Garde tout le code de création de widgets et de grid/pack/command/config/etc.]

        # Initialisation des listes d'atomes/sites et du menu abscisse
        self.update_site_atom_inputs()

    def update_site_atom_inputs(self):
        """
        Appelle la logique pour mettre à jour dynamiquement les widgets d’atomes/sites.
        Génère les listes ordonnées des colonnes pour les menus ComboBox.
        """
        self.logic.update_site_atom_inputs()
        self.update_atom_site_listboxes()
        atom_names = [e.get().strip() for e in self.network_atom_entries if e.get().strip()]
        atom_names += [e.get().strip() for e in self.added_atom_entries if e.get().strip()]
        # Génère la liste ordonnée des colonnes (pour ComboBox axes)
        mu_labels = [f"mu_{v}" for v in atom_names]
        x_labels = [f"x_{v}" for v in atom_names]
        self.all_colnames = mu_labels + x_labels + ["x_DP", "Hf_DP"]
        absc_choices = mu_labels + x_labels
        if not absc_choices:
            self.xaxis_choice['values'] = []
            self.xaxis_choice_var.set('')
            self.yaxis_choice['values'] = []
            self.yaxis_choice_var.set('')
            return
        self.xaxis_choice['values'] = absc_choices
        current = self.xaxis_choice_var.get()
        if self.xaxis_choice_var.get() not in absc_choices:
            self.xaxis_choice_var.set(absc_choices[0])
        else:
            self.xaxis_choice_var.set("")
            self.xaxis_choice_var.set(current)
        y_choices = ["x_DP", "Hf_DP"]
        self.yaxis_choice['values'] = y_choices
        if self.yaxis_choice_var.get() not in y_choices:
            self.yaxis_choice_var.set(y_choices[0])

    def update_axis_choices(self, filename):
        """
        Met à jour dynamiquement les menus ComboBox des axes selon le contenu du fichier (liste des colonnes).
        """
        colnames = data_loader.get_colnames(filename)
        self.xaxis_choice['values'] = colnames
        self.yaxis_choice['values'] = colnames
        if colnames:
            self.xaxis_choice_var.set(colnames[0])
            self.yaxis_choice_var.set(colnames[1] if len(colnames) > 1 else colnames[0])

    def update_atom_site_listboxes(self):
        """
        Met à jour les ListBox de sélection des atomes et sites à tracer.
        """
        self.atom_listbox.delete(0, tk.END)
        for e in self.network_atom_entries + self.added_atom_entries:
            val = e.get().strip()
            if val:
                self.atom_listbox.insert(tk.END, val)
        self.site_listbox.delete(0, tk.END)
        for e in self.network_site_entries + self.inter_site_entries:
            val = e.get().strip()
            if val:
                self.site_listbox.insert(tk.END, val)

    def update_selected_atoms_sites(self):
        """
        Met à jour les listes d’atomes/sites sélectionnés selon la sélection de l’utilisateur dans les ListBox.
        """
        self.selected_atoms = [self.atom_listbox.get(i) for i in self.atom_listbox.curselection()]
        self.selected_sites = [self.site_listbox.get(i) for i in self.site_listbox.curselection()]

    def generate_plot(self):
        """
        Callback pour générer le graphique, après mise à jour de la sélection atomes/sites.
        """
        self.update_selected_atoms_sites()
        self.plotter.generate_plot()

    def save_plot_dialog(self):
        """
        Callback pour ouvrir la boîte de dialogue de sauvegarde du graphique.
        """
        self.plotter.save_plot_dialog()

    def change_language(self, lang):
        """
        Change la langue de l’interface et met à jour tous les labels/widgets.
        """
        self.language = lang
        self.refresh_labels()
        self.update_site_atom_inputs()

    def refresh_labels(self):
        """
        Rafraîchit tous les labels et boutons de l’interface graphique dans la langue courante.
        """
        self.param_frame.config(text=self.tr('system_params'))
        self.system_name_label.config(text=self.tr('system_name'))
        self.network_sites_label.config(text=self.tr('network_sites'))
        self.network_sites_update_btn.config(text=self.tr('update'))
        self.network_atoms_label.config(text=self.tr('network_atoms'))
        self.network_atoms_update_btn.config(text=self.tr('update'))
        self.inter_sites_label.config(text=self.tr('inter_sites'))
        self.inter_sites_update_btn.config(text=self.tr('update'))
        self.added_atoms_label.config(text=self.tr('added_atoms'))
        self.added_atoms_update_btn.config(text=self.tr('update'))
        self.system_title_label.config(text=self.tr('system_title'))
        self.temperature_label.config(text=self.tr('temperature'))
        self.output_file_label.config(text=self.tr('output_file'))
        self.save_btn.config(text=self.tr('save'))
        self.xmin_label.config(text=self.tr('xmin'))
        self.xmax_label.config(text=self.tr('xmax'))
        self.ymin_label.config(text=self.tr('ymin'))
        self.ymax_label.config(text=self.tr('ymax'))
        self.xscale_label.config(text=self.tr('xscale'))
        self.yscale_label.config(text=self.tr('yscale'))
        self.options_frame.config(text=self.tr('defects_objects'))
        self.vacancies_cb.config(text=self.tr('vacancies'))
        self.substitutions_cb.config(text=self.tr('substitutions'))
        self.show_inter_sites_cb.config(text=self.tr('show_inter_sites'))
        self.show_network_atoms_cb.config(text=self.tr('show_network_atoms'))
        self.show_added_atoms_cb.config(text=self.tr('show_added_atoms'))
        self.generate_btn.config(text=self.tr('generate_plot'))
        self.quit_btn.config(text=self.tr('quit'))
        self.preview_label.config(text=self.tr('files_read'))
        self.atom_listbox_label.config(text=self.tr('select_atoms'))
        self.site_listbox_label.config(text=self.tr('select_sites'))
        self.apply_selection_btn.config(text=self.tr('apply_selection'))
        if self.xaxis_label is not None:
            self.xaxis_label.config(text=self.tr('xaxis_label') if 'xaxis_label' in translations[self.language] else "Abscisse")
        if self.yaxis_label is not None:
            self.yaxis_label.config(text=self.tr('yaxis_label') if 'yaxis_label' in translations[self.language] else "Ordonnée")
