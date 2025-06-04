"""
Point d'entrée de l'application.
- Initialise la fenêtre Tkinter.
- Crée l'instance principale de l'application.
- Lance la boucle principale.
"""
from ui_widgets import DefectPlotterApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = DefectPlotterApp(root)
    root.mainloop()
