import matplotlib.pyplot as plt
import numpy as np

# Data
metrics = ["Μέση", "p95", "Max", "Min"]

arch_a = [35.724, 62.805, 67.302, 4.675]
arch_b = [30.561, 56.201, 59.164, 0.006]

x = np.arange(len(metrics))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 5))

bars1 = ax.bar(x - width / 2, arch_a, width, label="Αρχιτεκτονική Α")

bars2 = ax.bar(x + width / 2, arch_b, width, label="Αρχιτεκτονική Β")

ax.set_ylabel("Χρόνος (δευτερόλεπτα)")
ax.set_xticks(x)
ax.set_xticklabels(metrics)

# Value labels
for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.8,
            f"{h:.3f}",
            ha="center",
            fontsize=9,
        )

# Clean style
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.legend(frameon=False)

plt.title("Σύγκριση Καθυστέρησης Μηνυμάτων")
plt.tight_layout()

plt.savefig("experiment1_latency_comparison.png", dpi=300, bbox_inches="tight")

plt.show()
