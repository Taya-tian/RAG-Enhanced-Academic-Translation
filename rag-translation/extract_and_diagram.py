import re
import matplotlib.pyplot as plt
import numpy as np

# Input file
input_file = "data/sensitive_test_top_k600similarity0.5_prompt.txt"

# Regex pattern
pattern = r"([0-9]+)\. \[similarity: ([0-9.]+)\]"

# Dictionary:
# key   -> similarity
# value -> number before dot
data = {}

with open(input_file, "r", encoding="utf-8") as f:
    text = f.read()

matches = re.findall(pattern, text)

for first_group, second_group in matches:
    key = float(second_group)
    value = int(first_group)
    data[key] = value

print("Extracted dict:")
print(data)

# Sort by x for better plotting
sorted_items = sorted(data.items())

x = [k for k, v in sorted_items]
y = [v for k, v in sorted_items]

# Draw diagram
# Polynomial degree
degree = 8

# Fit polynomial
coefficients = np.polyfit(x, y, degree)

# Create function
poly_function = np.poly1d(coefficients)

print("Derived function:")
print(poly_function)

# Generate smooth curve
x_smooth = np.linspace(min(x), max(x), 500)
y_smooth = poly_function(x_smooth)

# Plot
plt.figure(figsize=(10, 6))

# Original points
plt.scatter(x, y, label="Data points")

# Fitted function
plt.plot(x_smooth, y_smooth, label=f"Polynomial degree {degree}")

plt.xlabel("Similarity")
plt.ylabel("Value")
plt.title("Function Derived From Data")
plt.legend()
plt.grid(True)

# Save image
plt.savefig("fitted_function.png", dpi=300, bbox_inches="tight")

plt.show()
