import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
import os
from io import StringIO

class DefectPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Defect Concentration Plotter")

        self.system_name = tk.StringVar(value="TiN_adpi")
        self.num_atoms = tk.IntVar(value=3)
        self.atom_entries = []
        self.output_basename = tk.StringVar(value="conc_plot")
        self.title_text = tk.StringVar(value="Ti$_{0.51}$N$_{0.49}$ + H at 1000K")

        self.show_vacancies = tk.BooleanVar(value=True)
        self.show_substitutions = tk.BooleanVar(value=True)
        self.show_hydrogens = tk.BooleanVar(value=True)

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="System name (prefix):").grid(row=0, column=0, sticky='w')
        tk.Entry(self.root, textvariable=self.system_name).grid(row=0, column=1, sticky='ew')

        tk.Label(self.root, text="Number of atoms:").grid(row=1, column=0, sticky='w')
        tk.Entry(self.root, textvariable=self.num_atoms).grid(row=1, column=1, sticky='ew')
        tk.Button(self.root, text="Update atoms", command=self.update_atom_inputs).grid(row=1, column=2)

        self.atom_frame = tk.Frame(self.root)
        self.atom_frame.grid(row=2, column=0, columnspan=3, sticky='ew')
        self.update_atom_inputs()

        tk.Label(self.root, text="Plot title:").grid(row=3, column=0, sticky='w')
        tk.Entry(self.root, textvariable=self.title_text).grid(row=3, column=1, sticky='ew', columnspan=2)

        tk.Label(self.root, text="Output basename:").grid(row=4, column=0, sticky='w')
        tk.Entry(self.root, textvariable=self.output_basename).grid(row=4, column=1, sticky='ew')
        tk.Button(self.root, text="Save Plot", command=self.save_plot_dialog).grid(row=4, column=2)

        tk.Checkbutton(self.root, text="Show Vacancies", variable=self.show_vacancies).grid(row=5, column=0, sticky='w')
        tk.Checkbutton(self.root, text="Show Substitutions", variable=self.show_substitutions).grid(row=5, column=1, sticky='w')
        tk.Checkbutton(self.root, text="Show Atom 3 Defects", variable=self.show_hydrogens).grid(row=5, column=2, sticky='w')

        tk.Button(self.root, text="Generate Plot", command=self.generate_plot).grid(row=6, column=1, pady=10)

        self.preview_label = tk.Label(self.root, text="Files to read:")
        self.preview_label.grid(row=7, column=0, columnspan=3, sticky='w')

        self.preview_text = tk.Text(self.root, height=6, width=80)
        self.preview_text.grid(row=8, column=0, columnspan=3, sticky='ew')

        self.root.grid_columnconfigure(1, weight=1)

    def update_atom_inputs(self):
        for widget in self.atom_frame.winfo_children():
            widget.destroy()
        self.atom_entries.clear()

        for i in range(self.num_atoms.get()):
            tk.Label(self.atom_frame, text=f"Atom {i+1}:").grid(row=i, column=0, sticky='w')
            entry = tk.Entry(self.atom_frame)
            entry.insert(0, ["Ti", "N", "H"][i] if i < 3 else "")
            entry.grid(row=i, column=1, sticky='ew')
            self.atom_entries.append(entry)

    def read_data(self, filepath):
        try:
            with open(filepath, encoding='latin1') as f:
                lines = f.readlines()
            start_index = None
            for i, line in enumerate(lines):
                tokens = line.strip().split()
                if len(tokens) >= 8:
                    try:
                        _ = [float(tok) for tok in tokens[:8]]
                        start_index = i
                        break
                    except ValueError:
                        continue
            if start_index is None:
                print(f"[Avertissement] Aucune ligne de données détectée dans {filepath}")
                return None, None

            data_str = "".join(lines[start_index:])
            data = np.loadtxt(StringIO(data_str))
            if data.ndim == 1:
                data = np.expand_dims(data, axis=0)
            if data.shape[1] < 7:
                return None, None
            return data[:, 5], data[:, 6]  # colonnes 6 et 7
        except Exception as e:
            print(f"[ERREUR] Fichier {filepath} : {e}")
            return None, None

    def generate_plot(self):
        plt.figure(figsize=(8, 7.2))
        plt.grid(color="#C0C0C0")
        plt.yscale("log")
        plt.ylim(1e-12, 1)
        plt.xlim(0, 0.05)
        plt.xlabel("C[H]", fontsize=15, fontweight='bold')
        plt.ylabel("Point defect concentrations", fontsize=15, fontweight='bold')
        plt.tick_params(axis='both', which='both', direction='in', top=True, right=True)

        plt.text(0.03, 0.2, self.title_text.get(), fontsize=14, fontweight='bold', ha='center')

        base = self.system_name.get()
        atoms = [entry.get().strip() for entry in self.atom_entries if entry.get().strip()]
        colors = ['blue', 'black', 'black', 'green', 'red', 'red', 'orange', 'purple', 'purple']
        styles = ['-', '-', '--', '-', '-', '--', '-', '-', '--']

        file_templates = []

        if self.show_vacancies.get():
            file_templates += [
                (f"{base}_L_r_1", f"V_{{{atoms[1]}}}"),
                (f"{base}_L_r_2", f"V_{{{atoms[0]}}}")
            ]
        if self.show_substitutions.get():
            file_templates += [
                (f"{base}_1_r_2", f"{atoms[0]}_{{{atoms[1]}}}"),
                (f"{base}_1_r_3", f"{atoms[0]}_{{8c}}"),
                (f"{base}_2_r_1", f"{atoms[1]}_{{{atoms[0]}}}"),
                (f"{base}_2_r_3", f"{atoms[1]}_{{8c}}")
            ]
        if self.show_hydrogens.get():
            file_templates += [
                (f"{base}_3_r_1", f"{atoms[2]}_{{{atoms[0]}}}"),
                (f"{base}_3_r_2", f"{atoms[2]}_{{{atoms[1]}}}"),
                (f"{base}_3_r_3", f"{atoms[2]}_{{8c}}")
            ]

        self.preview_text.delete(1.0, tk.END)

        for (fname, label), color, style in zip(file_templates, colors, styles):
            self.preview_text.insert(tk.END, f"{fname}\n")
            x, y = self.read_data(fname)
            if x is not None and y is not None:
                plt.plot(x, y, label=label, color=color, linestyle=style, linewidth=3)

        plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=12, frameon=True)
        plt.tight_layout()
        plt.show()

    def save_plot_dialog(self):
        fmt = filedialog.asksaveasfilename(defaultextension=".png",
                                           filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("PDF", "*.pdf")],
                                           title="Save Plot As",
                                           initialfile=self.output_basename.get())
        if fmt:
            ext = os.path.splitext(fmt)[1][1:]
            if ext in ["png", "jpg", "pdf"]:
                self.generate_plot()
                plt.savefig(fmt, format=ext, dpi=300)
                messagebox.showinfo("Succès", f"Graphique sauvegardé sous {fmt}")
            else:
                messagebox.showerror("Erreur", "Format non supporté")

if __name__ == "__main__":
    root = tk.Tk()
    app = DefectPlotterApp(root)
    root.mainloop()
