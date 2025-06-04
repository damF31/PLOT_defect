"""
Interface graphique principale multilingue (français/anglais).
- Définit la classe DefectPlotterApp, qui organise tous les widgets et l'interface Tkinter.
- Gère les interactions utilisateur (saisie, boutons, options d'affichage, menu de langue).
- Délègue la logique métier à defect_logic, l'affichage à plotter.
- Préserve les paramètres lors du changement de langue.
- Permet de choisir dynamiquement l'abscisse de tracé (mu_atX ou x_atX d'après la liste d'atomes fournie).
"""

import tkinter as tk
from translations import translations
from defect_logic import DefectLogic
from plotter import Plotter
import config
import data_loader  # <-- Ajouté pour get_colnames

class DefectPlotterApp:
    def __init__(self, root):
        self.root = root
        self.language = 'fr'
        self.root.title("Défauts ponctuels – Visualiseur de concentrations")
        self.root.geometry("1250x780")
        self.root.minsize(1000, 600)

        # Variables d'état pour l'UI
        self.system_name = tk.StringVar(value=config.DEFAULT_SYSTEM_NAME)
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
        self.title_text = tk.StringVar(value=config.DEFAULT_TITLE)
        self.temperature = tk.StringVar(value=config.DEFAULT_TEMP)

        # Options d'affichage
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

        # Choix de l'abscisse pour le tracé
        self.xaxis_choice = tk.StringVar()      # ex: "x_Ti", "mu_H"
        self.xaxis_menu = None                  # widget OptionMenu dynamiquement créé
        self.xaxis_label = None                 # label pour l'abscisse

        self.logic = DefectLogic(self)
        self.plotter = Plotter(self)

        # Pour garder des références à tous les labels/boutons à traduire
        self.widgets_to_translate = {}

        self.create_widgets()

    def tr(self, key):
        """Méthode de traduction"""
        return translations[self.language].get(key, key)

    def create_widgets(self):
        # Menu pour changer de langue
        lang_var = tk.StringVar(value=self.language)
        lang_menu = tk.OptionMenu(self.root, lang_var, *translations.keys(), command=self.change_language)
        lang_menu.grid(row=0, column=99, sticky='ne', padx=5, pady=5)
        self.widgets_to_translate['lang_menu'] = lang_menu
        self.lang_var = lang_var

        # Cadre des paramètres système
        self.param_frame = tk.LabelFrame(self.root, text=self.tr('system_params'), padx=8, pady=4)
        self.param_frame.grid(row=0, column=0, sticky='nsew', padx=8, pady=5, columnspan=14)
        self.widgets_to_translate['param_frame'] = self.param_frame

        # Nom du système
        self.system_name_label = tk.Label(self.param_frame, text=self.tr('system_name'))
        self.system_name_label.grid(row=0, column=0, sticky='e')
        self.widgets_to_translate['system_name_label'] = self.system_name_label
        tk.Entry(self.param_frame, textvariable=self.system_name).grid(row=0, column=1, sticky='ew', columnspan=2)

        # SITES ET ATOMES DU RÉSEAU (inchangé)
        self.network_sites_label = tk.Label(self.param_frame, text=self.tr('network_sites'))
        self.network_sites_label.grid(row=1, column=0, sticky='e')
        self.widgets_to_translate['network_sites_label'] = self.network_sites_label
        tk.Entry(self.param_frame, textvariable=self.num_network_sites, width=5).grid(row=1, column=1, sticky='w')
        self.network_sites_update_btn = tk.Button(self.param_frame, text=self.tr('update'), command=self.update_site_atom_inputs)
        self.network_sites_update_btn.grid(row=1, column=2, sticky='w')
        self.widgets_to_translate['network_sites_update_btn'] = self.network_sites_update_btn
        self.network_sites_frame = tk.Frame(self.param_frame)
        self.network_sites_frame.grid(row=2, column=0, columnspan=3, sticky='ew')

        self.network_atoms_label = tk.Label(self.param_frame, text=self.tr('network_atoms'))
        self.network_atoms_label.grid(row=1, column=3, sticky='e')
        self.widgets_to_translate['network_atoms_label'] = self.network_atoms_label
        tk.Entry(self.param_frame, textvariable=self.num_network_atoms, width=5).grid(row=1, column=4, sticky='w')
        self.network_atoms_update_btn = tk.Button(self.param_frame, text=self.tr('update'), command=self.update_site_atom_inputs)
        self.network_atoms_update_btn.grid(row=1, column=5, sticky='w')
        self.widgets_to_translate['network_atoms_update_btn'] = self.network_atoms_update_btn
        self.network_atoms_frame = tk.Frame(self.param_frame)
        self.network_atoms_frame.grid(row=2, column=3, columnspan=3, sticky='ew')

        self.inter_sites_label = tk.Label(self.param_frame, text=self.tr('inter_sites'))
        self.inter_sites_label.grid(row=1, column=6, sticky='e')
        self.widgets_to_translate['inter_sites_label'] = self.inter_sites_label
        tk.Entry(self.param_frame, textvariable=self.num_inter_sites, width=5).grid(row=1, column=7, sticky='w')
        self.inter_sites_update_btn = tk.Button(self.param_frame, text=self.tr('update'), command=self.update_site_atom_inputs)
        self.inter_sites_update_btn.grid(row=1, column=8, sticky='w')
        self.widgets_to_translate['inter_sites_update_btn'] = self.inter_sites_update_btn
        self.inter_sites_frame = tk.Frame(self.param_frame)
        self.inter_sites_frame.grid(row=2, column=6, columnspan=3, sticky='ew')

        self.added_atoms_label = tk.Label(self.param_frame, text=self.tr('added_atoms'))
        self.added_atoms_label.grid(row=1, column=9, sticky='e')
        self.widgets_to_translate['added_atoms_label'] = self.added_atoms_label
        tk.Entry(self.param_frame, textvariable=self.num_added_atoms, width=5).grid(row=1, column=10, sticky='w')
        self.added_atoms_update_btn = tk.Button(self.param_frame, text=self.tr('update'), command=self.update_site_atom_inputs)
        self.added_atoms_update_btn.grid(row=1, column=11, sticky='w')
        self.widgets_to_translate['added_atoms_update_btn'] = self.added_atoms_update_btn
        self.added_atoms_frame = tk.Frame(self.param_frame)
        self.added_atoms_frame.grid(row=2, column=9, columnspan=3, sticky='ew')

        # Après la création des frames ci-dessus (pour que les entries existent)
        self.system_title_label = tk.Label(self.param_frame, text=self.tr('system_title'))
        self.system_title_label.grid(row=3, column=0, sticky='e')
        self.widgets_to_translate['system_title_label'] = self.system_title_label
        tk.Entry(self.param_frame, textvariable=self.title_text).grid(row=3, column=1, sticky='ew', columnspan=3)
        self.temperature_label = tk.Label(self.param_frame, text=self.tr('temperature'))
        self.temperature_label.grid(row=3, column=4, sticky='e')
        self.widgets_to_translate['temperature_label'] = self.temperature_label
        tk.Entry(self.param_frame, textvariable=self.temperature, width=8).grid(row=3, column=5, sticky='w')

        self.output_file_label = tk.Label(self.param_frame, text=self.tr('output_file'))
        self.output_file_label.grid(row=4, column=0, sticky='e')
        self.widgets_to_translate['output_file_label'] = self.output_file_label
        tk.Entry(self.param_frame, textvariable=self.output_basename).grid(row=4, column=1, sticky='ew', columnspan=4)
        self.save_btn = tk.Button(self.param_frame, text=self.tr('save'), command=self.save_plot_dialog)
        self.save_btn.grid(row=4, column=5, sticky='w')
        self.widgets_to_translate['save_btn'] = self.save_btn

        # Paramètres de tracé (axes)
        self.xmin_label = tk.Label(self.param_frame, text=self.tr('xmin'))
        self.xmin_label.grid(row=5, column=0, sticky='e')
        self.widgets_to_translate['xmin_label'] = self.xmin_label
        tk.Entry(self.param_frame, textvariable=self.xmin, width=8).grid(row=5, column=1, sticky='w')
        self.xmax_label = tk.Label(self.param_frame, text=self.tr('xmax'))
        self.xmax_label.grid(row=5, column=2, sticky='e')
        self.widgets_to_translate['xmax_label'] = self.xmax_label
        tk.Entry(self.param_frame, textvariable=self.xmax, width=8).grid(row=5, column=3, sticky='w')
        self.ymin_label = tk.Label(self.param_frame, text=self.tr('ymin'))
        self.ymin_label.grid(row=5, column=4, sticky='e')
        self.widgets_to_translate['ymin_label'] = self.ymin_label
        tk.Entry(self.param_frame, textvariable=self.ymin, width=8).grid(row=5, column=5, sticky='w')
        self.ymax_label = tk.Label(self.param_frame, text=self.tr('ymax'))
        self.ymax_label.grid(row=5, column=6, sticky='e')
        self.widgets_to_translate['ymax_label'] = self.ymax_label
        tk.Entry(self.param_frame, textvariable=self.ymax, width=8).grid(row=5, column=7, sticky='w')

        self.xscale_label = tk.Label(self.param_frame, text=self.tr('xscale'))
        self.xscale_label.grid(row=5, column=8, sticky='e')
        self.widgets_to_translate['xscale_label'] = self.xscale_label
        self.xscale_menu = tk.OptionMenu(self.param_frame, self.xscale, "linear", "log")
        self.xscale_menu.grid(row=5, column=9, sticky='w')
        self.widgets_to_translate['xscale_menu'] = self.xscale_menu
        self.yscale_label = tk.Label(self.param_frame, text=self.tr('yscale'))
        self.yscale_label.grid(row=5, column=10, sticky='e')
        self.widgets_to_translate['yscale_label'] = self.yscale_label
        self.yscale_menu = tk.OptionMenu(self.param_frame, self.yscale, "linear", "log")
        self.yscale_menu.grid(row=5, column=11, sticky='w')
        self.widgets_to_translate['yscale_menu'] = self.yscale_menu

        # ---------- NOUVEAU : Sélection dynamique de l'abscisse ----------
        self.xaxis_label = tk.Label(self.param_frame, text="Abscisse")  # sera traduit dans refresh_labels
        self.xaxis_label.grid(row=6, column=0, sticky="e")
        self.xaxis_menu = tk.OptionMenu(self.param_frame, self.xaxis_choice, "")  # init vide
        self.xaxis_menu.grid(row=6, column=1, sticky="ew", columnspan=3)
        self.update_xaxis_menu()
        # ---------------------------------------------------------------

        # Options d'affichage avancées (inchangé)
        self.options_frame = tk.LabelFrame(self.root, text=self.tr('defects_objects'), padx=8, pady=4)
        self.options_frame.grid(row=1, column=0, sticky='ew', padx=8, pady=0, columnspan=14)
        self.widgets_to_translate['options_frame'] = self.options_frame

        self.vacancies_cb = tk.Checkbutton(self.options_frame, text=self.tr('vacancies'), variable=self.show_vacancies)
        self.vacancies_cb.grid(row=0, column=0, sticky='w')
        self.widgets_to_translate['vacancies_cb'] = self.vacancies_cb
        self.substitutions_cb = tk.Checkbutton(self.options_frame, text=self.tr('substitutions'), variable=self.show_substitutions)
        self.substitutions_cb.grid(row=0, column=1, sticky='w')
        self.widgets_to_translate['substitutions_cb'] = self.substitutions_cb
        self.show_inter_sites_cb = tk.Checkbutton(self.options_frame, text=self.tr('show_inter_sites'), variable=self.show_inter_sites)
        self.show_inter_sites_cb.grid(row=0, column=2, sticky='w')
        self.widgets_to_translate['show_inter_sites_cb'] = self.show_inter_sites_cb
        self.show_network_atoms_cb = tk.Checkbutton(self.options_frame, text=self.tr('show_network_atoms'), variable=self.show_network_atoms)
        self.show_network_atoms_cb.grid(row=0, column=3, sticky='w')
        self.widgets_to_translate['show_network_atoms_cb'] = self.show_network_atoms_cb
        self.show_added_atoms_cb = tk.Checkbutton(self.options_frame, text=self.tr('show_added_atoms'), variable=self.show_added_atoms)
        self.show_added_atoms_cb.grid(row=0, column=4, sticky='w')
        self.widgets_to_translate['show_added_atoms_cb'] = self.show_added_atoms_cb

        # Sélection atomes/sites à tracer (Listbox multisélection)
        atoms_sites_sel_frame = tk.LabelFrame(self.root, text=self.tr('apply_selection'))
        atoms_sites_sel_frame.grid(row=1, column=99, sticky='ne', padx=8, pady=2, rowspan=1)
        # Liste des atomes
        self.atom_listbox_label = tk.Label(atoms_sites_sel_frame, text=self.tr('select_atoms'))
        self.atom_listbox_label.pack(anchor='w')
        self.widgets_to_translate['atom_listbox_label'] = self.atom_listbox_label
        self.atom_listbox = tk.Listbox(atoms_sites_sel_frame, selectmode='multiple', exportselection=0, height=6)
        self.atom_listbox.pack(fill='both', padx=2, pady=2)
        # Liste des sites
        self.site_listbox_label = tk.Label(atoms_sites_sel_frame, text=self.tr('select_sites'))
        self.site_listbox_label.pack(anchor='w')
        self.widgets_to_translate['site_listbox_label'] = self.site_listbox_label
        self.site_listbox = tk.Listbox(atoms_sites_sel_frame, selectmode='multiple', exportselection=0, height=6)
        self.site_listbox.pack(fill='both', padx=2, pady=2)

        self.apply_selection_btn = tk.Button(atoms_sites_sel_frame, text=self.tr('apply_selection'), command=self.update_selected_atoms_sites)
        self.apply_selection_btn.pack(pady=4)
        self.widgets_to_translate['apply_selection_btn'] = self.apply_selection_btn

        action_frame = tk.Frame(self.root)
        action_frame.grid(row=2, column=0, columnspan=14, pady=5)
        self.generate_btn = tk.Button(action_frame, text=self.tr('generate_plot'), command=self.generate_plot)
        self.generate_btn.pack(side='left', padx=10)
        self.widgets_to_translate['generate_btn'] = self.generate_btn
        self.quit_btn = tk.Button(action_frame, text=self.tr('quit'), command=self.root.quit)
        self.quit_btn.pack(side='left', padx=10)
        self.widgets_to_translate['quit_btn'] = self.quit_btn

        self.preview_label = tk.Label(self.root, text=self.tr('files_read'))
        self.preview_label.grid(row=3, column=0, sticky='w', padx=8, pady=2, columnspan=14)
        self.widgets_to_translate['preview_label'] = self.preview_label
        self.preview_text = tk.Text(self.root, height=14, width=150, state='disabled', wrap='none')
        self.preview_text.grid(row=4, column=0, columnspan=14, sticky='nsew', padx=8, pady=2)

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        self.param_frame.grid_columnconfigure(1, weight=1)
        self.param_frame.grid_columnconfigure(4, weight=1)

        # Initialisation des listes d'atomes/sites et du menu abscisse
        self.update_site_atom_inputs()

    def update_site_atom_inputs(self):
        # Appelle la logique pour mettre à jour les widgets dynamiquement
        self.logic.update_site_atom_inputs()
        self.update_atom_site_listboxes()
        self.update_xaxis_menu()  # MAJ la sélection abscisse à chaque update

        # ----------- AJOUT : bind dynamique sur tous les Entry de noms d'espèces ----------- #
        for entry in self.network_atom_entries:
            entry.bind("<KeyRelease>", lambda event: self.update_xaxis_menu())
        for entry in self.added_atom_entries:
            entry.bind("<KeyRelease>", lambda event: self.update_xaxis_menu())
        for entry in self.inter_site_entries:
            entry.bind("<KeyRelease>", lambda event: self.update_xaxis_menu())
        # ----------------------------------------------------------------------------------- #

    def update_xaxis_menu(self):
        # Récupère la liste des atomes (réseau + interstitiels + ajoutés)
        atom_names = []
        for e in self.network_atom_entries:
            v = e.get().strip()
            if v: atom_names.append(v)
        for e in self.added_atom_entries:
            v = e.get().strip()
            if v: atom_names.append(v)
        # Propose choix : x_<nom> et mu_<nom>
        choices = [f"x_{v}" for v in atom_names] + [f"mu_{v}" for v in atom_names]
        if not choices:
            choices = ["x_at1", "mu_at1"]
        old_choice = self.xaxis_choice.get()
        if old_choice not in choices:
            self.xaxis_choice.set(choices[0])
        # Détruit l'ancien menu si besoin
        if self.xaxis_menu is not None:
            self.xaxis_menu.destroy()
        # Crée le nouveau menu
        self.xaxis_menu = tk.OptionMenu(self.param_frame, self.xaxis_choice, *choices)
        self.xaxis_menu.grid(row=6, column=1, sticky="ew", columnspan=3)
        # Label associé
        if self.xaxis_label is not None:
            self.xaxis_label.config(text=self.tr('xaxis_label') if 'xaxis_label' in translations[self.language] else "Abscisse")

    def update_atom_site_listboxes(self):
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
        self.selected_atoms = [self.atom_listbox.get(i) for i in self.atom_listbox.curselection()]
        self.selected_sites = [self.site_listbox.get(i) for i in self.site_listbox.curselection()]

    def generate_plot(self):
        self.update_selected_atoms_sites()
        self.plotter.generate_plot()

    def save_plot_dialog(self):
        self.plotter.save_plot_dialog()

    def change_language(self, lang):
        self.language = lang
        self.refresh_labels()
        self.update_xaxis_menu()

    def refresh_labels(self):
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
