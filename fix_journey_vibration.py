"""
Fix the journey visualization vibration issue by removing scale transform on hover
"""

with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Change journey-node hover from scale to filter
old_journey_node = """        .journey-node {
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .journey-node:hover {
            transform: scale(1.1);
        }"""

new_journey_node = """        .journey-node {
            cursor: pointer;
            transition: filter 0.2s ease;
        }

        .journey-node:hover {
            /* Removed scale transform to prevent vibration */
            filter: brightness(1.2);
        }"""

# Replace all occurrences
content = content.replace(old_journey_node, new_journey_node)

# Fix 2: Improve node-circle hover transition
old_node_circle = """        .node-circle {
            filter: drop-shadow(0 0 10px currentColor);
            transition: all 0.3s ease;
        }

        .journey-node:hover .node-circle {
            filter: drop-shadow(0 0 20px currentColor);
        }"""

new_node_circle = """        .node-circle {
            filter: drop-shadow(0 0 10px currentColor);
            transition: filter 0.2s ease;
        }

        .journey-node:hover .node-circle {
            filter: drop-shadow(0 0 20px currentColor) brightness(1.2);
        }"""

content = content.replace(old_node_circle, new_node_circle)

with open('automated_signals_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed journey visualization vibration issue")
print("\nChanges made:")
print("1. Removed transform: scale(1.1) from .journey-node:hover")
print("2. Added filter: brightness(1.2) for smooth hover effect")
print("3. Changed transition from 'all' to 'filter' for better performance")
print("4. Reduced transition duration from 0.3s to 0.2s")
print("\nResult: Smooth hover effect without vibration!")
