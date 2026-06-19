import csv
import networkx as nx
import subprocess
import os
import sys
import time
import math
import re

# -----------------------------------------
# PHASE CONFIGURATION & COLORS
# -----------------------------------------
PHASE_ORDER = ["-7", "-6", "-5", "-4", "-3", "-2", "-2b", "-1", "0.1", "0.2", "1", "2", "3", "4", "5"]

# Color palette for phases
COLOR_PALETTE = [
    "#5D3A1A", "#8B4513", "#A0522D", "#B8860B", "#CD853F",
    "#D2691E", "#DAA520", "#BDB76B", "#9ACD32", "#6B8E23",
    "#4682B4", "#5F9EA0", "#6495ED", "#87CEEB", "#E0FFFF"
]

color_map = {}
for i, phase in enumerate(PHASE_ORDER):
    color_map[phase] = COLOR_PALETTE[i] if i < len(COLOR_PALETTE) else "#CCCCCC"
color_map[""] = "#FFFFFF"

print("="*60)
print("HARRIS PHASE DIAGRAM GENERATOR - STABLE VERSION (NO TEXT LABELS)")
print("="*60)

# -----------------------------------------
# 1. Read UC phase information
# -----------------------------------------
uc_phases = {}
print("\n📁 Reading UC phases...")
try:
    with open("./noeuds.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 2:
                node, phase = row[0].strip(), row[1].strip()
                uc_phases[node] = phase
    print(f"  ✓ {len(uc_phases)} UCs with phases found")
except FileNotFoundError:
    print("  ⚠️  File './noeuds.csv' not found")
    uc_phases = {}

# -----------------------------------------
# 2. Assign numbers to UCs
# -----------------------------------------
print("\n🔢 Assigning numbers to UCs...")
uc_numbers = {}
for idx, uc in enumerate(sorted(uc_phases.keys()), start=1):
    uc_numbers[uc] = str(idx)
print(f"  ✓ {len(uc_numbers)} UCs numbered")

# -----------------------------------------
# 3. Read cluster relationships
# -----------------------------------------
edges = []
synch_edges = []
all_clusters_set = set()

print("\n📁 Reading cluster relationships...")
try:
    with open("./relations_clusters.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) == 2:
                younger, older = row
                rel_type = "older"
            else:
                younger, older, rel_type = row

            younger, older = younger.strip(), older.strip()
            rel_type = rel_type.strip().lower()

            if rel_type == "older":
                edges.append((older, younger))
                all_clusters_set.add(older)
                all_clusters_set.add(younger)
            elif rel_type == "synch":
                synch_edges.append((younger, older))
                all_clusters_set.add(younger)
                all_clusters_set.add(older)
                
    print(f"  ✓ {len(edges)} 'older' relationships found")
    print(f"  ✓ {len(synch_edges)} 'synch' relationships found")
except FileNotFoundError:
    print("❌ ERROR: File './relations_clusters.csv' not found!")
    input("\nPress Enter to exit...")
    sys.exit(1)

# -----------------------------------------
# 4. Read cluster descriptions and UCs
# -----------------------------------------
cluster_data = {}
print("\n📁 Reading cluster descriptions and UCs...")
try:
    with open("./noeuds_clusters.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        
        for row in reader:
            if len(row) >= 2:
                cluster_id = row[0].strip()
                description = row[1].strip()
                
                ucs = []
                for uc in row[2:]:
                    if uc and uc.strip():
                        uc_clean = uc.strip()
                        if uc_clean:
                            ucs.append(uc_clean)
                
                if cluster_id in all_clusters_set:
                    cluster_data[cluster_id] = {
                        'description': description,
                        'ucs': ucs
                    }
    print(f"  ✓ {len(cluster_data)} clusters with data found")
except FileNotFoundError:
    print("  ⚠️  File './noeuds_clusters.csv' not found")

for cluster in all_clusters_set:
    if cluster not in cluster_data:
        cluster_data[cluster] = {'description': '', 'ucs': []}

# -----------------------------------------
# 5. Identify UCs outside clusters
# -----------------------------------------
print("\n🔍 Identifying UCs outside clusters...")
ucs_in_clusters = set()
for data in cluster_data.values():
    ucs_in_clusters.update(data['ucs'])
ucs_outside_clusters = set(uc_phases.keys()) - ucs_in_clusters
print(f"  ✓ UCs in clusters: {len(ucs_in_clusters)}")
print(f"  ✓ UCs outside clusters: {len(ucs_outside_clusters)}")

# -----------------------------------------
# 6. Read UC-to-UC relationships
# -----------------------------------------
uc_relations = []
print("\n📁 Reading UC relationships...")
try:
    with open("./relations.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 2:
                younger, older = row[0].strip(), row[1].strip()
                rel_type = row[2].strip().lower() if len(row) > 2 else "older"
                if rel_type == "older":
                    uc_relations.append((older, younger))
    print(f"  ✓ {len(uc_relations)} UC relationships found")
except FileNotFoundError:
    print("  ⚠️  File './relations.csv' not found")

# -----------------------------------------
# 7. Build cluster graph
# -----------------------------------------
print("\n🔧 Building cluster graph...")
G_clusters = nx.DiGraph()

for u, v in edges:
    G_clusters.add_edge(u, v)

print(f"  ✓ {G_clusters.number_of_nodes()} clusters")
print(f"  ✓ {G_clusters.number_of_edges()} relationships")

# Cycle detection
print("\n🔍 Checking for cycles...")
try:
    if not nx.is_directed_acyclic_graph(G_clusters):
        print("❌ ERROR: Cycle detected!")
        cycle = nx.find_cycle(G_clusters)
        print(f"  Cycle: {cycle}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    else:
        print("  ✓ No cycles detected")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Transitive reduction
print("\n📉 Computing transitive reduction...")
G_clusters_red = nx.DiGraph()
for node in G_clusters.nodes():
    G_clusters_red.add_node(node)

edge_count = 0
for u in G_clusters.nodes():
    for v in G_clusters.nodes():
        if u != v and G_clusters.has_edge(u, v):
            has_indirect_path = False
            for w in G_clusters.successors(u):
                if w != v and nx.has_path(G_clusters, w, v):
                    has_indirect_path = True
                    break
            if not has_indirect_path:
                G_clusters_red.add_edge(u, v)
                edge_count += 1

print(f"  ✓ Reduction: {G_clusters.number_of_edges()} → {edge_count} edges")

# -----------------------------------------
# 8. Group synchronous clusters
# -----------------------------------------
print("\n🔄 Grouping synchronous clusters...")
synch_groups = []

for a, b in synch_edges:
    if a in G_clusters_red.nodes() and b in G_clusters_red.nodes():
        group_found = False
        for group in synch_groups:
            if a in group or b in group:
                group.add(a)
                group.add(b)
                group_found = True
                break
        if not group_found:
            synch_groups.append({a, b})

print(f"  ✓ {len(synch_groups)} synchronous groups")

# -----------------------------------------
# 9. Formatting functions (NO TEXT, NO BORDERS for UCs)
# -----------------------------------------
def clean_text(text):
    """Sanitize text for DOT output"""
    if not text:
        return ""
    text = text.replace('"', "'")
    text = text.replace('\\', '/')
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def format_uc_label(uc, phase, uc_number=None):
    """Format UC as a colored circle without text or border"""
    bg_color = color_map.get(phase, "#FFFFFF")
    return f'[label="", style=filled, fillcolor="{bg_color}", shape=circle, width=0.4, height=0.4, fixedsize=true, penwidth=0]'

def format_cluster_title(cluster, data):
    """Format cluster title (kept for visual identification)"""
    cluster_clean = clean_text(cluster)
    desc_clean = clean_text(data['description'])
    
    if desc_clean:
        return f'"Secondary link {cluster_clean}\\n{desc_clean}"'
    else:
        return f'"Secondary link {cluster_clean}"'

def escape_dot_string(text):
    """Escape strings for DOT format"""
    if not text:
        return ""
    text = str(text)
    text = text.replace('"', '\\"')
    text = text.replace('\n', ' ')
    return text

# -----------------------------------------
# 10. Generate DOT file
# -----------------------------------------
print("\n📝 Generating DOT file...")
dot_file = "./Harris_toutes_UCs_avec_fleches.dot"

with open(dot_file, "w", encoding="utf-8") as f:
    # Header
    f.write("digraph G {\n")
    f.write('  rankdir=TB;\n')
    f.write('  splines=ortho;\n')
    f.write('  nodesep=0.4;\n')
    f.write('  ranksep=0.8;\n')
    f.write('  compound=true;\n')
    f.write('  newrank=true;\n')
    f.write('  margin="0.2,0.2";\n')
    f.write('  node [shape=circle, fontname="Arial"];\n')
    f.write('  edge [color="#000000", arrowhead=normal, arrowsize=0.5, penwidth=1.0];\n\n')
    
    # Legend
    f.write('  // LEGEND\n')
    f.write('  subgraph cluster_legend {\n')
    f.write('    rank=min;\n')
    f.write('    label="Phases";\n')
    f.write('    fontsize=9;\n')
    f.write('    color=lightgray;\n')
    f.write('    style=filled;\n')
    f.write('    fillcolor="#F9F9F9";\n')
    f.write('    margin=5;\n')
    
    legend_nodes = []
    for i, phase in enumerate(PHASE_ORDER):
        color = color_map.get(phase, "#CCCCCC")
        node_name = f"legend_{i}"
        f.write(f'    "{node_name}" [label="{phase}", style=filled, fillcolor="{color}", shape=box, fontsize=7];\n')
        legend_nodes.append(f'"{node_name}"')
    
    f.write(f'    {{ rank=same; {" ".join(legend_nodes)} }}\n')
    f.write('  }\n\n')
    
    # Dictionaries
    uc_to_nodeid = {}
    ucs_by_cluster = {}
    
    # 1. UCs inside clusters (no text, no border)
    f.write("  // UCS INSIDE CLUSTERS\n")
    for cluster in sorted(G_clusters_red.nodes()):
        data = cluster_data.get(cluster, {'description': '', 'ucs': []})
        ucs_by_cluster[cluster] = []
        
        for uc in sorted(data['ucs']):
            node_id = f"uc_{cluster}_{re.sub(r'[^a-zA-Z0-9]', '_', uc)}"
            uc_to_nodeid[uc] = node_id
            ucs_by_cluster[cluster].append((uc, node_id))
            
            phase = uc_phases.get(uc, "")
            uc_number = uc_numbers.get(uc, "")
            label = format_uc_label(uc, phase, uc_number)
            
            f.write(f'  "{node_id}" {label};\n')
    f.write('\n')
    
    # 2. UCs outside clusters (no text, no border)
    f.write("  // UCS OUTSIDE CLUSTERS\n")
    for uc in sorted(ucs_outside_clusters):
        node_id = f"uc_out_{re.sub(r'[^a-zA-Z0-9]', '_', uc)}"
        uc_to_nodeid[uc] = node_id
        
        phase = uc_phases.get(uc, "")
        uc_number = uc_numbers.get(uc, "")
        label = format_uc_label(uc, phase, uc_number)
        
        f.write(f'  "{node_id}" {label};\n')
    f.write('\n')
    
    # 3. Cluster subgraphs (with thin dashed borders)
    f.write("  // CLUSTERS\n")
    for cluster in sorted(G_clusters_red.nodes()):
        cluster_escaped = escape_dot_string(cluster)
        data = cluster_data.get(cluster, {'description': '', 'ucs': []})
        
        f.write(f'  subgraph "cluster_{cluster_escaped}" {{\n')
        f.write(f'    label={format_cluster_title(cluster, data)};\n')
        f.write(f'    fontsize=9;\n')
        f.write(f'    color=red;\n')
        f.write(f'    style="rounded,dashed";\n')
        f.write(f'    margin=15;\n')
        f.write(f'    penwidth=1;\n')
        f.write(f'    peripheries=1;\n')
        
        if cluster in ucs_by_cluster and ucs_by_cluster[cluster]:
            uc_nodes = [f'"{node_id}"' for (uc, node_id) in ucs_by_cluster[cluster]]
            f.write(f'    {{ rank=same; {" ".join(uc_nodes)} }}\n')
            for uc, node_id in ucs_by_cluster[cluster]:
                f.write(f'    "{node_id}";\n')
        
        f.write(f'  }}\n\n')
    
    # 4. Cluster-to-cluster relationships (invisible for layout)
    f.write("  // CLUSTER-TO-CLUSTER RELATIONSHIPS\n")
    for u, v in G_clusters_red.edges():
        if u in ucs_by_cluster and ucs_by_cluster[u] and v in ucs_by_cluster and ucs_by_cluster[v]:
            source_uc = ucs_by_cluster[u][0][1]
            target_uc = ucs_by_cluster[v][0][1]
            u_escaped = escape_dot_string(u)
            v_escaped = escape_dot_string(v)
            f.write(f'  "{source_uc}" -> "{target_uc}" [ltail="cluster_{u_escaped}", lhead="cluster_{v_escaped}", style="invis", weight=8];\n')
    f.write('\n')
    
    # 5. Synchronous relationships (invisible for layout)
    if synch_edges:
        f.write("  // SYNCHRONOUS RELATIONSHIPS\n")
        for a, b in synch_edges:
            if a in G_clusters_red.nodes() and b in G_clusters_red.nodes() and a in ucs_by_cluster and b in ucs_by_cluster:
                if ucs_by_cluster[a] and ucs_by_cluster[b]:
                    source_uc = ucs_by_cluster[a][0][1]
                    target_uc = ucs_by_cluster[b][0][1]
                    a_escaped = escape_dot_string(a)
                    b_escaped = escape_dot_string(b)
                    f.write(f'  "{source_uc}" -> "{target_uc}" [dir=none, style="invis", constraint=false, ltail="cluster_{a_escaped}", lhead="cluster_{b_escaped}"];\n')
        f.write('\n')
    
    # 6. UC-to-UC relationships
    f.write("  // UC-TO-UC RELATIONSHIPS\n")
    relation_count = 0
    for older, younger in uc_relations:
        if older in uc_to_nodeid and younger in uc_to_nodeid:
            f.write(f'  "{uc_to_nodeid[older]}" -> "{uc_to_nodeid[younger]}" [penwidth=0.6, arrowsize=0.4];\n')
            relation_count += 1
    f.write('\n')
    
    # 7. Rank constraints for UCs outside clusters
    f.write("  // RANK CONSTRAINTS\n")
    
    uc_to_parent_cluster = {}
    for cluster, data in cluster_data.items():
        for uc in data['ucs']:
            uc_to_parent_cluster[uc] = cluster
    
    rank_constraints = set()
    
    for older, younger in uc_relations:
        # Case: older in cluster, younger outside
        if older in uc_to_parent_cluster and younger in uc_to_nodeid and younger not in uc_to_parent_cluster:
            parent_cluster = uc_to_parent_cluster[older]
            if parent_cluster in ucs_by_cluster and ucs_by_cluster[parent_cluster]:
                cluster_node = f'"{ucs_by_cluster[parent_cluster][0][1]}"'
                uc_node = f'"{uc_to_nodeid[younger]}"'
                if (cluster_node, uc_node) not in rank_constraints:
                    f.write(f'  {cluster_node} -> {uc_node} [style="invis", weight=80, minlen=1];\n')
                    rank_constraints.add((cluster_node, uc_node))
        
        # Case: older outside, younger in cluster
        if younger in uc_to_parent_cluster and older in uc_to_nodeid and older not in uc_to_parent_cluster:
            parent_cluster = uc_to_parent_cluster[younger]
            if parent_cluster in ucs_by_cluster and ucs_by_cluster[parent_cluster]:
                cluster_node = f'"{ucs_by_cluster[parent_cluster][0][1]}"'
                uc_node = f'"{uc_to_nodeid[older]}"'
                if (uc_node, cluster_node) not in rank_constraints:
                    f.write(f'  {uc_node} -> {cluster_node} [style="invis", weight=80, minlen=1];\n')
                    rank_constraints.add((uc_node, cluster_node))
    
    f.write('\n')
    
    # 8. Synchronous groups (same rank)
    f.write("  // SYNCHRONOUS GROUPS\n")
    for group in synch_groups:
        if len(group) > 1:
            nodes_in_group = []
            for cluster in group:
                if cluster in ucs_by_cluster and ucs_by_cluster[cluster]:
                    nodes_in_group.append(f'"{ucs_by_cluster[cluster][0][1]}"')
            if nodes_in_group:
                f.write(f'  {{ rank=same; {" ".join(nodes_in_group)} }}\n')
    
    f.write("}\n")

print(f"  ✓ DOT file generated: {dot_file}")
print(f"  ✓ {relation_count} UC relationships added")
print(f"  ✓ {len(rank_constraints)} rank constraints added")

# -----------------------------------------
# 11. Generate PDF and SVG
# -----------------------------------------
print("\n🔍 Checking Graphviz...")

def check_graphviz():
    try:
        result = subprocess.run(["dot", "-V"], capture_output=True, text=True)
        print(f"  ✓ Version: {result.stderr.strip()}")
        return True
    except FileNotFoundError:
        return False

if not check_graphviz():
    print("❌ Graphviz not found!")
    print("   Install Graphviz from: https://graphviz.org/download/")
    input("\nPress Enter to exit...")
    sys.exit(1)

print("\n⚡ GENERATING PDF AND SVG")

pdf_file = "./Harris_phase.pdf"
svg_file = "./Harris_phase.svg"

# Generate PDF
cmd_pdf = ["dot", "-Tpdf", dot_file, "-o", pdf_file]
print(f"\n  Generating PDF...")
print(f"  Command: {' '.join(cmd_pdf)}")

# Generate SVG
cmd_svg = ["dot", "-Tsvg", dot_file, "-o", svg_file]
print(f"\n  Generating SVG...")
print(f"  Command: {' '.join(cmd_svg)}")

success_count = 0

# PDF generation
try:
    start_time = time.time()
    result_pdf = subprocess.run(cmd_pdf, capture_output=True, text=True, timeout=600)
    elapsed = time.time() - start_time
    
    if result_pdf.returncode == 0 and os.path.exists(pdf_file):
        size_kb = os.path.getsize(pdf_file) / 1024
        print(f"\n  ✅ PDF generated successfully!")
        print(f"  ⏱️  Time: {elapsed:.1f} seconds")
        print(f"  📁 PDF: {pdf_file}")
        print(f"  💾 Size: {size_kb:.1f} KB")
        success_count += 1
    else:
        print(f"\n  ❌ PDF failed (code: {result_pdf.returncode})")
        if result_pdf.stderr:
            stderr_lines = result_pdf.stderr.split('\n')[:10]
            print(f"  Error: {' '.join(stderr_lines)}")
            
except subprocess.TimeoutExpired:
    print(f"\n  ⏱️  PDF timeout after 600 seconds")
except Exception as e:
    print(f"❌ PDF ERROR: {e}")

# SVG generation
try:
    start_time = time.time()
    result_svg = subprocess.run(cmd_svg, capture_output=True, text=True, timeout=600)
    elapsed = time.time() - start_time
    
    if result_svg.returncode == 0 and os.path.exists(svg_file):
        size_kb = os.path.getsize(svg_file) / 1024
        print(f"\n  ✅ SVG generated successfully!")
        print(f"  ⏱️  Time: {elapsed:.1f} seconds")
        print(f"  📁 SVG: {svg_file}")
        print(f"  💾 Size: {size_kb:.1f} KB")
        success_count += 1
    else:
        print(f"\n  ❌ SVG failed (code: {result_svg.returncode})")
        if result_svg.stderr:
            stderr_lines = result_svg.stderr.split('\n')[:10]
            print(f"  Error: {' '.join(stderr_lines)}")
            
except subprocess.TimeoutExpired:
    print(f"\n  ⏱️  SVG timeout after 600 seconds")
except Exception as e:
    print(f"❌ SVG ERROR: {e}")

# -----------------------------------------
# 12. Summary
# -----------------------------------------
print("\n" + "="*60)
print("📊 SUMMARY")
print("="*60)
print(f"- Clusters: {len(all_clusters_set)}")
print(f"- Older/younger relationships: {len(edges)}")
print(f"- Synchronous relationships: {len(synch_edges)}")
print(f"- Total UCs: {len(uc_phases)}")
print(f"- UCs in clusters: {len(ucs_in_clusters)}")
print(f"- UCs outside clusters: {len(ucs_outside_clusters)}")
print(f"- UC-to-UC relationships: {len(uc_relations)}")

print("\n📁 Generated files:")
print(f"  - DOT: {dot_file}")
if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
    print(f"  - PDF: {pdf_file}")
if os.path.exists(svg_file) and os.path.getsize(svg_file) > 0:
    print(f"  - SVG: {svg_file}")

print("\n✅ GENERATION COMPLETE")
print("="*60)

if success_count > 0:
    response = input("\n📂 Open PDF? (y/n): ").lower().strip()
    if response in ['y', 'yes', 'o', 'oui']:
        if sys.platform == 'win32':
            os.startfile(pdf_file)
        elif sys.platform == 'darwin':
            subprocess.run(['open', pdf_file])
        else:
            subprocess.run(['xdg-open', pdf_file])

input("\nPress Enter to exit...")