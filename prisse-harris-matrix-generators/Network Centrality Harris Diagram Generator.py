"""
Network Centrality Visualization Tool
-------------------------------------
Reads relational data from CSV files, builds a directed acyclic graph (DAG),
computes betweenness and closeness centrality, applies various normalization
methods, and generates color-coded Graphviz visualizations.

Input files:
  - relations.csv : Contains 'older' and 'synch' relationships
  - noeuds.csv    : Optional node categories (not used in core logic)

Output:
  - ./graphes_centralite/ directory with PDF/SVG visualizations
"""

import csv
import networkx as nx
import subprocess
import os
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from sklearn.preprocessing import QuantileTransformer

# -----------------------------------------
# 1. Load relationships
# -----------------------------------------

edges = []            # (older, younger) directed edges
synch_edges = []      # Synchronous edges (undirected grouping)

print("Loading relationships...")

try:
    with open("./relations.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header

        for row_num, row in enumerate(reader, 2):
            # Parse row: either 2 or 3 columns
            if len(row) == 2:
                younger, older = row
                rel_type = "older"
            else:
                younger, older, rel_type = row

            younger, older = younger.strip(), older.strip()
            rel_type = rel_type.strip().lower()

            if rel_type == "older":
                # Edge direction: OLDER → YOUNGER
                edges.append((older, younger))
            elif rel_type == "synch":
                synch_edges.append((younger, older))

    print(f"  Loaded {len(edges)} 'older' relationships")
    print(f"  Loaded {len(synch_edges)} 'synch' relationships")

except FileNotFoundError:
    print("ERROR: './relations.csv' not found!")
    input("\nPress Enter to exit...")
    exit(1)

# -----------------------------------------
# 2. Load node categories (optional)
# -----------------------------------------

categories = {}
print("Loading node categories...")

try:
    with open("./noeuds.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 2:
                node, cat = row[0].strip(), row[1].strip()
                categories[node] = cat

    print(f"  Loaded {len(categories)} nodes with categories")

except FileNotFoundError:
    print("Warning: './noeuds.csv' not found - categories will be ignored")

# -----------------------------------------
# 3. Build graph and compute transitive reduction
# -----------------------------------------

print("Building graph...")
G = nx.DiGraph()

if not edges:
    print("ERROR: No 'older' relationships found!")
    input("\nPress Enter to exit...")
    exit(1)

# Add all directed edges
for u, v in edges:
    G.add_edge(u, v)

# Collect all nodes
all_nodes = set()
for u, v in edges:
    all_nodes.add(u)
    all_nodes.add(v)
for a, b in synch_edges:
    all_nodes.add(a)
    all_nodes.add(b)

print(f"  Total nodes: {len(all_nodes)}")

# Detect cycles (must be a DAG)
try:
    if not nx.is_directed_acyclic_graph(G):
        print("ERROR: Cycle detected in the graph!")
        input("\nPress Enter to exit...")
        exit(1)
except Exception as e:
    print(f"Error during cycle detection: {e}")
    input("\nPress Enter to exit...")
    exit(1)

# Compute transitive reduction manually
print("Computing transitive reduction...")
G_red = nx.DiGraph()

# Copy all nodes
for node in G.nodes():
    G_red.add_node(node)

# Simplified transitive reduction algorithm
for u in G.nodes():
    for v in G.nodes():
        if u != v and G.has_edge(u, v):
            # Check if there is an indirect path u → ... → v
            has_indirect_path = False
            for w in G.successors(u):
                if w != v and nx.has_path(G, w, v):
                    has_indirect_path = True
                    break

            # Keep edge only if no indirect path exists
            if not has_indirect_path:
                G_red.add_edge(u, v)

print(f"  Reduction: {G.number_of_edges()} → {G_red.number_of_edges()} edges")

# -----------------------------------------
# 4. Compute centrality metrics
# -----------------------------------------

print("\nComputing centrality metrics...")

# Convert to undirected for centrality calculations
G_undirected = G_red.to_undirected()

print("  Computing betweenness centrality...")
betweenness = nx.betweenness_centrality(G_undirected)

print("  Computing closeness centrality...")
closeness = nx.closeness_centrality(G_undirected)

print(f"  Betweenness - min: {min(betweenness.values()):.6f}, max: {max(betweenness.values()):.6f}")
print(f"  Closeness - min: {min(closeness.values()):.6f}, max: {max(closeness.values()):.6f}")

# Display closeness distribution statistics
close_values = list(closeness.values())
print(f"\n  Closeness distribution:")
print(f"    Quartiles: Q1={np.percentile(close_values, 25):.6f}, "
      f"Median={np.percentile(close_values, 50):.6f}, "
      f"Q3={np.percentile(close_values, 75):.6f}")
print(f"    Standard deviation: {np.std(close_values):.6f}")

# -----------------------------------------
# 5. Normalization functions
# -----------------------------------------

def normalize_linear(values):
    """Linear scaling to [0,1] range."""
    vals = list(values.values())
    min_val = min(vals)
    max_val = max(vals)
    if max_val == min_val:
        return {node: 0.5 for node in values}
    return {node: (val - min_val) / (max_val - min_val) for node, val in values.items()}

def normalize_log(values, shift=0.001):
    """Logarithmic scaling to [0,1] range."""
    vals = np.array(list(values.values())) + shift
    log_vals = np.log(vals)
    min_log = np.min(log_vals)
    max_log = np.max(log_vals)
    if max_log == min_log:
        return {node: 0.5 for node in values}
    return {node: (np.log(val + shift) - min_log) / (max_log - min_log)
            for node, val in values.items()}

def normalize_power(values, exponent=0.3):
    """Power-law scaling to [0,1] range."""
    vals = np.array(list(values.values()))
    min_val = np.min(vals)
    if min_val < 0:
        vals = vals - min_val

    powered_vals = np.power(vals, exponent)
    min_pow = np.min(powered_vals)
    max_pow = np.max(powered_vals)
    if max_pow == min_pow:
        return {node: 0.5 for node in values}
    return {node: (np.power(val, exponent) - min_pow) / (max_pow - min_pow)
            for node, val in zip(values.keys(), vals)}

def normalize_quantile(values, n_quantiles=10):
    """Quantile-based scaling with n distinct levels."""
    nodes = list(values.keys())
    vals = np.array(list(values.values())).reshape(-1, 1)

    transformer = QuantileTransformer(n_quantiles=n_quantiles, output_distribution='uniform')
    transformed = transformer.fit_transform(vals).flatten()

    return {node: float(transformed[i]) for i, node in enumerate(nodes)}

def normalize_rank(values):
    """Rank-based scaling: each unique value gets a distinct color level."""
    unique_vals = sorted(set(values.values()))
    if len(unique_vals) == 1:
        return {node: 0.5 for node in values}
    val_to_rank = {val: i / (len(unique_vals) - 1) for i, val in enumerate(unique_vals)}
    return {node: val_to_rank[val] for node, val in values.items()}

# -----------------------------------------
# 6. Normalization method registry
# -----------------------------------------

normalization_methods = {
    "linear": {
        "name": "Linear",
        "desc": "Preserves exact proportions",
        "func_between": lambda: normalize_linear(betweenness),
        "func_close": lambda: normalize_linear(closeness)
    },
    "log": {
        "name": "Logarithmic",
        "desc": "Stretches small differences",
        "func_between": lambda: normalize_log(betweenness),
        "func_close": lambda: normalize_log(closeness)
    },
    "power": {
        "name": "Power",
        "desc": "Compromise between linear and log",
        "func_between": lambda: normalize_power(betweenness),
        "func_close": lambda: normalize_power(closeness)
    },
    "quantile": {
        "name": "Quantiles",
        "desc": "10 distinct levels (guaranteed contrast)",
        "func_between": lambda: normalize_quantile(betweenness),
        "func_close": lambda: normalize_quantile(closeness)
    },
    "rank": {
        "name": "Rank",
        "desc": "Maximum contrast (each value unique)",
        "func_between": lambda: normalize_rank(betweenness),
        "func_close": lambda: normalize_rank(closeness)
    }
}

# -----------------------------------------
# 7. Common visualization setup
# -----------------------------------------

# Define color gradient: yellow → red
unique_cmap = LinearSegmentedColormap.from_list(
    "unique",
    ["#FFFFCC", "#FFD700", "#FF8C00", "#FF0000", "#8B0000"]
)

# Legend colors and labels
legend_colors = ["#FFFFCC", "#FFD700", "#FF8C00", "#FF0000", "#8B0000"]
legend_labels = ["Very low", "Low", "Medium", "High", "Very high"]

def get_color_from_gradient(value, cmap):
    """Convert normalized value (0-1) to hex color from the gradient."""
    if value <= 0:
        rgba = cmap(0.05)
    elif value >= 1:
        rgba = cmap(0.95)
    else:
        rgba = cmap(value)
    return '#{:02x}{:02x}{:02x}'.format(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255))

# Assign sequential numbers to nodes
node_numbers = {}
for idx, node in enumerate(sorted(G_red.nodes()), start=1):
    node_numbers[node] = str(idx)

# Group synchronous nodes (connected components via synch_edges)
synch_groups = []
for a, b in synch_edges:
    if a in G_red.nodes() and b in G_red.nodes():
        group_found = False
        for group in synch_groups:
            if a in group or b in group:
                group.add(a)
                group.add(b)
                group_found = True
                break
        if not group_found:
            synch_groups.append({a, b})

print(f"  Synchronization groups: {len(synch_groups)}")

# -----------------------------------------
# 8. Graph generation function
# -----------------------------------------

def generate_metric_graph(metric_name, metric_values, metric_norm, suffix, norm_name, norm_desc):
    """
    Generate a Graphviz DOT file and render it as PDF/SVG.

    Parameters:
      metric_name : Display name for the metric (e.g., "Betweenness")
      metric_values : Raw metric values (for statistics and display)
      metric_norm : Normalized values (0-1) for coloring
      suffix : File suffix (e.g., "betweenness")
      norm_name : Normalization method name (for legend)
      norm_desc : Normalization method description (for legend)
    """
    os.makedirs("./graphes_centralite", exist_ok=True)

    clean_suffix = suffix.replace(" ", "_").lower()
    clean_norm = norm_name.lower()

    dot_file = f"./graphes_centralite/Harris_{clean_suffix}_{clean_norm}.dot"
    pdf_file = f"./graphes_centralite/Harris_{clean_suffix}_{clean_norm}.pdf"
    svg_file = f"./graphes_centralite/Harris_{clean_suffix}_{clean_norm}.svg"

    print(f"  Generating: {metric_name} - {norm_name}")

    with open(dot_file, "w", encoding="utf-8") as f:
        f.write("digraph G {\n")
        f.write('  rankdir=TB;\n')
        f.write('  splines=ortho;\n')
        f.write('  nodesep=0.6;\n')
        f.write('  ranksep=0.8;\n')
        f.write('  node [shape=box, style=filled, fontname="Arial", margin="0.15,0.10"];\n')
        f.write('  edge [fontname="Arial", minlen=2, arrowsize=0.8];\n\n')

        # Write nodes
        for node in G_red.nodes():
            node_number = node_numbers.get(node, "?")
            node_escaped = node.replace('"', '\\"').replace('\n', ' ')

            norm_value = metric_norm.get(node, 0)
            color = get_color_from_gradient(norm_value, unique_cmap)
            actual_value = metric_values.get(node, 0)

            f.write(f'  "{node_escaped}" [fillcolor="{color}", label=<<font point-size="10">({node_number})</font><br/>{node_escaped}<br/><font point-size="8">{actual_value:.6f}</font>>];\n')

        f.write('\n')

        # Write directed edges
        for u, v in G_red.edges():
            u_escaped = u.replace('"', '\\"').replace('\n', ' ')
            v_escaped = v.replace('"', '\\"').replace('\n', ' ')
            f.write(f'  "{u_escaped}" -> "{v_escaped}";\n')

        f.write('\n')

        # Write synchronous edges (undirected, thicker)
        for a, b in synch_edges:
            if a in G_red.nodes() and b in G_red.nodes():
                a_escaped = a.replace('"', '\\"').replace('\n', ' ')
                b_escaped = b.replace('"', '\\"').replace('\n', ' ')
                f.write(f'  "{a_escaped}" -> "{b_escaped}" [dir=none, color="#000000", penwidth=3.0, style="solid", constraint=false];\n')

        # rank=same constraints for synchronous groups
        f.write('\n  // Synchronization constraints\n')
        for group in synch_groups:
            if len(group) > 1:
                nodes_list = ['"' + node.replace('"', '\\"').replace('\n', ' ') + '"' for node in group]
                f.write('  { rank=same; ' + '; '.join(nodes_list) + ' }\n')

        # LEGEND at the bottom
        f.write('\n\n  // LEGEND\n')
        f.write('  subgraph cluster_legend {\n')
        f.write('    rank="min";\n')
        f.write(f'    label="Legend - {metric_name} (normalization: {norm_name})";\n')
        f.write('    fontsize=11;\n')
        f.write('    fontname="Arial";\n')
        f.write('    margin=20;\n')
        f.write('    color="lightgray";\n')
        f.write('    style="filled";\n')
        f.write('    fillcolor="#F9F9F9";\n')
        f.write('    labelloc="t";\n')
        f.write('    node [shape=none, margin=0, fontname="Arial", style=""];\n\n')

        f.write('    legend_table [label=<\n')
        f.write('      <table border="0" cellborder="0" cellspacing="2" cellpadding="4">\n')
        f.write('        <tr><td colspan="5"><b>Color gradient</b></td></tr>\n')

        # Color row
        f.write('        <tr>\n')
        for color in legend_colors:
            f.write(f'          <td border="1" bgcolor="{color}" width="25" height="15"></td>\n')
        f.write('        </tr>\n')

        # Label row
        f.write('        <tr>\n')
        for label in legend_labels:
            f.write(f'          <td align="center"><font point-size="9">{label}</font></td>\n')
        f.write('        </tr>\n')

        # Method description
        f.write('        <tr><td colspan="5" align="center"><font point-size="9"><i>')
        f.write(f'{norm_desc}')
        f.write('</i></font></td></tr>\n')

        # Statistics
        f.write('        <tr><td colspan="5" align="center"><font point-size="8">')
        f.write(f'Min: {min(metric_values.values()):.6f} | ')
        f.write(f'Max: {max(metric_values.values()):.6f} | ')
        f.write(f'Median: {np.median(list(metric_values.values())):.6f}')
        f.write('</font></td></tr>\n')

        f.write('      </table>\n')
        f.write('    >];\n')
        f.write('  }\n\n')

        f.write("}\n")

    # Render PDF and SVG
    success = True
    try:
        subprocess.run(["dot", "-Tpdf", dot_file, "-o", pdf_file], capture_output=True, timeout=30, check=True)
    except:
        success = False
        print(f"    ✗ PDF generation failed")

    try:
        subprocess.run(["dot", "-Tsvg", dot_file, "-o", svg_file], capture_output=True, timeout=30, check=True)
    except:
        if success:
            print(f"    ✗ SVG generation failed")

    return pdf_file if success else None

# -----------------------------------------
# 9. Generate all graphs
# -----------------------------------------

print("\n" + "="*60)
print("GENERATING ALL GRAPHS (5 methods × 2 metrics)")
print("="*60)

generated_files = {
    "betweenness": [],
    "closeness": []
}

for method_key, method_info in normalization_methods.items():
    print(f"\n--- Method: {method_info['name']} ---")

    # Generate betweenness graph
    between_norm = method_info["func_between"]()
    pdf_between = generate_metric_graph(
        "Betweenness Centrality",
        betweenness,
        between_norm,
        "betweenness",
        method_info['name'],
        method_info['desc']
    )
    if pdf_between:
        generated_files["betweenness"].append(pdf_between)

    # Generate closeness graph
    close_norm = method_info["func_close"]()
    pdf_close = generate_metric_graph(
        "Closeness Centrality",
        closeness,
        close_norm,
        "closeness",
        method_info['name'],
        method_info['desc']
    )
    if pdf_close:
        generated_files["closeness"].append(pdf_close)

# -----------------------------------------
# 10. Generate original graph (no colors)
# -----------------------------------------

print("\n--- Original graph ---")
original_dot = "./graphes_centralite/Harris_original.dot"
original_pdf = "./graphes_centralite/Harris_original.pdf"
original_svg = "./graphes_centralite/Harris_original.svg"

with open(original_dot, "w", encoding="utf-8") as f:
    f.write("digraph G {\n")
    f.write('  rankdir=TB;\n')
    f.write('  splines=ortho;\n')
    f.write('  nodesep=0.6;\n')
    f.write('  ranksep=0.8;\n')
    f.write('  node [shape=box, style=filled, fontname="Arial", margin="0.15,0.10"];\n')
    f.write('  edge [fontname="Arial", minlen=2, arrowsize=0.8];\n\n')

    for node in G_red.nodes():
        node_number = node_numbers.get(node, "?")
        node_escaped = node.replace('"', '\\"').replace('\n', ' ')
        f.write(f'  "{node_escaped}" [fillcolor="white", label=<<font point-size="10">({node_number})</font><br/>{node_escaped}>];\n')

    f.write('\n')
    for u, v in G_red.edges():
        u_escaped = u.replace('"', '\\"').replace('\n', ' ')
        v_escaped = v.replace('"', '\\"').replace('\n', ' ')
        f.write(f'  "{u_escaped}" -> "{v_escaped}";\n')

    f.write('\n')
    for a, b in synch_edges:
        if a in G_red.nodes() and b in G_red.nodes():
            a_escaped = a.replace('"', '\\"').replace('\n', ' ')
            b_escaped = b.replace('"', '\\"').replace('\n', ' ')
            f.write(f'  "{a_escaped}" -> "{b_escaped}" [dir=none, color="#000000", penwidth=3.0, style="solid", constraint=false];\n')

    f.write('\n')
    for group in synch_groups:
        if len(group) > 1:
            nodes_list = ['"' + node.replace('"', '\\"').replace('\n', ' ') + '"' for node in group]
            f.write('  { rank=same; ' + '; '.join(nodes_list) + ' }\n')

    f.write("}\n")

try:
    subprocess.run(["dot", "-Tpdf", original_dot, "-o", original_pdf], capture_output=True, check=True)
    subprocess.run(["dot", "-Tsvg", original_dot, "-o", original_svg], capture_output=True, check=True)
    print(f"  ✓ Original graph generated")
except:
    print(f"  ✗ Original graph generation failed")

# -----------------------------------------
# 11. Final summary
# -----------------------------------------

print("\n" + "="*70)
print("FINAL SUMMARY - ALL GRAPHS GENERATED")
print("="*70)

print(f"\n📁 Output directory: ./graphes_centralite/")
print(f"\n📊 {len(generated_files['betweenness'])} betweenness graphs generated:")
for i, file in enumerate(generated_files['betweenness'], 1):
    print(f"   {i}. {os.path.basename(file)}")

print(f"\n📊 {len(generated_files['closeness'])} closeness graphs generated:")
for i, file in enumerate(generated_files['closeness'], 1):
    print(f"   {i}. {os.path.basename(file)}")

print(f"\n📊 1 original graph:")
print(f"   - Harris_original.pdf")

print("\n" + "-"*70)
print("NORMALIZATION METHODS LEGEND:")
print("  • Linear       : preserves exact proportions")
print("  • Logarithmic  : stretches small differences")
print("  • Power        : compromise between linear and log")
print("  • Quantiles    : 10 distinct levels (guaranteed contrast)")
print("  • Rank         : each unique value gets its own color")

print("\n✅ All graphs generated successfully!")
print("   You can now visually compare the different methods.")
print(f"\n📂 Files are in: {os.path.abspath('./graphes_centralite')}")

input("\nPress Enter to close...")