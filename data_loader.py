"""
Chargement et parsing des fichiers de données adaptés pour n espèces.
- read_data(filepath, x_col=None, y_col=None, n_species=None): Ouvre et lit la colonne voulue d'un fichier, détecte le header, gère les erreurs. n_species peut être déduit automatiquement.
- get_n_species(filepath): Détecte automatiquement le nombre d'espèces dans le fichier.
- get_colnames(filepath): Donne la liste des noms d'espèces (atome1, atome2, ...).
- check_files_exist(file_list): Retourne la liste des fichiers absents.
"""

import numpy as np
import os
from io import StringIO

debug=True

def get_n_species(filepath):
    """
    Détecte automatiquement le nombre d'espèces (atomes réseau + interstitiels) dans le fichier.
    On considère que mu_at1, mu_at2, ..., x_at1, x_at2, ..., x_DP, Hf sont présents.
    """
    if not os.path.isfile(filepath):
        print(f"[ERREUR] Fichier non trouvé pour détection du nombre d'espèces: {filepath}")  # MODIF gestion d’erreur
        return 0
    with open(filepath, encoding='latin1') as f:
        for line in f:
            tokens = line.strip().split()
            if not tokens or tokens[0].startswith("#"):
                continue
            ncol = len(tokens)
            # ncol = n (mu) + n (x) + 2 (x_DP, Hf)
            if ncol >= 4:
                n = (ncol - 2) // 2
                return n
    print(f"[ERREUR] Impossible de détecter le nombre d'espèces dans le fichier: {filepath}")  # MODIF gestion d’erreur
    return 0

def get_colnames(filepath):
    """
    Essaie de lire les noms d'espèces (atome1, atome2, ...) dans l'ordre (réseau puis interstitiel)
    depuis l'entête du fichier (si présente sous forme de commentaires #).
    Retourne une liste de noms, ou ['at1', 'at2', ...] si non trouvé.
    """
    if not os.path.isfile(filepath):
        print(f"[ERREUR] Fichier non trouvé pour lecture de l'entête: {filepath}")  # MODIF gestion d’erreur
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
                    return names
    # Sinon, on déduit depuis le nombre de colonnes
    n = get_n_species(filepath)
    return [f"at{i+1}" for i in range(n)]

def get_colnames_full(filepath):
    """
    Retourne la liste complète des noms de colonnes dans l'ordre du fichier :
    mu1, mu2, ..., x_at1, x_at2, ..., x_DP, Hf_DP
    Si l'entête n'est pas lisible, construit par défaut.
    """
    # Essaie de lire l'entête
    try:
        with open(filepath, encoding='latin1') as f:
            for line in f:
                if line.strip().startswith("mu"):
                    # Utilise la ligne d'entête pour détecter les noms, découpe sur les espaces
                    return line.strip().split()
    except Exception:
        pass
    # Sinon, construit à partir du nombre de colonnes
    n = get_n_species(filepath)
    colnames = []
    for i in range(n):
        colnames.append(f"mu{i+1}")
    for i in range(n):
        colnames.append(f"x_at{i+1}")
    colnames.append("x_DP")
    colnames.append("Hf_DP")
    return colnames


def read_data(filepath, x_col=None, y_col=None, n_species=None):
    """
    Ouvre et lit les colonnes utiles d'un fichier de données.
    x_col : index colonne à utiliser pour X (None = x_at dernière colonne)
    y_col : index colonne à utiliser pour Y (None = concentration de conf)
    n_species : permet d'imposer le nombre d'espèces (sinon auto)
    Retourne (x, y) ou (None, None) si le fichier est absent ou invalide.
    """
    if not os.path.isfile(filepath):
        report(f"Fichier de données absent: {filepath}")  # MODIF gestion d’erreur
        return None, None
    try:
        with open(filepath, encoding='latin1') as f:
            lines = f.readlines()
        start_index = None
        for i, line in enumerate(lines):
            tokens = line.strip().split()
            if not tokens or tokens[0].startswith("#"):
                continue
            # On prend la première ligne de données
            try:
                floats = [float(tok) for tok in tokens]
                start_index = i
                break
            except ValueError:
                continue
        if start_index is None:
            report(f"Aucune donnée exploitable dans le fichier: {filepath}")  # MODIF gestion d’erreur
            return None, None
        data_str = "".join(lines[start_index:])
        
        if debug:
              print(f"[DEBUG] Première ligne de données pour {filepath}: {lines[start_index]}")
              print(f"[DEBUG] Data déduite (après header):\n{data_str[:150]}")  # Affiche les 200 premiers caractères

        data = np.loadtxt(StringIO(data_str))
        if data.ndim == 1:
            data = np.expand_dims(data, axis=0)
        ncol = data.shape[1]
        n = n_species or ((ncol - 2) // 2)
        # Par défaut : X = dernière x_at (H si présent), Y = concentration de config (x_DP)
        if x_col is None:
            x_col = 2 * n - 1  # dernière colonne x_at
        if y_col is None:
            y_col = 2 * n      # x_DP (concentration de config)
        if x_col >= ncol or y_col >= ncol:
            report(f"Index colonne (x_col={x_col}, y_col={y_col}) hors limites [0, {ncol-1}] dans {filepath}")  # MODIF gestion d’erreur
            return [], []
        x, y = data[:, x_col], data[:, y_col]
        if debug:
            print(f"[DEBUG] x ({filepath}) : {x[:5]}")
            print(f"[DEBUG] y ({filepath}) : {y[:5]}")
        return x, y
    except Exception as e:
        report(f"Erreur lors de la lecture de {filepath} : {str(e)}")  # MODIF gestion d’erreur
        return [], []

def check_files_exist(file_list):
    """
    Retourne la liste des fichiers absents, chemins à fournir absolus si besoin.
    file_list : liste de tuples (nom_fichier, label)
    """
    missing = []
    for fname, _ in file_list:
        if not os.path.isfile(fname):
            print(f"[ERREUR] Fichier manquant: {fname}")  # MODIF gestion d’erreur
            missing.append(fname)
    return missing
