import matplotlib.pyplot as plt

# Define data and color map
data = [0.2, 0.5, 0.8, 0.95, 0.7]
color_map = {0: 'red', 0.5: 'yellow', 1: 'green'}

# Define block size
block_size = 50

# Create figure and axes
fig, ax = plt.subplots()

# Plot each square block
for i, value in enumerate(data):
    color = color_map[min(1, value)]
    x = i * block_size
    y = 0
    ax.add_patch(plt.Rectangle(
        xy=(x, y),
        width=block_size,
        height=block_size,
        color=color,
        alpha=value,
    ))

# Set labels and title
plt.xlabel('Company')
plt.ylabel('Performance')
plt.title('Performance of Companies')

# Show the plot
plt.show()