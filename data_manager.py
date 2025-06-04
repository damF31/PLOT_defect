import numpy as np

class DataManager:
    """
    Classe centrale pour la gestion des données multi-fichiers - lecture, stockage, extraction.
    Permet de charger en mémoire tous les fichiers en une fois, de générer dynamiquement la liste des noms de colonnes,
    et de fournir un accès simple aux colonnes à tracer via les labels (mu_X, x_X, x_DP, Hf_DP).
    """

    def __init__(self):
        """
        Initialise les structures de données.
        - self.data : tableau numpy à 3 dimensions (n_fichiers, n_lignes, n_colonnes)
        - self.colnames : liste ordonnée des noms de colonnes (str)
        - self.files : liste des fichiers chargés (pour référence)
        """
        self.data = None         # Tableau des données [n_fichiers, n_lignes, n_colonnes]
        self.colnames = []       # Noms des colonnes (générés dynamiquement)
        self.files = []          # Liste des noms de fichiers lus

    def load_data(self, atom_names, file_list):
        """
        Charge tous les fichiers de données en mémoire, et génère la liste ordonnée des noms de colonnes.

        Paramètres
        ----------
        atom_names : list of str
            Liste des noms d'atomes (ex : ['Al_1', 'Al_2', 'H_1']).
            Sert à générer les labels mu_XXX et x_XXX.

        file_list : list of str
            Liste des chemins de fichiers de données à lire.
            Chaque fichier doit avoir le même nombre et ordre de colonnes.

        Effet :
        -------
        - self.colnames est généré : ['mu_Al_1', 'mu_Al_2', 'mu_H_1', 'x_Al_1', 'x_Al_2', 'x_H_1', 'x_DP', 'Hf_DP']
        - self.data est un tableau numpy (n_files, n_rows, n_cols)
        - self.files est mis à jour
        """
        mu_labels = [f"mu_{a}" for a in atom_names]
        x_labels = [f"x_{a}" for a in atom_names]
        self.colnames = mu_labels + x_labels + ["x_DP", "Hf_DP"]
        self.files = file_list[:]
        self.data = []

        for f in file_list:
            # Lecture du fichier en ignorant la première ligne (header)
            arr = np.loadtxt(f, delimiter=',', skiprows=1)
            self.data.append(arr)
        self.data = np.array(self.data)  # shape: (n_files, n_rows, n_cols)

    def get_column(self, file_idx, col_label):
        """
        Retourne la colonne désirée sous forme d'un tableau numpy, pour un fichier donné.

        Paramètres
        ----------
        file_idx : int
            Index du fichier dans self.files (même ordre que file_list lors du chargement)
        col_label : str
            Nom de la colonne désirée (doit figurer dans self.colnames)

        Retour :
        -------
        col : np.ndarray
            Colonne extraite du tableau de données, shape (n_rows,)

        Exception :
        -----------
        - ValueError si le label n'est pas dans self.colnames
        - IndexError si le file_idx est hors limite
        """
        idx = self.colnames.index(col_label)
        return self.data[file_idx][:, idx]
