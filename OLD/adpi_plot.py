import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
import argparse

def load_and_plot(filename, label, color, linestyle='-', linewidth=3, annotate=True, annotate_fontsize=12):
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
            print(f"[Warning] No data detected in {filename}")
            return False

        data_str = "".join(lines[start_index:])
        data = np.loadtxt(StringIO(data_str))

        if data.ndim == 1:
            data = np.expand_dims(data, axis=0)

        if data.shape[1] < 7:
            print(f"[Warning] Insufficient data columns in {filename}")
            return False

        x = data[:, 5]
        y = data[:, 6]

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
        return True

    except Exception as e:
        print(f"[Error] File {filename} : {e}")
        return False

def plot_all(file_prefix, output_prefix,
             title=None, xlabel=None, ylabel=None,
             annotate=True, annotate_fontsize=12):

    plt.figure(figsize=(8, 7.2))
    plt.grid(color="#C0C0C0")
    plt.yscale("log")
    plt.ylim(1e-12, 1)
    plt.xlim(0, 0.05)
    plt.tick_params(axis='both', which='both', direction='in', top=True, right=True)

    if xlabel:
        plt.xlabel(xlabel, fontsize=15, fontweight='bold')
    else:
        plt.xlabel("C[H]", fontsize=15, fontweight='bold')

    if ylabel:
        plt.ylabel(ylabel, fontsize=15, fontweight='bold')
    else:
        plt.ylabel("Point defect concentrations", fontsize=15, fontweight='bold')

    if title:
        plt.text(0.03, 0.2, title,
                 fontsize=14, fontweight='bold', ha='center')

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

    any_plotted = False
    for suffix, label, color, linestyle, linewidth in courbes:
        filename = f"{file_prefix}_{suffix}"
        plotted = load_and_plot(filename, label, color, linestyle, linewidth,
                               annotate=annotate, annotate_fontsize=annotate_fontsize)
        if plotted:
            any_plotted = True

    if not any_plotted:
        print("[Error] No data was plotted. Check your file_prefix and files.")
        return

    plt.tight_layout()

    if not annotate:
        plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5),
                   fontsize=12, frameon=True)

    plt.savefig(f"{output_prefix}.eps", format='eps')
    plt.savefig(f"{output_prefix}.pdf", format='pdf')
    plt.savefig(f"{output_prefix}.jpg", format='jpg', dpi=300)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Plot TiN defect concentrations from data files.")
    parser.add_argument("--file_prefix", type=str, required=True,
                        help="Prefix for input data files (e.g. TiN_adpi)")
    parser.add_argument("--output_prefix", type=str, default="conc_tin_d_H",
                        help="Prefix for output plot files (default: conc_tin_d_H)")
    parser.add_argument("--title", type=str, default=r"$\mathrm{Ti_{0.51}N_{0.49} + H\ at\ 1000K}$",
                        help="Title for the plot (LaTeX syntax supported)")
    parser.add_argument("--xlabel", type=str, default="C[H]",
                        help="Label for x-axis")
    parser.add_argument("--ylabel", type=str, default="Point defect concentrations",
                        help="Label for y-axis")
    parser.add_argument("--no_annotate", action='store_true',
                        help="Disable annotation next to curves; will show legend instead")
    parser.add_argument("--annotate_fontsize", type=int, default=12,
                        help="Font size for annotations next to curves")

    args = parser.parse_args()

    plot_all(
        file_prefix=args.file_prefix,
        output_prefix=args.output_prefix,
        title=args.title,
        xlabel=args.xlabel,
        ylabel=args.ylabel,
        annotate=not args.no_annotate,
        annotate_fontsize=args.annotate_fontsize
    )

if __name__ == "__main__":
    main()

