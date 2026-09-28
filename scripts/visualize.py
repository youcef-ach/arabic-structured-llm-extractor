import json
import matplotlib.pyplot as plt
import sys
import os

def visualize_military_state(json_path):
    print(f"Loading {json_path} for visualization...")
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # If the JSON is wrapped in our sample format (with "text" and "ground_truth")
    if "ground_truth" in data:
        state = data["ground_truth"]
    else:
        state = data

    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot forces recursively
    def plot_unit(unit, color, marker):
        location = unit.get("location")
        if location and "coordinate" in location:
            x, y = location["coordinate"]
            # Plot the point
            ax.scatter(x, y, color=color, marker=marker, s=150, edgecolors='black', label=unit["name"])
            # Add label
            ax.text(x + 0.05, y + 0.05, unit["name"], fontsize=9, color=color, 
                    bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
            
        # Plot subunits
        for sub_unit in unit.get("sub_units", []):
            sub_marker = 'o' if marker == 's' else '^' # change marker for sub units
            plot_unit(sub_unit, color, sub_marker)

    forces = state.get("forces", [])
    for force in forces:
        color = 'blue' if force.get("affiliation") == "friendly" else 'red'
        plot_unit(force, color, 's') # 's' for square (battalion level usually)
        
    # Set up the map view
    ax.set_title("Tactical Map Visualization")
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Check if we have items, otherwise just show a default grid
    if len(ax.collections) > 0:
        plt.legend(loc='upper right')
    else:
        print("No units with coordinates found to plot.")
        
    output_img = "map_visualization.png"
    plt.savefig(output_img)
    print(f"Visualization saved to {output_img}")

if __name__ == "__main__":
    target = "augmented_data/sample_0.json"
    if len(sys.argv) > 1:
        target = sys.argv[1]
        
    try:
        import matplotlib
        visualize_military_state(target)
    except ImportError:
        print("Error: matplotlib is not installed. Run: pip install matplotlib")
