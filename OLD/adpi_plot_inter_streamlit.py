#pour executer: streamlit run fichier.py
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
import streamlit as st

def load_data(filename):
    try:
        with open(filename, encoding='latin1') as f:
            lines = f.readlines()

        start_index = None
        for i, line in enumerate(lines):
            tokens = line.strip().split()
            if len(tokens) < 8:
                continue
            try:
                _ = [float(tok) for tok in tokens[:8]]
                start_index = i
                break
            except ValueError:
                continue

        if start_index is None:
            st.warning(f"No data detected in {filename}")
            return None, None

        data_str = "".join(lines[start_index:])
        data = np.loadtxt(StringIO(data_str))

        if data.ndim == 1:
            data = np.expand_dims(data, axis=0)

        if data.shape[1] < 7:
            st.warning(f"Insufficient data columns in {filename}")
            return None, None

        x = data[:, 5]
        y = data[:, 6]
        return x, y

    except Exception as e:
        st.error(f"Error reading {filename}: {e}")
        return None, None

def plot_curves(file_prefix, annotate, annotate_fontsize):
    courbes = [
        ('L_r_1', r"$V_{N}$", "blue", '-', 3),
        ('1_r_2', r"$N_{Ti}$", "black", '-', 3),
        ('1_r_3', r"$N_{8c}$", "black", '--', 2),
        ('L_r_2', r"$V_{Ti}$", "green", '-', 3),
        ('2_r_1', r"$Ti_{N}$", "red", '-', 3),
        ('2_r_3', r"$Ti_{8c}$", "red", '--', 2),
        ('3_r_1', r"$H_{N}$", "orange", '-', 3),
        ('3_r_2', r"$H_{Ti}$", "purple", '-', 3),
        ('3_r_3', r"$H_{8c}$", "purple", '--', 2)
    ]

    plt.figure(figsize=(8, 7.2))
    plt.grid(color="#C0C0C0")
    plt.yscale("log")
    plt.ylim(1e-12, 1)
    plt.xlim(0, 0.05)
    plt.tick_params(axis='both', which='both', direction='in', top=True, right=True)

    plt.xlabel(st.session_state.xlabel, fontsize=15, fontweight='bold')
    plt.ylabel(st.session_state.ylabel, fontsize=15, fontweight='bold')

    if st.session_state.title:
        plt.text(0.03, 0.2, st.session_state.title,
                 fontsize=14, fontweight='bold', ha='center')

    any_plotted = False
    for suffix, label, color, linestyle, linewidth in courbes:
        filename = f"{file_prefix}_{suffix}"
        x, y = load_data(filename)
        if x is None or y is None:
            continue
        plt.plot(x, y, label=label, color=color,
                 linestyle=linestyle, linewidth=linewidth)
        if annotate:
            plt.annotate(label,
                         xy=(x[-1], y[-1]),
                         xytext=(5, 0),
                         textcoords='offset points',
                         color=color,
                         fontsize=annotate_fontsize,
                         va='center')
        any_plotted = True

    if not any_plotted:
        st.error("No data plotted. Check your file prefix and files.")
        return

    if not annotate:
        plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5),
                   fontsize=12, frameon=True)

    plt.tight_layout()
    st.pyplot(plt.gcf())

def main():
    st.title("TiN Defect Concentrations Plot")

    # Paramètres
    st.session_state.file_prefix = st.text_input("Préfixe des fichiers d'entrée",
                                                value="TiN_adpi")
    st.session_state.output_prefix = st.text_input("Préfixe des fichiers de sortie",
                                                  value="conc_tin_d_H")
    st.session_state.title = st.text_input("Titre du graphique",
                                          value=r"$\mathrm{Ti_{0.51}N_{0.49} + H\ at\ 1000K}$")
    st.session_state.xlabel = st.text_input("Label axe X", value="C[H]")
    st.session_state.ylabel = st.text_input("Label axe Y", value="Point defect concentrations")

    annotate = st.checkbox("Annoter les courbes à côté (désactiver légende)", value=True)
    annotate_fontsize = st.slider("Taille police annotation", min_value=6, max_value=20, value=12)

    if st.button("Tracer"):
        plot_curves(st.session_state.file_prefix, annotate, annotate_fontsize)

if __name__ == "__main__":
    main()

