Résumé et explications
But du fichier

Ce module définit une classe DataManager pour centraliser la gestion des fichiers de données :

    Chargement unique et en mémoire de tous les fichiers
    Génération automatique de la liste des noms de colonnes
    Extraction facilitée des colonnes à tracer, par label

Fonctions principales

    __init__
    Initialise les structures : tableau de données, labels, fichiers chargés.

    load_data(atom_names, file_list)
        Génère la liste ordonnée des noms de colonnes à partir des noms d’atomes.
        Charge tous les fichiers et les empile dans un tableau numpy 3D.
        Met à jour la liste des fichiers chargés.

    get_column(file_idx, col_label)
        Permet de récupérer une colonne donnée (par son label, ex : 'x_Al_1', 'Hf_DP') pour un fichier particulier.
        Utilisé pour le tracé ou l’analyse.

Utilisation typique

    Tu crées un objet DataManager.
    Tu charges les données (après choix de la config et sélection des fichiers).
    Tu utilises get_column pour extraire les colonnes à tracer, selon les choix de l’utilisateur dans l’interface.

