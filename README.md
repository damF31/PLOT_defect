# Visualiseur de Concentrations de Défauts Ponctuels

Ce projet est une interface graphique Python pour visualiser des concentrations de défauts ponctuels, adaptée à des systèmes matériaux (ex : TiN, TiO2...).  
Il permet de lire des fichiers de données, d’afficher les courbes, de personnaliser les paramètres du système ainsi que l’affichage, et désormais de changer dynamiquement la langue de l’interface (français/anglais) **sans perte des paramètres saisis**.

---

## Fonctionnalités principales

- **Interface graphique Tkinter** conviviale et configurable
- **Multilingue (FR/EN)** : sélection dynamique de la langue via menu déroulant, sans perte des valeurs d’entrée
- **Affichage et sauvegarde de courbes** matplotlib des concentrations de défauts
- **Gestion intelligente des chemins de fichiers** (vos fichiers de données doivent être dans le dossier où vous exécutez `main.py`)
- **Gestion des erreurs et messages contextuels traduits**
- **Architecture modulaire** : séparation entre logique métier, chargement des données, interface et configuration

---

## Installation

1. **Prérequis**  
   - Python 3.x
   - `matplotlib`, `numpy`, `tkinter` (souvent inclus avec Python, sinon : `pip install matplotlib numpy`)
2. **Téléchargement**
   - Placez tous les fichiers Python et le dossier `translations.py` dans un même dossier (ex : `INTERFACE`).

3. **Organisation recommandée**
   ```
   INTERFACE/
   ├── main.py
   ├── ui_widgets.py
   ├── defect_logic.py
   ├── data_loader.py
   ├── plotter.py
   ├── config.py
   ├── translations.py
   ├── ... (vos fichiers de données)
   ```

---

## Utilisation

1. **Placez vos fichiers de données (_L_r_k, _i_r_k, etc.) dans le dossier où vous exécutez la commande Python.**
2. **Lancez l’interface** depuis le dossier contenant les scripts :
   ```bash
   python3 main.py
   ```
3. **Remplissez les paramètres**, sélectionnez les options, et cliquez sur “Générer le graphique”.
4. **Changez la langue** grâce au menu déroulant en haut à droite (“fr” ou “en”) : toutes les étiquettes, boutons, messages, et boîtes de dialogue sont traduits dynamiquement, sans perte des valeurs déjà saisies.
5. **Sauvegardez le graphique** via le bouton dédié.

---

## Changement de langue dynamique

- L’interface propose un menu (en haut à droite) permettant de passer du français à l’anglais et vice-versa.
- **Aucune donnée saisie (entrées, cases à cocher, etc.) n’est perdue lors du changement de langue.**
- Les messages d’erreur, d’alerte, de confirmation, ainsi que les titres et étiquettes sont traduits à la volée.

---

## Astuces et résolution de problèmes

- **Fichiers non trouvés** : vérifiez que vous exécutez bien le script dans le dossier où se trouvent vos fichiers de données.
- **Ajout d’une langue** : modifiez `translations.py` et ajoutez une clé pour la nouvelle langue.
- **Personnalisation des titres/labels** : éditez les chaînes dans `translations.py` pour adapter le vocabulaire à vos usages.

---

## Structure des fichiers principaux

- `main.py` : point d’entrée, lance l’interface.
- `ui_widgets.py` : construit l’interface graphique, gère le changement de langue et la persistance des paramètres.
- `defect_logic.py` : logique métier et génération de la liste des fichiers à lire.
- `data_loader.py` : lecture et parsing des fichiers de données (chemin direct, pas de concaténation supplémentaire).
- `plotter.py` : affichage et sauvegarde du graphique, messages traduits dynamiquement.
- `translations.py` : dictionnaire centralisé des textes (labels, boutons, messages) pour chaque langue.
- `config.py` : valeurs par défaut, couleurs, styles...

---

## Extrait : Ajout d’une langue dans `translations.py`

```python
translations = {
    'fr': {
        'system_params': "Paramètres système",
        # ... (autres clés)
    },
    'en': {
        'system_params': "System parameters",
        # ... (other keys)
    },
    # Ajoutez ici une nouvelle langue :
    'es': {
        'system_params': "Parámetros del sistema",
        # ...etc
    }
}
```

---

## Licence

MIT

---

## Auteur

Vous pouvez contacter [votre nom ou pseudo] pour toute question ou suggestion.

# Visualiseur de concentrations de défauts ponctuels — Structure du code

Ce projet permet de visualiser les concentrations de défauts ponctuels en fonction de la composition et des différents types de sites et atomes via une interface graphique.

## Structure des fichiers

- **main.py**  
  Point d’entrée. Démarre l’interface graphique Tkinter et lance l’application.

- **ui_widgets.py**  
  Définit la classe principale de l’interface utilisateur (`DefectPlotterApp`).  
  Gère :  
  - L’organisation des widgets (champs de saisie, boutons, cases à cocher)
  - Les interactions et callbacks
  - Délègue la logique métier à `defect_logic.py` et l’affichage à `plotter.py`

- **defect_logic.py**  
  Contient la logique de génération des courbes à afficher :  
  - Génération des listes de fichiers à lire (_L_r_k, _i_r_k, _i_r_i)
  - Gestion des indices et labels selon les options cochées
  - Fournit les listes d’atomes/sites actifs

- **data_loader.py**  
  Fonctions utilitaires pour :
  - Charger et parser les fichiers de données
  - Gérer les erreurs de lecture et les fichiers manquants

- **plotter.py**  
  Gère l'affichage et la sauvegarde du graphique matplotlib :
  - Récupère la liste des fichiers et labels à tracer
  - Affiche le graphique, la légende, le titre
  - Prend en charge la sauvegarde (PNG, JPG, PDF)

- **config.py**  
  Paramètres globaux :
  - Couleurs, styles de lignes
  - Valeurs par défaut (nom système, température, etc.)
  - Limites maximales (nombre de sites, d’atomes)

## Fonctionnement général

1. L’utilisateur configure les atomes et sites via l’interface graphique.
2. Les options d’affichage (vacances, substitutions, sites interstitiels, etc.) sont sélectionnées via des cases à cocher.
3. Lors de la génération du graphique :
   - La logique (`defect_logic.py`) détermine la liste des fichiers à lire et les labels associés.
   - Les données sont chargées (`data_loader.py`).
   - Les courbes sont tracées et la légende/titre sont générés automatiquement (`plotter.py`).
   - Les fichiers absents ou non valides sont signalés à l’utilisateur.
4. L’utilisateur peut sauvegarder le graphique généré.

## Personnalisation

- Pour ajouter d’autres types de défauts ou d’options d’affichage, modifiez principalement `defect_logic.py` et adaptez l’interface dans `ui_widgets.py`.
- Les couleurs et styles sont centralisés dans `config.py`.
- Pour augmenter le nombre maximum d’atomes/sites affichables, modifiez `config.py`.

---

Pour toute extension, ajoutez une fonction dédiée dans le fichier concerné, sans casser la modularité du projet.
