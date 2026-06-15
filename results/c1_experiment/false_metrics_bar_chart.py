import matplotlib.pyplot as plt
import numpy as np

# Data
metrics = ['MAE', 'RMSE', 'MAPE']

arch_a = [404.21, 614.37, 36.29]
arch_b = [450.52, 898.61, 39.90]

x = np.arange(len(metrics))
width = 0.35

fig, ax1 = plt.subplots(figsize=(8, 5))

# MAE & RMSE
bars1 = ax1.bar(
    x[:2] - width/2,
    arch_a[:2],
    width,
    label='Αρχιτεκτονική Α'
)

bars2 = ax1.bar(
    x[:2] + width/2,
    arch_b[:2],
    width,
    label='Αρχιτεκτονική Β'
)

ax1.set_ylabel('Watt')
ax1.set_xticks(x)
ax1.set_xticklabels(metrics)

# Second axis for MAPE
ax2 = ax1.twinx()

bars3 = ax2.bar(
    x[2] - width/2,
    arch_a[2],
    width,
    label='Αρχιτεκτονική Α (MAPE)'
)

bars4 = ax2.bar(
    x[2] + width/2,
    arch_b[2],
    width,
    label='Αρχιτεκτονική Β (MAPE)'
)

ax2.set_ylabel('%')

# Value labels
for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width()/2,
            h + 10,
            f'{h:.1f}',
            ha='center',
            fontsize=9
        )

for bars in [bars3, bars4]:
    for bar in bars:
        h = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width()/2,
            h + 0.5,
            f'{h:.1f}%',
            ha='center',
            fontsize=9
        )

# Clean style
ax1.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)



plt.title('Σύγκριση Μετρικών Σφάλματος')
plt.tight_layout()

plt.savefig(
    'experiment3_error_metrics.png',
    dpi=300,
    bbox_inches='tight'
)

plt.show()