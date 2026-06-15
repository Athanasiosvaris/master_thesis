import matplotlib.pyplot as plt

watermarks = ["0 δευτερόλεπτα", "5 δευτερόλεπτα", "10 δευτερόλεπτα"]
completion_rate = [29.44, 29.00, 28.44]

plt.figure(figsize=(8,5))

bars = plt.bar(watermarks, completion_rate)

plt.title("Ποσοστό συμπληρωμένων τιμών ανά watermark")
plt.xlabel("Watermark")
plt.ylabel("Ποσοστό συμπληρωμένων τιμών (%)")

for bar in bars:
    y = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2,
        y + 0.1,
        f"{y:.2f}%",
        ha="center"
    )

plt.ylim(0, 35)

plt.tight_layout()
plt.savefig("watermark_completion_rate.png", dpi=300, bbox_inches="tight")
plt.show()