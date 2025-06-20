"""
Dictionnaire de traductions pour l’interface utilisateur (français / anglais).

Permet la localisation dynamique de tous les textes affichés dans l’interface,
y compris les boutons, labels, messages d’erreur, options de tracé, etc.

Utilisation typique :
    lang = "fr" ou "en"
    translations[lang]['system_params']  # => texte localisé

Astuce : pour ajouter une langue, ajouter une nouvelle clé de dictionnaire à la racine.
"""

translations = {
    'fr': {
        'system_params': "Paramètres système",
        'system_name': "Nom du système :",
        'network_sites': "Nb sites réseau (avec lacunes)",
        'network_atoms': "Nb atomes réseau",
        'inter_sites': "Nb sites interstitiels",
        'added_atoms': "Nb atomes ajoutés",
        'update': "Mettre à jour",
        'system_title': "Nom système (pour le titre) :",
        'temperature': "Température (K) :",
        'output_file': "Nom du fichier de sortie :",
        'save': "Sauvegarder",
        'defects_objects': "Défauts & Objets à afficher",
        'vacancies': "Lacunes",
        'substitutions': "Substitutions",
        'show_inter_sites': "Afficher sites interstitiels",
        'show_network_atoms': "Afficher atomes réseau",
        'show_added_atoms': "Afficher atomes ajoutés",
        'generate_plot': "Générer le graphique",
        'quit': "Quitter",
        'files_read': "Fichiers lus :",
        'missing_files': "Les fichiers suivants sont manquants ou invalides :",
        'no_file': "Aucun fichier de données valide trouvé.",
        'no_file_title': "Aucun fichier",
        'ylabel_defects': "Concentration de défauts ponctuels",
        'missing_files': "Les fichiers suivants sont manquants ou invalides :",
        'missing_files_title': "Fichiers manquants",
        'no_file': "Aucun fichier de données valide trouvé.",
        'no_file_title': "Aucun fichier",
        'save_dialog_title': "Enregistrer le graphique sous...",
        'save_success_title': "Succès",
        'save_success_msg': "Graphique sauvegardé sous",
        'error_title': "Erreur",
        'unsupported_format': "Format non supporté",

        # AJOUTS pour configuration du tracé et sélection atomes/sites
        'print_options': "Options des tracés", 
        'xmin': "X min",
        'xmax': "X max",
        'ymin': "Y min",
        'ymax': "Y max",
        'xscale': "Échelle X",
        'yscale': "Échelle Y",
        'xscale_label': "Abcisse",
        'yscale_label': "Ordonnée",
        'scale_linear': "Linéaire",
        'scale_log': "Logarithmique",
        'select_atoms': "Sélectionner les atomes à tracer",
        'select_sites': "Sélectionner les sites à tracer",
        'apply_selection': "Appliquer la sélection",
    },
    'en': {
        'system_params': "System parameters",
        'system_name': "System name:",
        'network_sites': "Nb. network sites (with vacancies)",
        'network_atoms': "Nb. network atoms",
        'inter_sites': "Nb. interstitial sites",
        'added_atoms': "Nb. added atoms",
        'update': "Update",
        'system_title': "System name (for title):",
        'temperature': "Temperature (K):",
        'output_file': "Output filename:",
        'save': "Save",
        'defects_objects': "Defects & Objects to display",
        'vacancies': "Vacancies",
        'substitutions': "Substitutions",
        'show_inter_sites': "Show interstitial sites",
        'show_network_atoms': "Show network atoms",
        'show_added_atoms': "Show added atoms",
        'generate_plot': "Generate plot",
        'quit': "Quit",
        'files_read': "Files read:",
        'missing_files': "The following files are missing or invalid:",
        'no_file': "No valid data file found.",
        'no_file_title': "No file",
        'ylabel_defects': "Concentration of point defects",
        'missing_files': "The following files are missing or invalid:",
        'missing_files_title': "Missing files",
        'no_file': "No valid data file found.",
        'no_file_title': "No file",
        'save_dialog_title': "Save plot as...",
        'save_success_title': "Success",
        'save_success_msg': "Plot saved as",
        'error_title': "Error",
        'unsupported_format': "Unsupported format",

        # ADDED for plot config and atom/site selection
        'print_options': "Plot options", 
        'xmin': "X min",
        'xmax': "X max",
        'ymin': "Y min",
        'ymax': "Y max",
        'xscale': "X scale",
        'yscale': "Y scale",
        'xscale_label': "x-axis",
        'yscale_label': "y-axis",
        'scale_linear': "Linear",
        'scale_log': "Logarithmic",
        'select_atoms': "Select atoms to plot",
        'select_sites': "Select sites to plot",
        'apply_selection': "Apply selection",
    }
}
