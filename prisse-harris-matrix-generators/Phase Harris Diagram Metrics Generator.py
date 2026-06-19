import csv
import networkx as nx
import subprocess
import os
import sys
import time
import math
import re
import json
from collections import defaultdict, Counter
from datetime import datetime
import traceback
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Matplotlib configuration to avoid font issues
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

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

def main():
    try:
        print("="*60)
        print("HARRIS PHASE DIAGRAM GENERATOR")
        print("WITH STATISTICAL ANALYSIS & VISUALIZATION")
        print("AND UC-CLUSTER INTEGRATION CENTRALITY (CIC)")
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
            print("  ❌ File './noeuds.csv' not found")
            input("\nPress Enter to exit...")
            return
        except Exception as e:
            print(f"  ❌ Error: {e}")
            traceback.print_exc()
            input("\nPress Enter to exit...")
            return

        # -----------------------------------------
        # 2. Read cluster (secondary link) relationships
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
            print("❌ File './relations_clusters.csv' not found!")
            input("\nPress Enter to exit...")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
            input("\nPress Enter to exit...")
            return

        # -----------------------------------------
        # 3. Read cluster descriptions and UCs
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
        except Exception as e:
            print(f"  ⚠️  Error: {e}")

        for cluster in all_clusters_set:
            if cluster not in cluster_data:
                cluster_data[cluster] = {'description': '', 'ucs': []}

        # -----------------------------------------
        # 4. Identify UCs outside clusters
        # -----------------------------------------
        print("\n🔍 Identifying UCs outside clusters...")
        ucs_in_clusters = set()
        for data in cluster_data.values():
            ucs_in_clusters.update(data['ucs'])
        ucs_outside_clusters = set(uc_phases.keys()) - ucs_in_clusters
        print(f"  ✓ UCs in clusters: {len(ucs_in_clusters)}")
        print(f"  ✓ UCs outside clusters: {len(ucs_outside_clusters)}")

        # -----------------------------------------
        # 5. Read UC-to-UC relationships
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
        except Exception as e:
            print(f"  ⚠️  Error: {e}")

        # -----------------------------------------
        # 6. Build cluster graph
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
                return
            else:
                print("  ✓ No cycles detected")
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
            input("\nPress Enter to exit...")
            return

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
        # 7. Group synchronous clusters
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

        # =========================================
        # STATISTICS & VISUALIZATION SECTION
        # =========================================
        
        print("\n" + "="*60)
        print("📊 GENERATING STATISTICS AND VISUALIZATIONS")
        print("="*60)
        
        # Collect metrics
        stats = {
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "general": {},
            "diagram": {},
            "clusters": {},
            "ucs": {},
            "relations": {},
            "topology": {},
            "synchronicity": {},
            "uc_cluster_integration": {}
        }
        
        # General metrics
        stats["general"] = {
            "total_clusters": len(all_clusters_set),
            "clusters_with_relations": G_clusters.number_of_nodes(),
            "total_ucs": len(uc_phases),
            "ucs_in_clusters": len(ucs_in_clusters),
            "ucs_outside_clusters": len(ucs_outside_clusters),
            "coverage_rate": round(len(ucs_in_clusters) / len(uc_phases) * 100, 2) if uc_phases else 0,
            "total_cluster_relations": len(edges),
            "relations_after_reduction": edge_count,
            "reduction_rate": round((1 - edge_count/len(edges)) * 100, 2) if edges else 0,
            "total_uc_relations": len(uc_relations),
            "total_synch_relations": len(synch_edges),
            "total_synch_groups": len(synch_groups)
        }
        
        # Phase distribution
        phase_distribution = Counter(uc_phases.values())
        
        # Compute centrality and topology metrics
        if G_clusters_red.number_of_nodes() > 0:
            in_degrees = dict(G_clusters_red.in_degree())
            out_degrees = dict(G_clusters_red.out_degree())
            degrees = dict(G_clusters_red.degree())
            
            try:
                betweenness = nx.betweenness_centrality(G_clusters_red)
                closeness = nx.closeness_centrality(G_clusters_red)
                pagerank = nx.pagerank(G_clusters_red)
            except:
                betweenness = {n: 0 for n in G_clusters_red.nodes()}
                closeness = {n: 0 for n in G_clusters_red.nodes()}
                pagerank = {n: 0 for n in G_clusters_red.nodes()}
            
            # Topological levels (depth)
            try:
                topological_levels = {}
                for node in nx.topological_sort(G_clusters_red):
                    predecessors = list(G_clusters_red.predecessors(node))
                    if not predecessors:
                        topological_levels[node] = 0
                    else:
                        topological_levels[node] = max(topological_levels[p] for p in predecessors) + 1
            except:
                topological_levels = {n: 0 for n in G_clusters_red.nodes()}
            
            # =========================================
            # DIAGRAM METRICS
            # =========================================
            
            # Maximum depth (longest path length)
            try:
                longest_path_length = 0
                for node in G_clusters_red.nodes():
                    if G_clusters_red.in_degree(node) == 0:
                        for target in G_clusters_red.nodes():
                            if nx.has_path(G_clusters_red, node, target):
                                try:
                                    path_length = nx.shortest_path_length(G_clusters_red, node, target)
                                    longest_path_length = max(longest_path_length, path_length)
                                except:
                                    pass
                max_depth = longest_path_length
            except:
                max_depth = max(topological_levels.values()) if topological_levels else 0
            
            # Maximum width (max nodes at same topological level)
            level_counts = Counter(topological_levels.values())
            max_width = max(level_counts.values()) if level_counts else 0
            level_with_max_width = max(level_counts.items(), key=lambda x: x[1])[0] if level_counts else 0
            
            # Undirected graph diameter
            undirected = G_clusters_red.to_undirected()
            try:
                if nx.is_connected(undirected):
                    diameter = nx.diameter(undirected)
                    radius = nx.radius(undirected)
                else:
                    components = list(nx.connected_components(undirected))
                    largest_comp = max(components, key=len)
                    subgraph = undirected.subgraph(largest_comp)
                    diameter = nx.diameter(subgraph)
                    radius = nx.radius(subgraph)
            except:
                diameter = 0
                radius = 0
            
            # Graph center
            try:
                center_nodes = list(nx.center(undirected))
            except:
                center_nodes = []
            
            # Average eccentricity
            try:
                eccentricities = nx.eccentricity(undirected)
                avg_eccentricity = round(sum(eccentricities.values()) / len(eccentricities), 3) if eccentricities else 0
                max_eccentricity = max(eccentricities.values()) if eccentricities else 0
                min_eccentricity = min(eccentricities.values()) if eccentricities else 0
            except:
                avg_eccentricity = 0
                max_eccentricity = 0
                min_eccentricity = 0
            
            # Graph density
            n = G_clusters_red.number_of_nodes()
            density = round(edge_count / (n * (n-1)) if n > 1 else 0, 6)
            
            # Average degree
            avg_degree = round(sum(degrees.values()) / n, 2) if n > 0 else 0
            
            # Freeman centralization
            try:
                max_betweenness = max(betweenness.values()) if betweenness else 0
                betweenness_centralization = sum(betweenness.values()) / ((n-1) * max_betweenness) if n > 1 and max_betweenness > 0 else 0
            except:
                betweenness_centralization = 0
            
            # Level distribution
            level_distribution = {int(k): v for k, v in level_counts.items()}
            
            stats["diagram"] = {
                "max_depth": max_depth,
                "min_depth": min(topological_levels.values()) if topological_levels else 0,
                "max_width": max_width,
                "level_of_max_width": level_with_max_width,
                "number_of_levels": len(level_counts),
                "level_distribution": level_distribution,
                "diameter": diameter,
                "radius": radius,
                "graph_center": center_nodes[:10] if center_nodes else [],
                "avg_eccentricity": avg_eccentricity,
                "max_eccentricity": max_eccentricity,
                "min_eccentricity": min_eccentricity,
                "graph_density": density,
                "avg_degree": avg_degree,
                "betweenness_centralization": round(betweenness_centralization, 6)
            }
            
            # =========================================
            # PER-CLUSTER STATISTICS
            # =========================================
            
            for cluster in all_clusters_set:
                data = cluster_data.get(cluster, {'description': '', 'ucs': []})
                ucs_list = data['ucs']
                phases_in_cluster = [uc_phases.get(uc, "") for uc in ucs_list if uc in uc_phases]
                phase_counts = Counter(phases_in_cluster)
                
                stats["clusters"][cluster] = {
                    "description": data['description'],
                    "nb_ucs": len(ucs_list),
                    "dominant_phase": phase_counts.most_common(1)[0][0] if phase_counts else "",
                    "phase_diversity": len(phase_counts),
                    "in_degree": in_degrees.get(cluster, 0),
                    "out_degree": out_degrees.get(cluster, 0),
                    "total_degree": degrees.get(cluster, 0),
                    "betweenness_centrality": round(betweenness.get(cluster, 0), 6),
                    "closeness_centrality": round(closeness.get(cluster, 0), 6),
                    "pagerank": round(pagerank.get(cluster, 0), 6),
                    "topological_level": topological_levels.get(cluster, -1),
                    "is_source": G_clusters_red.in_degree(cluster) == 0,
                    "is_sink": G_clusters_red.out_degree(cluster) == 0,
                    "has_synch_relations": any(cluster in group for group in synch_groups)
                }
            
            # =========================================
            # UC-CLUSTER INTEGRATION CENTRALITY (CIC)
            # =========================================
            
            print("\n🔗 Computing UC-Cluster Integration Centrality (CIC)...")
            
            # Build UC -> cluster mapping
            cluster_to_uc = {}
            for cluster, data in cluster_data.items():
                for uc in data['ucs']:
                    cluster_to_uc[uc] = cluster
            
            # Count external UC relationships with each cluster
            external_in_flux = defaultdict(int)   # External UC → cluster
            external_out_flux = defaultdict(int)  # Cluster → external UC
            
            for older, younger in uc_relations:
                older_cluster = cluster_to_uc.get(older)
                younger_cluster = cluster_to_uc.get(younger)
                
                older_external = older not in ucs_in_clusters
                younger_external = younger not in ucs_in_clusters
                
                # Case: external UC → UC inside cluster
                if older_external and younger_cluster:
                    external_in_flux[younger_cluster] += 1
                
                # Case: UC inside cluster → external UC
                if older_cluster and younger_external:
                    external_out_flux[older_cluster] += 1
            
            # Normalize values (min-max scaling for each component)
            all_nb_ucs = [data['nb_ucs'] for data in stats['clusters'].values()]
            all_pagerank = [data['pagerank'] for data in stats['clusters'].values()]
            all_flux_in = list(external_in_flux.values()) if external_in_flux else [0]
            all_flux_out = list(external_out_flux.values()) if external_out_flux else [0]
            
            max_nb_ucs = max(all_nb_ucs) if all_nb_ucs else 1
            max_pagerank = max(all_pagerank) if all_pagerank else 1
            max_flux_in = max(all_flux_in) if all_flux_in else 1
            max_flux_out = max(all_flux_out) if all_flux_out else 1
            
            # Weights (adjustable)
            weight_size = 0.35
            weight_pagerank = 0.35
            weight_flux_in = 0.15
            weight_flux_out = 0.15
            
            cic_scores = {}
            
            for cluster, data in stats['clusters'].items():
                # Component 1: Normalized internal size
                size_norm = data['nb_ucs'] / max_nb_ucs if max_nb_ucs > 0 else 0
                
                # Component 2: Normalized PageRank (importance in cluster graph)
                pagerank_norm = data['pagerank'] / max_pagerank if max_pagerank > 0 else 0
                
                # Component 3: Normalized external incoming flux
                flux_in_norm = external_in_flux.get(cluster, 0) / max_flux_in if max_flux_in > 0 else 0
                
                # Component 4: Normalized external outgoing flux
                flux_out_norm = external_out_flux.get(cluster, 0) / max_flux_out if max_flux_out > 0 else 0
                
                # CIC score (between 0 and 1)
                cic = (weight_size * size_norm + 
                       weight_pagerank * pagerank_norm + 
                       weight_flux_in * flux_in_norm + 
                       weight_flux_out * flux_out_norm)
                
                cic_scores[cluster] = round(cic, 6)
                
                # Add to cluster stats
                stats['clusters'][cluster]['cic_score'] = cic_scores[cluster]
                stats['clusters'][cluster]['external_in_flux'] = external_in_flux.get(cluster, 0)
                stats['clusters'][cluster]['external_out_flux'] = external_out_flux.get(cluster, 0)
            
            # Global CIC statistics
            stats['uc_cluster_integration'] = {
                'cic_mean': round(sum(cic_scores.values()) / len(cic_scores), 6) if cic_scores else 0,
                'cic_max': max(cic_scores.values()) if cic_scores else 0,
                'cic_min': min(cic_scores.values()) if cic_scores else 0,
                'top_10_cic': sorted(cic_scores.items(), key=lambda x: x[1], reverse=True)[:10],
                'weight_size': weight_size,
                'weight_pagerank': weight_pagerank,
                'weight_flux_in': weight_flux_in,
                'weight_flux_out': weight_flux_out
            }
            
            print(f"  ✓ CIC computed for {len(cic_scores)} clusters")
            print(f"  ✓ CIC mean: {stats['uc_cluster_integration']['cic_mean']:.4f}")
            print(f"  ✓ CIC max: {stats['uc_cluster_integration']['cic_max']:.4f}")
            
            # Topology
            components = list(nx.connected_components(undirected))
            source_nodes = [n for n in G_clusters_red.nodes() if G_clusters_red.in_degree(n) == 0]
            sink_nodes = [n for n in G_clusters_red.nodes() if G_clusters_red.out_degree(n) == 0]
            
            stats["topology"] = {
                "connected_components": len(components),
                "largest_component_size": max(len(c) for c in components) if components else 0,
                "source_clusters": source_nodes,
                "nb_sources": len(source_nodes),
                "sink_clusters": sink_nodes,
                "nb_sinks": len(sink_nodes)
            }
        
        # Cross-relations analysis
        cluster_to_uc = {}
        for cluster, data in cluster_data.items():
            for uc in data['ucs']:
                cluster_to_uc[uc] = cluster
        
        intra_relations = 0
        inter_relations = 0
        outgoing_relations = 0
        incoming_relations = 0
        
        for older, younger in uc_relations:
            older_cluster = cluster_to_uc.get(older)
            younger_cluster = cluster_to_uc.get(younger)
            
            if older_cluster and younger_cluster:
                if older_cluster == younger_cluster:
                    intra_relations += 1
                else:
                    inter_relations += 1
            elif older_cluster and not younger_cluster:
                outgoing_relations += 1
            elif not older_cluster and younger_cluster:
                incoming_relations += 1
        
        stats["relations"] = {
            "intra_cluster": intra_relations,
            "inter_cluster": inter_relations,
            "cluster_to_external": outgoing_relations,
            "external_to_cluster": incoming_relations,
            "cross_relation_percentage": round(inter_relations / len(uc_relations) * 100, 2) if uc_relations else 0
        }
        
        # Synchronicity
        synch_clusters = set()
        for group in synch_groups:
            synch_clusters.update(group)
        
        stats["synchronicity"] = {
            "nb_synch_relations": len(synch_edges),
            "nb_synch_groups": len(synch_groups),
            "clusters_involved": len(synch_clusters),
            "avg_group_size": round(sum(len(g) for g in synch_groups) / len(synch_groups), 2) if synch_groups else 0
        }
        
        # =========================================
        # GENERATE TEXT REPORT
        # =========================================
        
        print("\n📝 Generating statistical report...")
        
        report_file = "./HARRIS_STATISTICAL_REPORT.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("HARRIS PHASE DIAGRAM - STATISTICAL REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {stats['generation_date']}\n")
            f.write("="*80 + "\n\n")
            
            # 1. GENERAL SUMMARY
            f.write("1. GENERAL SUMMARY\n")
            f.write("-"*60 + "\n")
            f.write(f"   Total clusters: {stats['general']['total_clusters']}\n")
            f.write(f"   Clusters with relations: {stats['general']['clusters_with_relations']}\n")
            f.write(f"   Total UCs: {stats['general']['total_ucs']}\n")
            f.write(f"   UCs integrated in clusters: {stats['general']['ucs_in_clusters']} ({stats['general']['coverage_rate']}%)\n")
            f.write(f"   UCs outside clusters: {stats['general']['ucs_outside_clusters']}\n")
            f.write(f"   Cluster relations: {stats['general']['total_cluster_relations']}\n")
            f.write(f"   Relations after transitive reduction: {stats['general']['relations_after_reduction']}\n")
            f.write(f"   Reduction rate: {stats['general']['reduction_rate']}%\n")
            f.write(f"   UC relations: {stats['general']['total_uc_relations']}\n")
            f.write(f"   Synchronous relations: {stats['general']['total_synch_relations']}\n")
            f.write(f"   Synchronous groups: {stats['general']['total_synch_groups']}\n\n")
            
            # 2. DIAGRAM METRICS
            f.write("2. DIAGRAM METRICS\n")
            f.write("-"*60 + "\n")
            f.write(f"\n   📏 DEPTH & WIDTH:\n")
            f.write(f"      Maximum depth (longest path): {stats['diagram'].get('max_depth', 0)}\n")
            f.write(f"      Minimum depth: {stats['diagram'].get('min_depth', 0)}\n")
            f.write(f"      Maximum width: {stats['diagram'].get('max_width', 0)}\n")
            f.write(f"      Level with max width: {stats['diagram'].get('level_of_max_width', 0)}\n")
            f.write(f"      Total topological levels: {stats['diagram'].get('number_of_levels', 0)}\n")
            
            f.write(f"\n   🎯 DIAMETER & RADIUS:\n")
            f.write(f"      Graph diameter: {stats['diagram'].get('diameter', 0)}\n")
            f.write(f"      Graph radius: {stats['diagram'].get('radius', 0)}\n")
            f.write(f"      Average eccentricity: {stats['diagram'].get('avg_eccentricity', 0)}\n")
            f.write(f"      Max eccentricity: {stats['diagram'].get('max_eccentricity', 0)}\n")
            f.write(f"      Min eccentricity: {stats['diagram'].get('min_eccentricity', 0)}\n")
            
            f.write(f"\n   📊 DENSITY & DEGREES:\n")
            f.write(f"      Graph density: {stats['diagram'].get('graph_density', 0):.6f}\n")
            f.write(f"      Average node degree: {stats['diagram'].get('avg_degree', 0)}\n")
            f.write(f"      Betweenness centralization: {stats['diagram'].get('betweenness_centralization', 0):.6f}\n")
            
            if stats['diagram'].get('graph_center'):
                f.write(f"\n   🎯 Graph center:\n")
                for centre in stats['diagram']['graph_center'][:10]:
                    f.write(f"      - Cluster {centre}\n")
            
            f.write(f"\n   📈 Topological level distribution:\n")
            level_dist = stats['diagram'].get('level_distribution', {})
            for level, count in sorted(level_dist.items()):
                bar = "█" * min(int(count / max(level_dist.values()) * 40), 40) if level_dist else ""
                f.write(f"      Level {level:>2} : {count:>3} clusters {bar}\n")
            
            # 3. PHASE DISTRIBUTION
            f.write("\n3. PHASE DISTRIBUTION IN UCs\n")
            f.write("-"*60 + "\n")
            for phase, count in sorted(phase_distribution.items(), key=lambda x: x[1], reverse=True):
                pct = round(count / len(uc_phases) * 100, 1)
                bar = "█" * int(pct / 2)
                f.write(f"   Phase {phase:>4} : {count:>4} UCs ({pct:>5.1f}%) {bar}\n")
            f.write("\n")
            
            # 4. GRAPH TOPOLOGY
            f.write("4. CLUSTER GRAPH TOPOLOGY\n")
            f.write("-"*60 + "\n")
            f.write(f"   Connected components: {stats['topology'].get('connected_components', 0)}\n")
            f.write(f"   Largest component size: {stats['topology'].get('largest_component_size', 0)}\n")
            f.write(f"   Source clusters: {stats['topology'].get('nb_sources', 0)}\n")
            f.write(f"   Sink clusters: {stats['topology'].get('nb_sinks', 0)}\n\n")
            
            # 5. PER-CLUSTER STATISTICS
            f.write("5. PER-CLUSTER STATISTICS\n")
            f.write("-"*60 + "\n")
            
            # Top 10 clusters by number of UCs
            f.write("\n   🔹 Top 10 clusters by UC count:\n")
            top_by_ucs = sorted(stats["clusters"].items(), key=lambda x: x[1]["nb_ucs"], reverse=True)[:10]
            for i, (cluster, data) in enumerate(top_by_ucs, 1):
                f.write(f"      {i:2}. Cluster {cluster} : {data['nb_ucs']} UCs (dominant phase: {data['dominant_phase']})\n")
            
            # Top 10 clusters by total degree
            f.write("\n   🔹 Top 10 clusters by degree:\n")
            top_by_degree = sorted(stats["clusters"].items(), key=lambda x: x[1]["total_degree"], reverse=True)[:10]
            for i, (cluster, data) in enumerate(top_by_degree, 1):
                f.write(f"      {i:2}. Cluster {cluster} : total degree={data['total_degree']} (in={data['in_degree']}, out={data['out_degree']})\n")
            
            # Top 10 clusters by PageRank
            f.write("\n   🔹 Top 10 clusters by PageRank:\n")
            top_by_pagerank = sorted(stats["clusters"].items(), key=lambda x: x[1]["pagerank"], reverse=True)[:10]
            for i, (cluster, data) in enumerate(top_by_pagerank, 1):
                f.write(f"      {i:2}. Cluster {cluster} : PageRank={data['pagerank']:.6f}\n")
            
            # 6. UC-CLUSTER RELATIONS
            f.write("\n6. UC-CLUSTER RELATIONS\n")
            f.write("-"*60 + "\n")
            f.write(f"   Intra-cluster relations: {stats['relations']['intra_cluster']}\n")
            f.write(f"   Inter-cluster relations: {stats['relations']['inter_cluster']}\n")
            f.write(f"   Cluster → External relations: {stats['relations']['cluster_to_external']}\n")
            f.write(f"   External → Cluster relations: {stats['relations']['external_to_cluster']}\n")
            f.write(f"   Cross-relation percentage: {stats['relations']['cross_relation_percentage']}%\n\n")
            
            # 7. SYNCHRONICITY
            f.write("7. SYNCHRONOUS RELATIONS\n")
            f.write("-"*60 + "\n")
            f.write(f"   Number of synchronous relations: {stats['synchronicity']['nb_synch_relations']}\n")
            f.write(f"   Number of synchronous groups: {stats['synchronicity']['nb_synch_groups']}\n")
            f.write(f"   Clusters involved: {stats['synchronicity']['clusters_involved']}\n")
            f.write(f"   Average group size: {stats['synchronicity']['avg_group_size']}\n\n")
            
            # 8. UC-CLUSTER INTEGRATION CENTRALITY (CIC)
            if stats['uc_cluster_integration']:
                f.write("8. UC-CLUSTER INTEGRATION CENTRALITY (CIC)\n")
                f.write("-"*60 + "\n")
                f.write(f"   CIC measures the systemic importance of a cluster by combining\n")
                f.write(f"   its internal size, PageRank, and external UC connections.\n\n")
                f.write(f"   Weights used:\n")
                f.write(f"      - Internal size: {stats['uc_cluster_integration']['weight_size']*100:.0f}%\n")
                f.write(f"      - PageRank: {stats['uc_cluster_integration']['weight_pagerank']*100:.0f}%\n")
                f.write(f"      - External incoming flux: {stats['uc_cluster_integration']['weight_flux_in']*100:.0f}%\n")
                f.write(f"      - External outgoing flux: {stats['uc_cluster_integration']['weight_flux_out']*100:.0f}%\n\n")
                f.write(f"   Global CIC statistics:\n")
                f.write(f"      Mean: {stats['uc_cluster_integration']['cic_mean']:.4f}\n")
                f.write(f"      Maximum: {stats['uc_cluster_integration']['cic_max']:.4f}\n")
                f.write(f"      Minimum: {stats['uc_cluster_integration']['cic_min']:.4f}\n\n")
                f.write(f"   🔹 Top 10 clusters by CIC:\n")
                for i, (cluster, score) in enumerate(stats['uc_cluster_integration']['top_10_cic'], 1):
                    data = stats['clusters'][cluster]
                    f.write(f"      {i:2}. Cluster {cluster} : CIC={score:.4f} "
                           f"(size={data['nb_ucs']}, PR={data['pagerank']:.4f}, "
                           f"ext_in={data['external_in_flux']}, ext_out={data['external_out_flux']})\n")
                f.write("\n")
            
            # 9. SOURCE AND SINK CLUSTERS
            f.write("9. SOURCE AND SINK CLUSTERS\n")
            f.write("-"*60 + "\n")
            sources = stats['topology'].get('source_clusters', [])
            sinks = stats['topology'].get('sink_clusters', [])
            f.write(f"   Sources ({len(sources)}) :\n")
            for s in sources[:15]:
                f.write(f"      - Cluster {s}\n")
            if len(sources) > 15:
                f.write(f"      ... and {len(sources)-15} more\n")
            f.write(f"\n   Sinks ({len(sinks)}) :\n")
            for s in sinks[:15]:
                f.write(f"      - Cluster {s}\n")
            if len(sinks) > 15:
                f.write(f"      ... and {len(sinks)-15} more\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
        
        print(f"  ✓ Report generated: {report_file}")
        
        # =========================================
        # GENERATE VISUALIZATIONS
        # =========================================
        
        print("\n📊 Generating statistical charts...")
        
        # Create figure with multiple subplots (3x3 grid including CIC)
        fig = plt.figure(figsize=(21, 16))
        fig.suptitle('HARRIS PHASE DIAGRAM - STATISTICAL ANALYSIS', fontsize=16, fontweight='bold')
        
        # Chart 1: Phase distribution (donut chart)
        ax1 = fig.add_subplot(3, 3, 1)
        phases = list(phase_distribution.keys())
        counts = list(phase_distribution.values())
        colors_phases = [color_map.get(p, "#CCCCCC") for p in phases]
        
        if phases:
            wedges, texts, autotexts = ax1.pie(counts, labels=phases, colors=colors_phases, 
                                                autopct='%1.1f%%', startangle=90, pctdistance=0.85)
            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            ax1.add_artist(centre_circle)
            ax1.set_title('Phase Distribution in UCs', fontsize=11, fontweight='bold')
        
        # Chart 2: Topological level distribution (width)
        ax2 = fig.add_subplot(3, 3, 2)
        if level_dist:
            levels = sorted(level_dist.keys())
            widths = [level_dist[l] for l in levels]
            ax2.bar(levels, widths, color='steelblue', edgecolor='black', alpha=0.7)
            ax2.set_xlabel('Topological Level')
            ax2.set_ylabel('Number of Clusters')
            ax2.set_title('Topological Level Distribution\n(Diagram Width)', fontsize=11, fontweight='bold')
            ax2.grid(axis='y', alpha=0.3)
            for i, v in enumerate(widths):
                ax2.text(levels[i], v + 0.5, str(v), ha='center', fontsize=8)
        
        # Chart 3: Cluster size histogram
        ax3 = fig.add_subplot(3, 3, 3)
        sizes = [data['nb_ucs'] for data in stats['clusters'].values()]
        if sizes:
            ax3.hist(sizes, bins=20, color='coral', edgecolor='black', alpha=0.7)
            ax3.set_xlabel('Number of UCs per Cluster')
            ax3.set_ylabel('Number of Clusters')
            ax3.set_title('Cluster Size Distribution', fontsize=11, fontweight='bold')
            ax3.axvline(np.mean(sizes), color='red', linestyle='dashed', linewidth=2, label=f'Mean: {np.mean(sizes):.1f}')
            ax3.axvline(np.median(sizes), color='green', linestyle='dashed', linewidth=2, label=f'Median: {np.median(sizes):.1f}')
            ax3.legend()
        
        # Chart 4: Degree distribution
        ax4 = fig.add_subplot(3, 3, 4)
        degrees = [data['total_degree'] for data in stats['clusters'].values()]
        if degrees:
            ax4.hist(degrees, bins=20, color='teal', edgecolor='black', alpha=0.7)
            ax4.set_xlabel('Total Degree (in + out)')
            ax4.set_ylabel('Number of Clusters')
            ax4.set_title('Cluster Degree Distribution', fontsize=11, fontweight='bold')
            ax4.axvline(np.mean(degrees), color='red', linestyle='dashed', linewidth=2, label=f'Mean: {np.mean(degrees):.1f}')
            ax4.legend()
        
        # Chart 5: Top 15 clusters by PageRank
        ax5 = fig.add_subplot(3, 3, 5)
        top_pr = sorted(stats['clusters'].items(), key=lambda x: x[1]['pagerank'], reverse=True)[:15]
        if top_pr:
            names_pr = [f"C{cluster}" for cluster, _ in top_pr]
            values_pr = [data['pagerank'] for _, data in top_pr]
            ax5.barh(range(len(names_pr)), values_pr, color='forestgreen', alpha=0.7)
            ax5.set_yticks(range(len(names_pr)))
            ax5.set_yticklabels(names_pr, fontsize=7)
            ax5.set_xlabel('PageRank')
            ax5.set_title('Top 15 Clusters by Importance (PageRank)', fontsize=11, fontweight='bold')
            ax5.invert_yaxis()
        
        # Chart 6: Source/Sink/Intermediate breakdown
        ax6 = fig.add_subplot(3, 3, 6)
        nb_sources = stats['topology'].get('nb_sources', 0)
        nb_sinks = stats['topology'].get('nb_sinks', 0)
        nb_intermediate = stats['general']['clusters_with_relations'] - nb_sources - nb_sinks
        categories = ['Sources', 'Intermediate', 'Sinks']
        values = [nb_sources, nb_intermediate, nb_sinks]
        colors = ['#2E8B57', '#4682B4', '#CD853F']
        ax6.bar(categories, values, color=colors, edgecolor='black', alpha=0.7)
        ax6.set_ylabel('Number of Clusters')
        ax6.set_title('Topological Role Distribution', fontsize=11, fontweight='bold')
        for i, v in enumerate(values):
            ax6.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
        
        # Chart 7: Cross-relations pie chart
        ax7 = fig.add_subplot(3, 3, 7)
        intra = stats['relations']['intra_cluster']
        inter = stats['relations']['inter_cluster']
        to_ext = stats['relations']['cluster_to_external']
        from_ext = stats['relations']['external_to_cluster']
        labels = ['Intra-cluster', 'Inter-cluster', 'Cluster→Ext.', 'Ext.→Cluster']
        sizes = [intra, inter, to_ext, from_ext]
        colors_rel = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
        if sum(sizes) > 0:
            ax7.pie(sizes, labels=labels, colors=colors_rel, autopct='%1.1f%%', startangle=90)
            ax7.set_title('UC Relation Breakdown', fontsize=11, fontweight='bold')
        
        # Chart 8: Key diagram metrics
        ax8 = fig.add_subplot(3, 3, 8)
        if level_dist:
            max_depth = stats['diagram'].get('max_depth', 0)
            max_width = stats['diagram'].get('max_width', 0)
            nb_levels = stats['diagram'].get('number_of_levels', 0)
            
            metrics_names = ['Max\nDepth', 'Max\nWidth', 'Nb\nLevels', 'Diameter', 'Radius']
            metrics_values = [max_depth, max_width, nb_levels, 
                             stats['diagram'].get('diameter', 0), 
                             stats['diagram'].get('radius', 0)]
            colors_metrics = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            bars = ax8.bar(metrics_names, metrics_values, color=colors_metrics, edgecolor='black', alpha=0.7)
            ax8.set_ylabel('Value')
            ax8.set_title('Key Diagram Metrics', fontsize=11, fontweight='bold')
            for bar, val in zip(bars, metrics_values):
                ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                        str(val), ha='center', fontweight='bold', fontsize=9)
        
        # Chart 9: Top 15 CIC scores
        ax9 = fig.add_subplot(3, 3, 9)
        if cic_scores:
            top_cic = sorted(cic_scores.items(), key=lambda x: x[1], reverse=True)[:15]
            names_cic = [f"C{cluster}" for cluster, _ in top_cic]
            values_cic = [score for _, score in top_cic]
            ax9.barh(range(len(names_cic)), values_cic, color='darkorchid', alpha=0.7)
            ax9.set_yticks(range(len(names_cic)))
            ax9.set_yticklabels(names_cic, fontsize=7)
            ax9.set_xlabel('CIC Score')
            ax9.set_title('Top 15 Clusters by CIC', fontsize=11, fontweight='bold')
            ax9.invert_yaxis()
            ax9.set_xlim(0, 1)
        
        plt.tight_layout()
        chart_file = "./HARRIS_STATISTICAL_CHARTS.png"
        plt.savefig(chart_file, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"  ✓ Summary chart generated: {chart_file}")
        plt.close()
        
        # Supplementary chart: Phase distribution pie
        fig2, ax = plt.subplots(figsize=(10, 8))
        if phases:
            wedges, texts, autotexts = ax.pie(counts, labels=phases, colors=colors_phases, 
                                                autopct='%1.1f%%', startangle=90)
            ax.set_title('Detailed Phase Distribution in UCs', fontsize=14, fontweight='bold')
            chart2_file = "./HARRIS_PHASE_DISTRIBUTION.png"
            plt.savefig(chart2_file, dpi=150, bbox_inches='tight', facecolor='white')
            print(f"  ✓ Phase chart: {chart2_file}")
            plt.close()
        
        # Supplementary chart: CIC distribution histogram
        if cic_scores:
            fig3, ax = plt.subplots(figsize=(10, 6))
            cic_values = list(cic_scores.values())
            ax.hist(cic_values, bins=20, color='darkorchid', edgecolor='black', alpha=0.7)
            ax.set_xlabel('CIC Score')
            ax.set_ylabel('Number of Clusters')
            ax.set_title('UC-Cluster Integration Centrality (CIC) Distribution', fontsize=12, fontweight='bold')
            ax.axvline(np.mean(cic_values), color='red', linestyle='dashed', linewidth=2, label=f'Mean: {np.mean(cic_values):.3f}')
            ax.axvline(np.median(cic_values), color='green', linestyle='dashed', linewidth=2, label=f'Median: {np.median(cic_values):.3f}')
            ax.legend()
            chart3_file = "./HARRIS_CIC_DISTRIBUTION.png"
            plt.savefig(chart3_file, dpi=150, bbox_inches='tight', facecolor='white')
            print(f"  ✓ CIC distribution chart: {chart3_file}")
            plt.close()
        
        # Export CSV of cluster metrics
        csv_file = "./CLUSTER_METRICS.csv"
        with open(csv_file, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Cluster", "Description", "Nb_UCs", "Dominant_Phase", "Phase_Diversity",
                "In_Degree", "Out_Degree", "Total_Degree", "Betweenness_Centrality",
                "Closeness_Centrality", "PageRank", "Topological_Level", "Is_Source", "Is_Sink", 
                "Has_Synch_Relations", "External_In_Flux", "External_Out_Flux", "CIC_Score"
            ])
            
            for cluster, data in sorted(stats["clusters"].items()):
                writer.writerow([
                    cluster, data.get("description", ""), data.get("nb_ucs", 0),
                    data.get("dominant_phase", ""), data.get("phase_diversity", 0),
                    data.get("in_degree", 0), data.get("out_degree", 0),
                    data.get("total_degree", 0), data.get("betweenness_centrality", 0),
                    data.get("closeness_centrality", 0), data.get("pagerank", 0),
                    data.get("topological_level", -1), data.get("is_source", False),
                    data.get("is_sink", False), data.get("has_synch_relations", False),
                    data.get("external_in_flux", 0), data.get("external_out_flux", 0),
                    data.get("cic_score", 0)
                ])
        print(f"  ✓ Cluster metrics CSV: {csv_file}")
        
        # Export CSV of diagram metrics
        diag_csv = "./DIAGRAM_METRICS.csv"
        with open(diag_csv, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for key, value in stats["diagram"].items():
                if key not in ["level_distribution", "graph_center"]:
                    writer.writerow([key.replace("_", " ").title(), value])
                elif key == "graph_center" and value:
                    writer.writerow(["Graph Center", ", ".join(value)])
        print(f"  ✓ Diagram metrics CSV: {diag_csv}")
        
        # Export CSV of CIC metrics
        if cic_scores:
            cic_csv = "./CIC_METRICS.csv"
            with open(cic_csv, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Cluster", "CIC_Score", "Internal_Size", "PageRank", 
                               "External_In_Flux", "External_Out_Flux"])
                for cluster, score in sorted(cic_scores.items(), key=lambda x: x[1], reverse=True):
                    data = stats['clusters'][cluster]
                    writer.writerow([
                        cluster, score, data['nb_ucs'], data['pagerank'],
                        data.get('external_in_flux', 0), data.get('external_out_flux', 0)
                    ])
            print(f"  ✓ CIC metrics CSV: {cic_csv}")
        
        # =========================================
        # SUMMARY DISPLAY
        # =========================================
        
        print("\n" + "="*60)
        print("📊 DIAGRAM METRICS SUMMARY")
        print("="*60)
        print(f"   📏 Maximum depth: {stats['diagram'].get('max_depth', 0)}")
        print(f"   📐 Maximum width: {stats['diagram'].get('max_width', 0)}")
        print(f"   🎯 Diameter: {stats['diagram'].get('diameter', 0)}")
        print(f"   ⭕ Radius: {stats['diagram'].get('radius', 0)}")
        print(f"   📊 Density: {stats['diagram'].get('graph_density', 0):.6f}")
        print(f"   📈 Average degree: {stats['diagram'].get('avg_degree', 0)}")
        
        if cic_scores:
            print(f"\n   🔗 CIC mean: {stats['uc_cluster_integration']['cic_mean']:.4f}")
            print(f"   🔗 CIC max: {stats['uc_cluster_integration']['cic_max']:.4f}")
            print(f"   🔗 Top CIC: {stats['uc_cluster_integration']['top_10_cic'][0][0]} ({stats['uc_cluster_integration']['top_10_cic'][0][1]:.4f})")
        
        print("\n" + "="*60)
        print("📁 GENERATED FILES")
        print("="*60)
        print(f"   📄 Text report       : {report_file}")
        print(f"   📊 Summary chart     : {chart_file}")
        print(f"   📊 Phase chart       : {chart2_file}")
        if cic_scores:
            print(f"   📊 CIC chart         : {chart3_file}")
        print(f"   📁 Cluster CSV       : {csv_file}")
        print(f"   📁 Diagram CSV       : {diag_csv}")
        if cic_scores:
            print(f"   📁 CIC CSV           : {cic_csv}")
        
        print("\n" + "="*60)
        print("✅ GENERATION COMPLETE")
        print("="*60)
        
        # Option to open report
        response = input("\n📂 Open report? (y/n): ").lower().strip()
        if response in ['y', 'yes', 'o', 'oui']:
            if sys.platform == 'win32':
                os.startfile(report_file)
            elif sys.platform == 'darwin':
                subprocess.run(['open', report_file])
            else:
                subprocess.run(['xdg-open', report_file])
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ CRITICAL ERROR")
        print("="*60)
        print(f"Error: {e}")
        print("\nError details:")
        traceback.print_exc()
        print("\n" + "="*60)
    
    finally:
        print("\nPress Enter to exit...")
        input()

if __name__ == "__main__":
    main()