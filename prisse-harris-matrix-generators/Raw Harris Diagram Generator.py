"""
Raw Harris Diagram Generator
Archaeological Stratigraphy Visualizer
Generates PDF and SVG diagrams from CSV relations using Graphviz DOT
"""

import csv
import networkx as nx
import subprocess
import os

# -----------------------------------------
# 1. Load relations from CSV
# -----------------------------------------

edges = []
synch_edges = []

print("Reading relations...")
try:
    with open("./relations.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row_num, row in enumerate(reader, 2):
            if len(row) == 2:
                younger, older = row
                rel_type = "older"
            else:
                younger, older, rel_type = row

            younger, older = younger.strip(), older.strip()
            rel_type = rel_type.strip().lower()

            if rel_type == "older":
                edges.append((older, younger))   # OLDER → YOUNGER
            elif rel_type == "synch":
                synch_edges.append((younger, older))
                
    print(f"  Found {len(edges)} 'older' relations")
    print(f"  Found {len(synch_edges)} 'synch' relations")
    
except FileNotFoundError:
    print("ERROR: File './relations.csv' not found!")
    input("\nPress Enter to exit...")
    exit(1)

# -----------------------------------------
# 2. Load node categories
# -----------------------------------------

categories = {}
print("Reading nodes...")
try:
    with open("./noeuds.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 2:
                node, cat = row[0].strip(), row[1].strip()
                categories[node] = cat
    
    print(f"  Found {len(categories)} nodes with categories")
except FileNotFoundError:
    print("Warning: './noeuds.csv' not found - categories will not be applied")

# Color mapping for categories (all white for raw/minimal diagram)
color_map = {
    "1": "white",
    "2": "white",
    "3": "white",
    "4": "white",
    "5": "white",
    "6": "white",
    "": "white"
}

# Category labels for legend
category_labels = {
    "1": "stone",
    "2": "wood",
    "3": "clay",
    "4": "unknown",
    "5": "-",
    "6": "_",
    "": ""
}

# -----------------------------------------
# 3. Build graph
# -----------------------------------------

print("Building graph...")
G = nx.DiGraph()

if not edges:
    print("ERROR: No 'older' relations found!")
    input("\nPress Enter to exit...")
    exit(1)

# Add all edges
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

# Check for cycles
try:
    if not nx.is_directed_acyclic_graph(G):
        print("ERROR: Cycle detected in relations!")
        input("\nPress Enter to exit...")
        exit(1)
except Exception as e:
    print(f"Error during cycle check: {e}")
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
            # Check if there's an indirect path u->...->v
            has_indirect_path = False
            for w in G.successors(u):
                if w != v and nx.has_path(G, w, v):
                    has_indirect_path = True
                    break
            
            # Keep edge only if no indirect path exists
            if not has_indirect_path:
                G_red.add_edge(u, v)

print(f"  Reduction: {G.number_of_edges()} -> {G_red.number_of_edges()} edges")

# -----------------------------------------
# 4. Generate DOT file with synchronicity visible
# -----------------------------------------

print("Generating DOT file with visible synchronicity...")
dot_file = "./Harris_raw.dot"

# Number nodes for display
node_numbers = {}
for idx, node in enumerate(sorted(G_red.nodes()), start=1):
    node_numbers[node] = str(idx)

# Group synchronous nodes for rank=same
synch_groups = []
processed_nodes = set()

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
        
        processed_nodes.add(a)
        processed_nodes.add(b)

print(f"  Synchronization groups: {len(synch_groups)}")

# Generate DOT file manually
with open(dot_file, "w", encoding="utf-8") as f:
    f.write("digraph G {\n")
    f.write('  rankdir=TB;\n')
    f.write('  splines=ortho;\n')
    f.write('  nodesep=0.6;\n')
    f.write('  ranksep=0.8;\n')
    f.write('  node [shape=box, style=filled, fontname="Arial", margin="0.15,0.10"];\n')
    f.write('  edge [fontname="Arial",minlen=2,arrowsize=0.8];\n\n')
    
    # Add nodes with their numbers (raw version - minimal styling)
    for node in G_red.nodes():
        cat = categories.get(node, "")
        color = color_map.get(cat, "white")
        node_number = node_numbers.get(node, "?")
        node_escaped = node.replace('"', '\\"').replace('\n', ' ')
        
        # Add number in label for the raw diagram
        f.write(f'  "{node_escaped}" [fillcolor="{color}", label=<<font point-size="10">({node_number})</font><br/>{node_escaped}>];\n')
    
    f.write('\n')
    
    # Add standard edges (stratigraphic relations)
    for u, v in G_red.edges():
        u_escaped = u.replace('"', '\\"').replace('\n', ' ')
        v_escaped = v.replace('"', '\\"').replace('\n', ' ')
        f.write(f'  "{u_escaped}" -> "{v_escaped}";\n')
    
    f.write('\n')
    
    # Add synchronous relations with special styling (double black lines)
    for a, b in synch_edges:
        if a in G_red.nodes() and b in G_red.nodes():
            a_escaped = a.replace('"', '\\"').replace('\n', ' ')
            b_escaped = b.replace('"', '\\"').replace('\n', ' ')
            
            f.write(f'  "{a_escaped}" -> "{b_escaped}" [')
            f.write('dir=none, ')
            f.write('color="#000000", ')
            f.write('penwidth=3.0, ')
            f.write('style="solid", ')
            f.write('constraint=false')
            f.write('];\n')
    
    # Rank constraints for synchronicity
    f.write('\n  // Synchronization relations (same rank)\n')
    for group in synch_groups:
        if len(group) > 1:
            nodes_list = ['"' + node.replace('"', '\\"').replace('\n', ' ') + '"' for node in group]
            f.write('  { rank=same; ' + '; '.join(nodes_list) + ' }\n')
    
    f.write("}\n")

# -----------------------------------------
# 5. Generate PDF (vector, editable text)
# -----------------------------------------

pdf_file = "./Harris_raw.pdf"
svg_file = "./Harris_raw.svg"

print(f"\nGenerating {pdf_file}...")

# Check if Graphviz is installed
try:
    subprocess.run(["dot", "-V"], capture_output=True, check=True)
    print("  Graphviz detected and functional")
except (subprocess.CalledProcessError, FileNotFoundError):
    print("ERROR: Graphviz (dot) is not installed or accessible")
    print("Install Graphviz from: https://graphviz.org/download/")
    input("\nPress Enter to exit...")
    exit(1)

# Generate PDF
try:
    result = subprocess.run(
        ["dot", "-Tpdf", dot_file, "-o", pdf_file], 
        capture_output=True, 
        text=True, 
        timeout=30
    )
    
    if result.returncode == 0:
        print(f"✔ PDF generated successfully: {pdf_file}")
        if os.path.exists(pdf_file):
            print(f"  File size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
            print("  Format: Vector PDF with editable text")
    else:
        print(f"✗ Error generating PDF:")
        print(f"  Error message: {result.stderr[:500]}")
        
        # Try simplified version if legend caused issues
        print("\nAttempting simplified version...")
        simple_dot_file = "./Harris_simple.dot"
        
        # Copy DOT but remove legend if present
        with open(dot_file, "r", encoding="utf-8") as src:
            content = src.read()
        
        lines = content.split('\n')
        simple_lines = []
        in_legend = False
        brace_count = 0
        
        for line in lines:
            if 'subgraph cluster_legend' in line:
                in_legend = True
                brace_count = 0
            elif in_legend:
                brace_count += line.count('{') - line.count('}')
                if brace_count < 0:
                    in_legend = False
                continue
            
            if not in_legend:
                simple_lines.append(line)
        
        with open(simple_dot_file, "w", encoding="utf-8") as dst:
            dst.write('\n'.join(simple_lines))
        
        subprocess.run(["dot", "-Tpdf", simple_dot_file, "-o", "./Harris_simple.pdf"], check=True)
        print("✔ Simplified version generated: ./Harris_simple.pdf")
        
except subprocess.TimeoutExpired:
    print("✗ Timeout: Generation took too long")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

# -----------------------------------------
# 5b. Generate SVG (editable in Illustrator)
# -----------------------------------------

print(f"\nGenerating {svg_file}...")

try:
    result_svg = subprocess.run(
        ["dot", "-Tsvg", dot_file, "-o", svg_file],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result_svg.returncode == 0:
        print(f"✔ SVG generated successfully: {svg_file}")
        if os.path.exists(svg_file):
            print(f"  File size: {os.path.getsize(svg_file) / 1024:.1f} KB")
            print("  Format: Vector SVG (editable in Illustrator)")
    else:
        print("✗ Error generating SVG:")
        print(result_svg.stderr[:500])

except subprocess.TimeoutExpired:
    print("✗ Timeout generating SVG")
except Exception as e:
    print(f"✗ Unexpected error (SVG): {e}")

# -----------------------------------------
# 6. Summary
# -----------------------------------------

print("\n" + "="*50)
print("SUMMARY:")

print(f"- Stratigraphic relations: {len(edges)}")
print(f"- Synchronous relations: {len(synch_edges)}")
print(f"- Total nodes: {len(all_nodes)}")
print(f"- Synchronous groups identified: {len(synch_groups)}")

print(f"\nGenerated files:")
print(f"  - DOT: {dot_file}")
print(f"  - PDF: {pdf_file}")
print(f"  - SVG: {svg_file}")

if os.path.exists(pdf_file):
    print("\n✔ Raw Harris diagram generated successfully!")
    print("  Format: Vector PDF (editable text)")
    print("  Synchronous relations shown with double black lines.")
else:
    print("\n✗ Failed to generate main PDF.")
    if os.path.exists("./Harris_simple.pdf"):
        print("  A simplified version was generated: ./Harris_simple.pdf")

if os.path.exists(svg_file):
    print("  SVG ready for editing in Illustrator / Inkscape")

# Option: Auto-open PDF
if os.path.exists(pdf_file):
    try:
        import platform
        system = platform.system()
        if system == "Windows":
            os.startfile(pdf_file)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", pdf_file])
        elif system == "Linux":
            subprocess.run(["xdg-open", pdf_file])
        print("\nOpening PDF...")
    except:
        pass

input("\nPress Enter to exit...")