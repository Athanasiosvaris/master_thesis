import matplotlib.pyplot as plt
import numpy as np

# Containers
containers = ["pulsar", "jobmanager", "taskmanager", "mosquitto", "postgres", "rustfs"]

# CPU mean (in cores)
arch_a = [0.153, 0.0259, 0.0849, 0.0007, 0.0009, 0.0165]
arch_b = [0.08540, 0.0, 0.0, 0.00054, 0.00065, 0.00061]  # jobmanager/taskmanager not running

# Track which containers are not running in architecture B
not_running_b = {"jobmanager", "taskmanager"}

x = np.arange(len(containers))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 5))

bars1 = ax.bar(x - width / 2, arch_a, width, label="Αρχιτεκτονική Α")
bars2 = ax.bar(x + width / 2, arch_b, width, label="Αρχιτεκτονική Β")

ax.set_ylabel("CPU (πυρήνες)")
ax.set_xticks(x)
ax.set_xticklabels(containers)

# Value labels
for bar in bars1:
    h = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        h + 0.002,
        f"{h:.4f}",
        ha="center",
        fontsize=8,
    )

for bar, name in zip(bars2, containers):
    h = bar.get_height()
    if name in not_running_b:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            0.002,
            "—",
            ha="center",
            fontsize=10,
        )
    else:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.002,
            f"{h:.4f}",
            ha="center",
            fontsize=8,
        )

# Clean style
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.legend(frameon=False)

plt.title("Σύγκριση Μέσης Χρήσης CPU ανά Container")
plt.tight_layout()

plt.savefig("cpu_mean_comparison.png", dpi=300, bbox_inches="tight")

plt.show()
