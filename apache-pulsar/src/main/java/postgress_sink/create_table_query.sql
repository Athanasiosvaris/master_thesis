import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# Ρύθμιση των παραμέτρων του κύματος
z = np.linspace(0, 4 * np.pi, 200)  # Διάδοση κατά z
omega = 2 * np.pi  # Γωνιακή συχνότητα
k = 1              # Αριθμός κύματος
t_vals = np.linspace(0, 2, 100)  # Χρονικές στιγμές

# Δημιουργία του 3D διαγράμματος
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

# Αρχικές γραμμές για το E και H
line_E, = ax.plot([], [], [], 'r', label='Ηλεκτρικό πεδίο E (x)')
line_H, = ax.plot([], [], [], 'b', label='Μαγνητικό πεδίο H (y)')

# Κατεύθυνση διάδοσης (βελάκι στον z άξονα)
ax.quiver(0, 0, 0, 0, 0, 1, length=2, color='black', arrow_length_ratio=0.1, label='Διάδοση (z)')

# Ρύθμιση των αξόνων
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.set_zlim(0, 4 * np.pi)
ax.set_xlabel('x (E)')
ax.set_ylabel('y (H)')
ax.set_zlabel('z (διάδοση)')
ax.set_title('Διάδοση Ηλεκτρομαγνητικού Κύματος (Animation)')
ax.legend()

# Συνάρτηση ενημέρωσης για κάθε frame του animation
def update(t):
    E = np.sin(k * z - omega * t)  # Ταλάντωση E στον x
    H = np.sin(k * z - omega * t)  # Ταλάντωση H στον y

    # Ενημέρωση γραμμών
    line_E.set_data(E, np.zeros_like(z))     # E στον x, y = 0
    line_E.set_3d_properties(z)              # z

    line_H.set_data(np.zeros_like(z), H)     # H στον y, x = 0
    line_H.set_3d_properties(z)              # z

    return line_E, line_H

# Δημιουργία του animation
ani = FuncAnimation(fig, update, frames=t_vals, interval=50, blit=False)

# Εμφάνιση του animation
plt.show()
