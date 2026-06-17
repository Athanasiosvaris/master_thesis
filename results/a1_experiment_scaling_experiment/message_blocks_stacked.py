import matplotlib.pyplot as plt
import numpy as np

# Data
architectures = ['Αρχιτεκτονική Α', 'Αρχιτεκτονική Β']

expected = np.array([630, 630])
received = np.array([423, 625])
missing = expected - received

fig, ax = plt.subplots(figsize=(8, 5))

# Stacked bars
bars_received = ax.bar(
    architectures,
    received,
    label='Ληφθέντα μπλοκ'
)

bars_missing = ax.bar(
    architectures,
    missing,
    bottom=received,
    label='Χαμένα μπλοκ'
)

# Labels inside bars
for bar in bars_received:
    h = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2,
        h/2,
        f'{int(h)}',
        ha='center',
        va='center',
        fontsize=10
    )

for bar, miss, rec in zip(bars_missing, missing, received):
    ax.text(
        bar.get_x() + bar.get_width()/2,
        rec + miss/2,
        f'{int(miss)}',
        ha='center',
        va='center',
        fontsize=10
    )

# Coverage percentage above bars
coverage = received / expected * 100

for bar, cov, exp in zip(bars_missing, coverage, expected):
    ax.text(
        bar.get_x() + bar.get_width()/2,
        exp + 10,
        f'{cov:.1f}%',
        ha='center',
        fontsize=11,
        fontweight='bold'
    )

ax.set_ylabel('Πλήθος μπλοκ μηνυμάτων')
ax.set_title('Σύγκριση Ληφθέντων και Χαμένων Μπλοκ Μηνυμάτων')

# Add vertical headroom so bars/labels don't reach the top
ax.set_ylim(0, expected.max() * 1.25)

# Clean style
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Place the legend above the plot so it never overlaps the bars
ax.legend(
    frameon=False,
    loc='lower center',
    bbox_to_anchor=(0.5, 1.02),
    ncol=2
)

plt.tight_layout()

plt.savefig(
    'message_blocks_stacked.png',
    dpi=300,
    bbox_inches='tight'
)

plt.show()
