"""
Chargement et parsing des fichiers de données adaptés pour n espèces.

Fonctions principales :
- read_data(filepath, x_col=None, y_col=None, n_species=None) :
    Ouvre et lit les colonnes voulues d'un fichier de données. Détecte le header, gère les erreurs, et permet de choisir quelles colonnes extraire selon leur index. Le nombre d'espèces peut être déduit automatiquement ou imposé.
- get_n_species(filepath) :
    Détecte automatiquement le nombre d'espèces (atomes types) présentes dans un fichier, en se basant sur le nombre de colonnes de données.
- get_colnames(filepath) :
    Essaie de lire les noms d'espèces (atome1, atome2, ...) depuis l'entête du fichier (commentaires #), sinon les déduit automatiquement.
- check_files_exist(file_list) :
    Prend une liste de fichiers et retourne ceux qui sont absents.
"""

import numpy as np
import os
from io import StringIO

debug=False  # Mettre à True pour afficher des informations de debug lors de la lecture des fichiers

def get_n_species(filepath):
    """
    Détecte automatiquement le nombre d'espèces (atomes réseau + interstitiels) dans le fichier de données.
    On suppose que les colonnes sont dans l'ordre suivant : mu_at1, mu_at2, ..., x_at1, x_at2, ..., x_DP, Hf.
    
    Entrée :
        filepath (str) : Chemin du fichier à analyser.

    Sortie :
        n (int) : Nombre d'espèces détectées, ou 0 si non détecté.
    """
    if not os.path.isfile(filepath):
        print(f"[ERREUR] Fichier non trouvé pour détection du nombre d'espèces: {filepath}")
        return 0
    with open(filepath, encoding='latin1') as f:
        for line in f:
            tokens = line.strip().split()
            if not tokens or tokens[0].startswith("#"):
                continue  # Ignore les lignes vides ou commentaires
            ncol = len(tokens)
            # ncol = n (mu) + n (x) + 2 (x_DP, Hf)
            if ncol >= 4:
                n = (ncol - 2) // 2
                return n
    print(f"[ERREUR] Impossible de détecter le nombre d'espèces dans le fichier: {filepath}")
    return 0

def get_colnames(filepath):
    """
    Essaie de lire les noms d'espèces (atome1, atome2, ...) dans l'ordre (réseau puis interstitiel)
    depuis l'entête du fichier (si présente sous forme de commentaires #).
    Retourne une liste de noms, ou ['at1', 'at2', ...] si non trouvé.

    Entrée :
        filepath (str) : Chemin du fichier à analyser.

    Sortie :
        names (list of str) : Liste des noms des espèces, ou liste générique si non trouvés.
    """
    if not os.path.isfile(filepath):
        print(f"[ERREUR] Fichier non trouvé pour lecture de l'entête: {filepath}")
        return []
    with open(filepath, encoding='latin1') as f:
        for line in f:
            if line.strip().startswith("#"):
                # Cherche les colonnes mu_<nom>, x_<nom>
                tokens = line.strip("#").replace(",", " ").replace("=", " ").split()
                names = []
                for tok in tokens:
                    if tok.startswith("mu_") or tok.startswith("x_"):
                        name = tok.split("_", 1)[1]
                        if name not in names:
                            names.append(name)
                if names:
                    return names  # Si trouvé dans l'entête, on retourne la liste
    # Sinon, on déduit depuis le nombre de colonnes
    n = get_n_species(filepath)
    return [f"at{i+1}" for i in range(n)]

def read_data(filepath, x_col=None, y_col=None, n_species=None):
    """
    Ouvre et lit les colonnes utiles d'un fichier de données.

    Entrées :
        filepath (str) : chemin du fichier de données à lire.
        x_col (int, optionnel) : index de la colonne à utiliser pour X (None = dernière colonne x_at).
        y_col (int, optionnel) : index de la colonne à utiliser pour Y (None = colonne concentration de config).
        n_species (int, optionnel) : nombre d'espèces à imposer (sinon auto-détection).

    Sortie :
        (x, y) : tuple de deux np.arrays des valeurs à tracer, ou (None, None) si erreur.
    """
    if not os.path.isfile(filepath):
        report(f"Fichier de données absent: {filepath}")
        return None, None
    try:
        with open(filepath, encoding='latin1') as f:
            lines = f.readlines()
        start_index = None
        for i, line in enumerate(lines):
            tokens = line.strip().split()
            if not tokens or tokens[0].startswith("#"):
                continue  # Ignore les lignes vides ou commentaires
            # On prend la première ligne de données
            try:
                floats = [float(tok) for tok in tokens]
                start_index = i
                break
            except ValueError:
                continue
        if start_index is None:
            report(f"Aucune donnée exploitable dans le fichier: {filepath}")
            return None, None
        data_str = "".join(lines[start_index:])
        
        if debug:
            print(f"[DEBUG] Première ligne de données pour {filepath}: {lines[start_index]}")
            print(f"[DEBUG] Data déduite (après header):\n{data_str[:150]}")  # Affiche les 150 premiers caractères

        data = np.loadtxt(StringIO(data_str))
        if data.ndim == 1:
            data = np.expand_dims(data, axis=0)
        ncol = data.shape[1]
        n = n_species or ((ncol - 2) // 2)
        # Par défaut : X = dernière x_at (H si présent), Y = concentration de config (x_DP)
        if x_col is None:
            x_col = 2 * n - 1  # dernière colonne x_at
        if y_col is None:
            y_col = 2 * n      # x_DP (concentration de config)
        if x_col >= ncol or y_col >= ncol:
            report(f"Index colonne (x_col={x_col}, y_col={y_col}) hors limites [0, {ncol-1}] dans {filepath}")
            return [], []
        x, y = data[:, x_col], data[:, y_col]
        if debug:
            print(f"[DEBUG] x ({filepath}) : {x[:5]}")
            print(f"[DEBUG] y ({filepath}) : {y[:5]}")
        return x, y
    except Exception as e:
        report(f"Erreur lors de la lecture de {filepath} : {str(e)}")
        return [], []

def check_files_exist(file_list):
    """
    Retourne la liste des fichiers absents, chemins à fournir absolus si besoin.

    Entrée :
        file_list (list of tuples) : liste de tuples (nom_fichier, label).

    Sortie :
        missing (list of str) : liste des chemins de fichiers absents.
    """
    missing = []
    for fname, _ in file_list:
        if not os.path.isfile(fname):
            print(f"[ERREUR] Fichier manquant: {fname}")
            missing.append(fname)
    return missing

def report(msg):
    """
    Affiche le message d'erreur ou d'information, à centraliser si besoin.
    """
    print(msg)
