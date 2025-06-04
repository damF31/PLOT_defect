"""
Logique métier pour la gestion des défauts ponctuels.

Responsabilités principales :
- Génère dynamiquement les listes de fichiers à lire pour chaque courbe (_L_r_k, _i_r_k, _i_r_i)
- Calcule les labels et indices associés selon les options d'affichage et la configuration utilisateur
- Fournit les listes d’atomes/sites actifs pour le plotter et le data_loader
- Filtre la génération des courbes selon la sélection de l'utilisateur (atomes/sites à tracer)
"""

import tkinter as tk
import config

class DefectLogic:
    def __init__(self, app):
        """
        Initialise la logique métier.
        Paramètres :
            app : référence à l'application principale (pour accéder à l'état de l'interface)
        """
        self.app = app
        self.debug = True  # Mettre à False pour désactiver les prints de debug

    def update_site_atom_inputs(self):
        """
        Met à jour dynamiquement les widgets d'entrée pour les sites/atomes réseau, interstitiels, ajoutés.
        Pour chaque catégorie :
        - détruit les widgets existants,
        - recrée le bon nombre d'entrées,
        - pré-remplit soit avec la valeur précédente, soit avec une valeur par défaut,
        - relie chaque entrée à un callback pour actualiser la liste d'atomes/sites sélectionnables.
        """
        # Sites réseau
        self._update_entries(
            self.app.network_sites_frame, self.app.network_site_entries,
            self.app.num_network_sites.get(), "Site réseau", config.MAX_SITES,
            [f"site_{i+1}" for i in range(self.app.num_network_sites.get())],
            self.app.update_atom_site_listboxes
        )
        # Atomes réseau
        self._update_entries(
            self.app.network_atoms_frame, self.app.network_atom_entries,
            self.app.num_network_atoms.get(), "Atome réseau", config.MAX_ATOMS,
            [f"Al_{i+1}" for i in range(self.app.num_network_atoms.get())],
            self.app.update_atom_site_listboxes
        )
        # Sites interstitiels
        self._update_entries(
            self.app.inter_sites_frame, self.app.inter_site_entries,
            self.app.num_inter_sites.get(), "Site interstitiel", config.MAX_SITES,
            [f"site_inter_{i+1}" for i in range(self.app.num_inter_sites.get())],
            self.app.update_atom_site_listboxes
        )
        # Atomes ajoutés
        self._update_entries(
            self.app.added_atoms_frame, self.app.added_atom_entries,
            self.app.num_added_atoms.get(), "Atome ajouté", config.MAX_ATOMS,
            [f"H_{i+1}" for i in range(self.app.num_added_atoms.get())],
            self.app.update_atom_site_listboxes
        )

    def _update_entries(self, frame, entries, n, label, maxn, defaults, refresh_callback=None):
        """
        Méthode utilitaire interne pour mettre à jour dynamiquement un bloc d'entrées (Entry + Label).

        Paramètres :
            frame : Frame tkinter contenant les Entry (sera vidé puis rempli)
            entries : liste python qui contient les Entry (sera vidée/remplie)
            n : nombre d'entrées à créer (int)
            label : texte du label à afficher pour chaque entrée
            maxn : nombre maximum d'entrées autorisées
            defaults : liste de valeurs par défaut à insérer si pas de valeur précédente
            refresh_callback : fonction à appeler à chaque modification (souvent pour rafraîchir la liste d'atomes/sites sélectionnables)
        """
        previous_values = [e.get() for e in entries]
        for widget in frame.winfo_children():
            widget.destroy()
        entries.clear()
        try:
            n = int(n)
            if n < 0 or n > maxn:
                raise ValueError
        except Exception:
            n = min(maxn, max(0, int(n) if str(n).isdigit() else 1))
        for i in range(n):
            tk.Label(frame, text=f"{label} {i+1} :").grid(row=i, column=0, sticky='e')
            entry = tk.Entry(frame)
            # Préserve la valeur précédente si elle existe, sinon utilise la valeur par défaut
            if i < len(previous_values) and previous_values[i].strip():
                entry.insert(0, previous_values[i])
            else:
                entry.insert(0, defaults[i] if i < len(defaults) else "")
            entry.grid(row=i, column=1, sticky='ew')
            if refresh_callback:
                # Rafraîchit la liste d'atomes/sites lors de la modification de la valeur
                entry.bind("<FocusOut>", lambda e, ent=entry: refresh_callback())
                entry.bind("<KeyRelease>", lambda e, ent=entry: refresh_callback())
            entries.append(entry)
        frame.grid_columnconfigure(1, weight=1)

    def get_active_atoms_sites(self):
        """
        Retourne, sous forme de listes, tous les atomes et sites actuellement actifs, en fonction des cases à cocher de l'interface.
        - Atomes réseau, atomes ajoutés
        - Sites réseau, sites interstitiels
        - Atomes/Sites globaux selon les filtres
        Retour :
            (network_atoms, added_atoms, network_sites, inter_sites, atoms, sites) : tuple de listes
        """
        network_atoms = [e.get().strip() for e in self.app.network_atom_entries if e.get().strip()]
        added_atoms = [e.get().strip() for e in self.app.added_atom_entries if e.get().strip()]
        network_sites = [e.get().strip() for e in self.app.network_site_entries if e.get().strip()]
        inter_sites = [e.get().strip() for e in self.app.inter_site_entries if e.get().strip()]
        atoms = []
        sites = []
        if self.app.show_network_atoms.get():
            atoms += network_atoms
        if self.app.show_added_atoms.get():
            atoms += added_atoms
        # Toujours inclure les sites réseau pour les lacunes
        sites += network_sites
        if self.app.show_inter_sites.get():
            sites += inter_sites
        return network_atoms, added_atoms, network_sites, inter_sites, atoms, sites

    def generate_file_list_and_labels(self):
        """
        Génère la liste (fichier, label) pour chaque courbe à afficher, en tenant compte des options cochées,
        et de la sélection utilisateur (atomes/sites à tracer).
        - Lacunes sur sites réseau : si "vacances" ET "atomes réseau" cochés
        - Substitutions (i ≠ k) pour tous atomes/sites sélectionnés
        - Défauts interstitiels pour atomes ajoutés et sites interstitiels sélectionnés

        Retour :
            file_labels : liste de tuples (nom_fichier, label) pour chaque courbe à afficher
        """
        base = self.app.system_name.get()
        show_vac = self.app.show_vacancies.get()
        show_sub = self.app.show_substitutions.get()

        network_atoms, added_atoms, network_sites, inter_sites, all_atoms, all_sites = self.get_active_atoms_sites()
        n_net_sites = len(network_sites)
        n_all_atoms = len(all_atoms)
        n_all_sites = len(all_sites)

        # Prise en compte de la sélection utilisateur (listes vides = tout sélectionner)
        selected_atoms = getattr(self.app, 'selected_atoms', []) or all_atoms
        selected_sites = getattr(self.app, 'selected_sites', []) or all_sites

        file_labels = []

        # Lacunes sur sites réseau
        if show_vac and self.app.show_network_atoms.get():
            for k, site in enumerate(network_sites, 1):
                if site in selected_sites:
                    file_labels.append((f"{base}_L_r_{k}", f"V_{{{site}}}"))

        # Substitutions (i ≠ k)
        if show_sub and n_all_atoms > 0 and n_all_sites > 0:
            for k in range(1, n_all_sites+1):
                if all_sites[k-1] not in selected_sites:
                    continue
                for i in range(1, n_all_atoms+1):
                    if i != k and all_atoms[i-1] in selected_atoms:
                        file_labels.append((f"{base}_{i}_r_{k}", f"{all_atoms[i-1]}_{{{all_sites[k-1]}}}"))
            # Défauts interstitiels pour atomes ajoutés/sélectionnés sur sites interstitiels
            if self.app.show_added_atoms.get() and inter_sites and added_atoms:
                for idx_site, site in enumerate(inter_sites, start=len(network_sites)+1):
                    if site not in selected_sites:
                        continue
                    for idx_atom, atom in enumerate(added_atoms, start=len(network_atoms)+1):
                        if atom in selected_atoms:
                            file_labels.append((f"{base}_{idx_atom}_r_{idx_site}", f"{atom}_{{{site}}}"))
        if self.debug:
            print("[DEBUG] file_labels =", file_labels)

        return file_labels

