#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bibliometric_engine.py — VOSviewer/Bibliometrix Science Mapping & Network Analysis Engine
AcademicSuite Skill #24: bibliometric-network-analyst
=======================================================================================
Conducts automated bibliometric science mapping, keyword co-occurrence analysis,
co-authorship networks, Bradford's Law journal scattering, Lotka's Law author productivity,
NetworkX centrality modeling (Degree, Betweenness, Closeness), and Callon's 4-Quadrant
Strategic Diagram (Motor, Niche, Emerging/Declining, Basic Themes).

Exports:
  1. VOSviewer Native Files: `vosviewer_map.txt` & `vosviewer_network.txt`.
  2. Dual 300-DPI Publication Visual Plots: `bibliometric_network_map.png` & `thematic_strategic_map.png`.
  3. 5-Sheet Excel Workbook: `bibliometric_matrix.xlsx`.
  4. Publication-Ready Chapter 2 Word Report: `گزارش_تحلیل_علم‌سنجی_و_ترسیم_نقشه_دانش.docx` / `Bibliometric_Science_Mapping_Report.docx`.
  5. Machine-Readable JSON Ledger: `bibliometric_summary.json`.
"""

import os
import sys
import json
import csv
import math
import argparse
from datetime import datetime
from collections import Counter, defaultdict

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


# ==============================================================================
# OpenXML BiDi & Typography Helpers
# ==============================================================================

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set custom internal padding for Word table cell (in dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_shading(cell, color_hex):
    """Set background hex shading for Word table cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def make_table_apa7(table, is_bidi=True):
    """Format Word table according to strict APA 7th Edition rules (borderless sides, horizontal rules)."""
    tblPr = table._tbl.tblPr
    if is_bidi:
        bidi_visual = parse_xml(f'<w:bidiVisual {nsdecls("w")}/>')
        tblPr.append(bidi_visual)
    
    table_borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="1A365D"/>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="1A365D"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(table_borders)


def format_cell_text(cell, text, bold=False, italic=False, size_pt=10, color_rgb=(40,40,40),
                     align=WD_ALIGN_PARAGRAPH.CENTER, font_fa="B Nazanin", font_en="Times New Roman", is_bidi=True):
    """Format run text inside table cell with exact bidirectional font bindings."""
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    if is_bidi:
        pPr = p._element.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
    
    run = p.add_run(str(text))
    run.font.name = font_en
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._element.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_en}" w:hAnsi="{font_en}" w:cs="{font_fa}"/>')
    rPr.append(rFonts)


def add_styled_paragraph(doc, text, bold=False, italic=False, size_pt=12, color_rgb=(30,30,30),
                         align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=6, line_spacing=1.15,
                         font_fa="B Nazanin", font_en="Times New Roman", is_bidi=True):
    """Add a bidirectional paragraph with custom typography."""
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if is_bidi:
        pPr = p._element.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
    
    run = p.add_run(text)
    run.font.name = font_en
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._element.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_en}" w:hAnsi="{font_en}" w:cs="{font_fa}"/>')
    rPr.append(rFonts)
    return p


# ==============================================================================
# Data Ingestion & Parsing
# ==============================================================================

def load_bibliometric_data(input_path):
    """
    Ingest bibliometric literature payload from JSON, CSV, or RIS file.
    Returns list of dicts: [{id, title, authors, journal, year, citations, keywords}]
    """
    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    ext = os.path.splitext(input_path)[1].lower()
    
    if ext == '.json':
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            articles = data.get('articles', []) or data.get('studies', [])
            project_title = data.get('project_title') or (f"تحلیل علم‌سنجی: {data.get('query')}" if data.get('query') else 'Bibliometric Science Mapping')
            language = data.get('language', 'fa')
            timespan = data.get('timespan', None)
            for a in articles:
                if 'year_ad' in a and isinstance(a['year_ad'], int):
                    a['year'] = a['year_ad']
                elif 'year' in a:
                    try:
                        y_str = str(a['year']).strip()
                        for f_d, e_d in zip('۰۱۲۳۴۵۶۷۸۹', '0123456789'):
                            y_str = y_str.replace(f_d, e_d)
                        a['year'] = int(y_str)
                    except (ValueError, TypeError):
                        a['year'] = 2023
                else:
                    a['year'] = 2023
                if 'citations' not in a or not isinstance(a.get('citations'), (int, float)):
                    a['citations'] = a.get('citations') if isinstance(a.get('citations'), int) else 5
            return articles, project_title, language, timespan
        elif isinstance(data, list):
            return data, 'Bibliometric Science Mapping', 'fa', None
    
    elif ext == '.csv':
        articles = []
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                # Flexible column matching
                title = row.get('Title') or row.get('title') or f"Document {i+1}"
                authors_str = row.get('Authors') or row.get('authors') or row.get('Author') or ""
                authors = [a.strip() for a in authors_str.split(';') if a.strip()]
                if not authors and ',' in authors_str:
                    authors = [a.strip() for a in authors_str.split(',') if a.strip()]
                
                journal = row.get('Source title') or row.get('Journal') or row.get('journal') or "Unknown Journal"
                year_str = row.get('Year') or row.get('year') or "2023"
                try:
                    year = int(year_str)
                except ValueError:
                    year = 2023
                
                cit_str = row.get('Cited by') or row.get('Citations') or row.get('citations') or "0"
                try:
                    citations = int(cit_str)
                except ValueError:
                    citations = 0
                
                kw_str = row.get('Author Keywords') or row.get('Keywords') or row.get('keywords') or ""
                keywords = [k.strip() for k in kw_str.split(';') if k.strip()]
                if not keywords and ',' in kw_str:
                    keywords = [k.strip() for k in kw_str.split(',') if k.strip()]
                
                doc_id = row.get('id') or f"DOC_{i+1:03d}"
                articles.append({
                    "id": doc_id,
                    "title": title,
                    "authors": authors,
                    "journal": journal,
                    "year": year,
                    "citations": citations,
                    "keywords": keywords
                })
        return articles, 'Bibliometric Science Mapping from CSV', 'fa', None
    
    elif ext in ('.ris', '.txt'):
        articles = []
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        entries = content.split('ER  -')
        for i, entry in enumerate(entries):
            lines = entry.strip().split('\n')
            title = ""
            authors = []
            journal = ""
            year = 2023
            keywords = []
            citations = 0
            
            for line in lines:
                line = line.strip()
                if line.startswith('TI  - ') or line.startswith('T1  - '):
                    title = line[6:].strip()
                elif line.startswith('AU  - ') or line.startswith('A1  - '):
                    authors.append(line[6:].strip())
                elif line.startswith('JO  - ') or line.startswith('JF  - ') or line.startswith('T2  - '):
                    journal = line[6:].strip()
                elif line.startswith('PY  - ') or line.startswith('Y1  - '):
                    try:
                        year = int(line[6:10].strip())
                    except ValueError:
                        pass
                elif line.startswith('KW  - '):
                    keywords.append(line[6:].strip())
            
            if title:
                articles.append({
                    "id": f"DOC_{i+1:03d}",
                    "title": title,
                    "authors": authors,
                    "journal": journal or "Academic Journal",
                    "year": year,
                    "citations": citations,
                    "keywords": keywords
                })
        return articles, 'Bibliometric Science Mapping from RIS', 'fa', None
    
    else:
        raise ValueError(f"Unsupported file format: {ext}. Expected .json, .csv, or .ris")


# ==============================================================================
# Computational Core: Bradford's Law & Lotka's Law
# ==============================================================================

def analyze_bradfords_law(articles):
    """
    Computes Bradford's Law journal distribution:
    Divides journals into Zone 1 (Core, ~33%), Zone 2 (Secondary, ~33%), Zone 3 (Peripheral, ~33%).
    """
    journal_counts = Counter([a['journal'] for a in articles if a.get('journal')])
    if not journal_counts:
        return {"zones": [], "core_journals": [], "multiplier": 1.0}
    
    sorted_journals = journal_counts.most_common()
    total_articles = sum(c for _, c in sorted_journals)
    target_zone_size = total_articles / 3.0
    
    zones = []
    current_zone = 1
    current_zone_journals = []
    cum_articles = 0
    for j_name, count in sorted_journals:
        cum_articles += count
        current_zone_journals.append(j_name)
        pct = (count / total_articles) * 100
        cum_pct = (cum_articles / total_articles) * 100
        
        zones.append({
            "journal": j_name,
            "articles": count,
            "pct": round(pct, 2),
            "cum_pct": round(cum_pct, 2),
            "zone": f"Zone {current_zone}"
        })
        
        if current_zone == 1 and cum_articles >= target_zone_size:
            current_zone = 2
            current_zone_journals = []
        elif current_zone == 2 and cum_articles >= target_zone_size * 2:
            current_zone = 3
            current_zone_journals = []
    
    core_journals = [z['journal'] for z in zones if z['zone'] == 'Zone 1']
    z1_count = len(core_journals)
    z2_count = len([z for z in zones if z['zone'] == 'Zone 2'])
    z3_count = len([z for z in zones if z['zone'] == 'Zone 3'])
    multiplier = round(z2_count / max(1, z1_count), 2) if z1_count > 0 and z2_count > 0 else (round(len(sorted_journals) / 3.0, 2))
    
    return {
        "zones": zones,
        "core_journals": core_journals,
        "multiplier": multiplier,
        "total_journals": len(sorted_journals),
        "total_articles": total_articles
    }


def analyze_lotkas_law(articles):
    """
    Computes Lotka's Law author productivity distribution:
    Calculates proportion of authors with 1 paper, 2 papers, 3+ papers vs. theoretical 60%.
    """
    author_counts = Counter()
    for a in articles:
        for author in a.get('authors', []):
            if author.strip():
                author_counts[author.strip()] += 1
    
    if not author_counts:
        return {"authors": [], "productivity_tiers": {}}
    
    freq_distribution = Counter(author_counts.values())
    total_authors = len(author_counts)
    
    tiers = {}
    for papers, num_auths in sorted(freq_distribution.items()):
        tiers[papers] = {
            "num_authors": num_auths,
            "observed_pct": round((num_auths / total_authors) * 100, 2),
            "theoretical_pct": round((1.0 / (papers ** 2)) * 60.0, 2)
        }
    
    top_authors = []
    for author, p_count in author_counts.most_common(15):
        # compute total citations for author
        auth_cits = sum(a.get('citations', 0) for a in articles if author in a.get('authors', []))
        top_authors.append({
            "author": author,
            "papers": p_count,
            "citations": auth_cits,
            "tier": "Core Scholar" if p_count >= 3 else ("Prolific" if p_count == 2 else "Occasional")
        })
    
    return {
        "top_authors": top_authors,
        "productivity_tiers": tiers,
        "total_authors": total_authors
    }


# ==============================================================================
# Network Modeling, Centrality & Callon's Strategic Diagram
# ==============================================================================

def build_cooccurrence_network(articles, min_freq=1, top_n=30):
    """
    Constructs keyword co-occurrence matrix, NetworkX graph, computes centralities,
    modularity communities, and Callon's Centrality & Density coordinates.
    """
    # 1. Keyword frequency count and normalization
    kw_counter = Counter()
    for a in articles:
        # unique keywords per article to avoid artificial self-loops
        kws = set([k.strip() for k in a.get('keywords', []) if k.strip()])
        for k in kws:
            kw_counter[k] += 1
    
    # Filter keywords by frequency and top_n
    valid_kws = [k for k, count in kw_counter.most_common() if count >= min_freq]
    if len(valid_kws) > top_n:
        valid_kws = valid_kws[:top_n]
    
    if len(valid_kws) < 3:
        # fallback: take whatever is available
        valid_kws = [k for k, _ in kw_counter.most_common(15)]
    
    kw_set = set(valid_kws)
    kw_to_id = {kw: i + 1 for i, kw in enumerate(valid_kws)}
    
    # 2. Build Co-occurrence matrix
    matrix = defaultdict(lambda: defaultdict(int))
    for a in articles:
        doc_kws = [k.strip() for k in a.get('keywords', []) if k.strip() in kw_set]
        for i in range(len(doc_kws)):
            for j in range(i + 1, len(doc_kws)):
                k1, k2 = doc_kws[i], doc_kws[j]
                if k1 != k2:
                    matrix[k1][k2] += 1
                    matrix[k2][k1] += 1
    
    # 3. NetworkX Graph creation
    G = nx.Graph()
    for kw in valid_kws:
        G.add_node(kw, occurrences=kw_counter[kw], id=kw_to_id[kw])
    
    total_edges_weight = 0
    node_link_strength = defaultdict(int)
    
    for i, kw1 in enumerate(valid_kws):
        for j in range(i + 1, len(valid_kws)):
            kw2 = valid_kws[j]
            weight = matrix[kw1][kw2]
            if weight > 0:
                G.add_edge(kw1, kw2, weight=weight)
                total_edges_weight += weight
                node_link_strength[kw1] += weight
                node_link_strength[kw2] += weight
    
    # Compute Association Strength for VOSviewer
    m = max(1, total_edges_weight)
    for u, v, d in G.edges(data=True):
        w_u = node_link_strength[u]
        w_v = node_link_strength[v]
        d['association_strength'] = round((2 * m * d['weight']) / max(1, (w_u * w_v)), 4)
    
    # 4. Centrality calculations
    deg_centrality = dict(G.degree())
    try:
        bet_centrality = nx.betweenness_centrality(G, weight='weight', normalized=True)
    except Exception:
        bet_centrality = {n: 0.0 for n in G.nodes()}
    
    try:
        cls_centrality = nx.closeness_centrality(G)
    except Exception:
        cls_centrality = {n: 0.0 for n in G.nodes()}
    
    # 5. Modularity Community Detection
    try:
        communities = list(nx.community.greedy_modularity_communities(G))
    except Exception:
        # Fallback if graph is empty or disconnected
        connected_comps = list(nx.connected_components(G))
        communities = connected_comps
    
    node_cluster = {}
    cluster_nodes = defaultdict(list)
    for c_idx, comm in enumerate(communities, start=1):
        for node in comm:
            node_cluster[node] = c_idx
            cluster_nodes[c_idx].append(node)
    
    # 6. Callon's Strategic Diagram Coordinates (Centrality & Density)
    # Callon Centrality: external link strength sum * 10
    # Callon Density: internal link strength sum / cluster_size * 100
    cluster_stats = []
    for c_id, members in cluster_nodes.items():
        member_set = set(members)
        external_weight = 0
        internal_weight = 0
        
        for u in members:
            for v, d in G[u].items():
                if v in member_set:
                    internal_weight += d.get('weight', 1)
                else:
                    external_weight += d.get('weight', 1)
        
        internal_weight = internal_weight / 2.0  # undirected graph edges counted twice
        c_size = max(1, len(members))
        
        callon_c = round(10.0 * external_weight, 2)
        callon_d = round(100.0 * (internal_weight / c_size), 2)
        
        # Primary label: highest occurrence or highest degree node
        dom_node = max(members, key=lambda x: (kw_counter[x], deg_centrality[x]))
        
        cluster_stats.append({
            "cluster_id": c_id,
            "label": dom_node,
            "size": c_size,
            "members": members,
            "callon_centrality": callon_c,
            "callon_density": callon_d
        })
    
    # Determine quadrant cutoffs (median centrality and median density)
    if cluster_stats:
        med_c = np.median([c['callon_centrality'] for c in cluster_stats])
        med_d = np.median([c['callon_density'] for c in cluster_stats])
    else:
        med_c, med_d = 0.0, 0.0
    
    for c in cluster_stats:
        c_val = c['callon_centrality']
        d_val = c['callon_density']
        if c_val >= med_c and d_val >= med_d:
            c['quadrant'] = 'Quadrant I: Motor Themes'
            c['quadrant_fa'] = 'ربع اول: موتور محرک پژوهش'
        elif c_val < med_c and d_val >= med_d:
            c['quadrant'] = 'Quadrant II: Niche Themes'
            c['quadrant_fa'] = 'ربع دوم: مباحث تخصصی و حاشیه‌ای'
        elif c_val < med_c and d_val < med_d:
            c['quadrant'] = 'Quadrant III: Emerging/Declining Themes'
            c['quadrant_fa'] = 'ربع سوم: مباحث نوظهور یا رو به زوال'
        else:
            c['quadrant'] = 'Quadrant IV: Basic & Transversal Themes'
            c['quadrant_fa'] = 'ربع چهارم: مفاهیم پایه و بین‌رشته‌ای'
    
    # Summary of node metrics
    node_metrics = []
    for node in valid_kws:
        node_metrics.append({
            "id": kw_to_id[node],
            "keyword": node,
            "occurrences": kw_counter[node],
            "total_link_strength": node_link_strength[node],
            "degree": deg_centrality.get(node, 0),
            "betweenness": round(bet_centrality.get(node, 0.0), 4),
            "closeness": round(cls_centrality.get(node, 0.0), 4),
            "cluster": node_cluster.get(node, 1)
        })
    
    # Sort node metrics by Total Link Strength
    node_metrics.sort(key=lambda x: (x['total_link_strength'], x['occurrences']), reverse=True)
    
    return {
        "graph": G,
        "valid_keywords": valid_kws,
        "node_metrics": node_metrics,
        "cluster_stats": cluster_stats,
        "med_centrality": float(med_c),
        "med_density": float(med_d),
        "adjacency_matrix": matrix,
        "total_nodes": len(valid_kws),
        "total_edges": G.number_of_edges(),
        "graph_density": round(nx.density(G), 4)
    }


# ==============================================================================
# Visual Plotting: Network Map & Callon's Strategic Diagram (300 DPI)
# ==============================================================================

def generate_visual_plots(network_data, output_dir, language='fa'):
    """
    Renders and exports:
      1. `bibliometric_network_map.png`: Force-directed keyword co-occurrence map.
      2. `thematic_strategic_map.png`: Callon's 4-Quadrant Strategic Diagram.
    """
    G = network_data['graph']
    node_metrics = {m['keyword']: m for m in network_data['node_metrics']}
    cluster_stats = network_data['cluster_stats']
    
    # --------------------------------------------------------------------------
    # Figure 1: Bibliometric Network Co-Occurrence Map
    # --------------------------------------------------------------------------
    plt.figure(figsize=(12, 10), dpi=300)
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Spring layout positions
    pos = nx.spring_layout(G, k=0.75, iterations=60, seed=42)
    
    cmap = plt.get_cmap('tab10')
    node_colors = [cmap(node_metrics[n]['cluster'] % 10) for n in G.nodes()]
    node_sizes = [300 + node_metrics[n]['occurrences'] * 90 for n in G.nodes()]
    
    # Draw edges
    edge_weights = [d.get('weight', 1) for _, _, d in G.edges(data=True)]
    max_w = max(1, max(edge_weights)) if edge_weights else 1
    edge_widths = [0.8 + (w / max_w) * 3.5 for w in edge_weights]
    
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='#94A3B8', alpha=0.55)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, edgecolors='#1E293B', linewidths=1.2)
    
    # Node labels with background bbox
    labels = {n: n for n in G.nodes()}
    for node, (x, y) in pos.items():
        occ = node_metrics[node]['occurrences']
        plt.text(x, y + 0.035, node, fontsize=8.5, fontweight='bold', ha='center', va='bottom',
                 color='#0F172A',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#CBD5E1', alpha=0.85, linewidth=0.8))
    
    title_text = "نقشه هم‌رخدادی واژگان کلیدی و ساختار دانش (Keyword Co-Occurrence Network)" if language == 'fa' else "Keyword Co-Occurrence Knowledge Map"
    plt.title(title_text, fontsize=14, fontweight='bold', pad=18, color='#1E293B')
    plt.axis('off')
    plt.tight_layout()
    
    network_map_path = os.path.join(output_dir, "bibliometric_network_map.png")
    plt.savefig(network_map_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # --------------------------------------------------------------------------
    # Figure 2: Callon's Thematic Strategic Diagram (4 Quadrants)
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    
    med_c = network_data['med_centrality']
    med_d = network_data['med_density']
    
    c_vals = [c['callon_centrality'] for c in cluster_stats]
    d_vals = [c['callon_density'] for c in cluster_stats]
    
    min_x, max_x = (min(c_vals + [0]) - 5, max(c_vals + [med_c * 2, 20]) + 10)
    min_y, max_y = (min(d_vals + [0]) - 10, max(d_vals + [med_d * 2, 50]) + 20)
    
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    
    # Crosshairs at medians
    ax.axvline(x=med_c, color='#DC2626', linestyle='--', linewidth=1.5, alpha=0.75, label='Median Centrality')
    ax.axhline(y=med_d, color='#DC2626', linestyle='--', linewidth=1.5, alpha=0.75, label='Median Density')
    
    # Quadrant Shading and Labels
    # Quad II (Top-Left): Niche Themes
    q2_text = "Quadrant II: Niche Themes\n(مباحث تخصصی و حاشیه‌ای)" if language == 'fa' else "Quadrant II: Niche Themes\n(High Density, Low Centrality)"
    ax.text(min_x + (med_c - min_x) * 0.5, max_y - (max_y - med_d) * 0.15, q2_text,
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#B91C1C',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF2F2', edgecolor='#F87171', alpha=0.6))
    
    # Quad I (Top-Right): Motor Themes
    q1_text = "Quadrant I: Motor Themes\n(موتورهای محرک پژوهش)" if language == 'fa' else "Quadrant I: Motor Themes\n(High Density, High Centrality)"
    ax.text(med_c + (max_x - med_c) * 0.5, max_y - (max_y - med_d) * 0.15, q1_text,
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#15803D',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#F0FDF4', edgecolor='#4ADE80', alpha=0.6))
    
    # Quad III (Bottom-Left): Emerging or Declining Themes
    q3_text = "Quadrant III: Emerging/Declining\n(مباحث نوظهور یا رو به زوال)" if language == 'fa' else "Quadrant III: Emerging/Declining Themes\n(Low Density, Low Centrality)"
    ax.text(min_x + (med_c - min_x) * 0.5, min_y + (med_d - min_y) * 0.15, q3_text,
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#B45309',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFBEB', edgecolor='#FBBF24', alpha=0.6))
    
    # Quad IV (Bottom-Right): Basic & Transversal Themes
    q4_text = "Quadrant IV: Basic Themes\n(مفاهیم پایه و بین‌رشته‌ای)" if language == 'fa' else "Quadrant IV: Basic & Transversal Themes\n(Low Density, High Centrality)"
    ax.text(med_c + (max_x - med_c) * 0.5, min_y + (med_d - min_y) * 0.15, q4_text,
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1D4ED8',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#EFF6FF', edgecolor='#60A5FA', alpha=0.6))
    
    # Plot clusters as bubbles
    for c in cluster_stats:
        cid = c['cluster_id']
        cx = c['callon_centrality']
        cy = c['callon_density']
        c_size = 400 + c['size'] * 120
        c_color = cmap(cid % 10)
        
        ax.scatter(cx, cy, s=c_size, color=c_color, edgecolors='#1E293B', linewidth=1.5, alpha=0.85, zorder=5)
        ax.annotate(f"C{cid}: {c['label']} (N={c['size']})", (cx, cy),
                    textcoords="offset points", xytext=(0, 14), ha='center',
                    fontsize=8.5, fontweight='bold', color='#0F172A',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#CBD5E1', alpha=0.85))
    
    x_label = "مرکزیت کالون (Callon's Centrality - پیوند بیرونی)" if language == 'fa' else "Callon's Centrality (External Link Strength)"
    y_label = "تراکم کالون (Callon's Density - پیوستگی درونی)" if language == 'fa' else "Callon's Density (Internal Cohesion)"
    main_title = "نمودار راهبردی کالون و دسته‌بندی خوشه‌های موضوعی (Callon's Strategic Diagram)" if language == 'fa' else "Callon's Thematic Strategic Diagram"
    
    ax.set_xlabel(x_label, fontsize=11, fontweight='bold', labelpad=10, color='#1E293B')
    ax.set_ylabel(y_label, fontsize=11, fontweight='bold', labelpad=10, color='#1E293B')
    ax.set_title(main_title, fontsize=13, fontweight='bold', pad=15, color='#1E293B')
    ax.grid(True, linestyle=':', alpha=0.5, color='#CBD5E1')
    
    strategic_map_path = os.path.join(output_dir, "thematic_strategic_map.png")
    plt.tight_layout()
    plt.savefig(strategic_map_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return network_map_path, strategic_map_path, pos


# ==============================================================================
# VOSviewer Native File Exporter
# ==============================================================================

def export_vosviewer_files(network_data, pos, output_dir):
    """
    Exports native VOSviewer tab-delimited files:
      1. `vosviewer_map.txt`: id\tlabel\tx\ty\tcluster\tweight<Total link strength>\tweight<Occurrences>
      2. `vosviewer_network.txt`: source\ttarget\tstrength
    """
    node_metrics = network_data['node_metrics']
    G = network_data['graph']
    kw_to_id = {m['keyword']: m['id'] for m in node_metrics}
    
    # 1. Map file
    map_path = os.path.join(output_dir, "vosviewer_map.txt")
    with open(map_path, 'w', encoding='utf-8') as f:
        f.write("id\tlabel\tx\ty\tcluster\tweight<Total link strength>\tweight<Occurrences>\n")
        for m in node_metrics:
            kw = m['keyword']
            x, y = pos.get(kw, (0.0, 0.0))
            f.write(f"{m['id']}\t{kw}\t{x:.4f}\t{y:.4f}\t{m['cluster']}\t{m['total_link_strength']}\t{m['occurrences']}\n")
    
    # 2. Network file
    net_path = os.path.join(output_dir, "vosviewer_network.txt")
    with open(net_path, 'w', encoding='utf-8') as f:
        f.write("source\ttarget\tstrength\n")
        for u, v, d in G.edges(data=True):
            src_id = kw_to_id.get(u)
            tgt_id = kw_to_id.get(v)
            weight = d.get('weight', 1)
            if src_id and tgt_id:
                f.write(f"{src_id}\t{tgt_id}\t{weight}\n")
    
    return map_path, net_path


# ==============================================================================
# Excel Multi-Sheet Matrix Builder (5 Sheets)
# ==============================================================================

def export_excel_matrix(articles, bradford_res, lotka_res, network_data, output_dir, language='fa'):
    """
    Exports 5-sheet bibliometric matrix workbook:
      Sheet 1: Overview & Top Papers (21 chars)
      Sheet 2: Keyword Centrality (18 chars)
      Sheet 3: Adjacency Matrix (16 chars)
      Sheet 4: Author Collaboration (20 chars)
      Sheet 5: Thematic Clusters (17 chars)
    """
    wb = openpyxl.Workbook()
    # default sheet
    ws1 = wb.active
    ws1.title = "Overview & Top Papers"
    
    header_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Arial", size=10)
    bold_font = Font(name="Arial", size=10, bold=True)
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    
    # --------------------------------------------------------------------------
    # Sheet 1: Overview & Top Papers
    # --------------------------------------------------------------------------
    ws1.append(["Metric / Parameter", "Value / Description", "Notes & Scientific Standards"])
    ws1.append(["Total Corpus Documents", len(articles), "Analyzed empirical & review literature"])
    years = [a['year'] for a in articles if a.get('year')]
    timespan_str = f"{min(years)} - {max(years)}" if years else "N/A"
    ws1.append(["Publication Timespan", timespan_str, "Temporal coverage range"])
    ws1.append(["Total Unique Journals", bradford_res['total_journals'], "Sources analyzed under Bradford's Law"])
    ws1.append(["Bradford Core Journals (Zone 1)", len(bradford_res['core_journals']), ", ".join(bradford_res['core_journals'][:5])])
    ws1.append(["Bradford Multiplier (k)", bradford_res['multiplier'], "Empirical journal scattering coefficient"])
    ws1.append(["Total Authors Analyzed", lotka_res['total_authors'], "Authors evaluated under Lotka's Law"])
    ws1.append(["Co-Occurrence Network Nodes", network_data['total_nodes'], "Filtered keywords (min_freq threshold)"])
    ws1.append(["Network Density", network_data['graph_density'], "Interconnectedness of intellectual domain"])
    ws1.append([])
    
    ws1.append(["Document ID", "Title", "Authors", "Journal", "Year", "Citations"])
    for cell in ws1[ws1.max_row]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    top_cited = sorted(articles, key=lambda x: x.get('citations', 0), reverse=True)
    for a in top_cited:
        auth_str = ", ".join(a.get('authors', []))
        ws1.append([a.get('id', ''), a.get('title', ''), auth_str, a.get('journal', ''), a.get('year', ''), a.get('citations', 0)])
    
    # --------------------------------------------------------------------------
    # Sheet 2: Keyword Centrality
    # --------------------------------------------------------------------------
    ws2 = wb.create_sheet(title="Keyword Centrality")
    ws2.append(["ID", "Keyword", "Occurrences", "Total Link Strength", "Degree Centrality", "Betweenness Centrality", "Closeness Centrality", "Cluster ID"])
    for cell in ws2[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    for m in network_data['node_metrics']:
        ws2.append([
            m['id'], m['keyword'], m['occurrences'], m['total_link_strength'],
            m['degree'], m['betweenness'], m['closeness'], m['cluster']
        ])
    
    # --------------------------------------------------------------------------
    # Sheet 3: Adjacency Matrix
    # --------------------------------------------------------------------------
    ws3 = wb.create_sheet(title="Adjacency Matrix")
    kws = network_data['valid_keywords']
    adj = network_data['adjacency_matrix']
    
    header_row = ["Keyword"] + kws
    ws3.append(header_row)
    for cell in ws3[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    for kw1 in kws:
        row = [kw1] + [adj[kw1][kw2] for kw2 in kws]
        ws3.append(row)
    
    # --------------------------------------------------------------------------
    # Sheet 4: Author Collaboration
    # --------------------------------------------------------------------------
    ws4 = wb.create_sheet(title="Author Collaboration")
    ws4.append(["Author Name", "Publications", "Total Citations", "Productivity Tier"])
    for cell in ws4[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    for auth in lotka_res['top_authors']:
        ws4.append([auth['author'], auth['papers'], auth['citations'], auth['tier']])
    
    # --------------------------------------------------------------------------
    # Sheet 5: Thematic Clusters
    # --------------------------------------------------------------------------
    ws5 = wb.create_sheet(title="Thematic Clusters")
    ws5.append(["Cluster ID", "Dominant Label", "Cluster Size (Keywords)", "Member Keywords", "Callon Centrality", "Callon Density", "Strategic Quadrant"])
    for cell in ws5[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    for c in network_data['cluster_stats']:
        quad = c.get('quadrant_fa', c.get('quadrant')) if language == 'fa' else c.get('quadrant')
        members_str = ", ".join(c['members'])
        ws5.append([
            c['cluster_id'], c['label'], c['size'], members_str,
            c['callon_centrality'], c['callon_density'], quad
        ])
    
    # Styling and auto column width adjustment across all sheets
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(40, max(12, max_len + 3))
            for cell in col:
                cell.border = thin_border
                if cell.row != 1 and cell.fill.start_color.rgb != "001A365D":
                    cell.font = data_font
                    if isinstance(cell.value, (int, float)):
                        cell.alignment = center_align
    
    excel_path = os.path.join(output_dir, "bibliometric_matrix.xlsx")
    wb.save(excel_path)
    return excel_path


# ==============================================================================
# Publication Word Report Compiler (OpenXML BiDi RTL / APA 7)
# ==============================================================================

def export_word_report(articles, bradford_res, lotka_res, network_data, project_title,
                       network_map_img, strategic_map_img, output_dir, language='fa'):
    """
    Compiles defense-ready APA 7th Edition Word document:
    `گزارش_تحلیل_علم‌سنجی_و_ترسیم_نقشه_دانش.docx` or `Bibliometric_Science_Mapping_Report.docx`.
    With authentic Persian typography (B Titr, B Nazanin) and OpenXML BiDi tags.
    """
    doc = docx.Document()
    is_bidi = (language == 'fa')
    
    # Setup standard 1-inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
    
    # --------------------------------------------------------------------------
    # Title & Metadata
    # --------------------------------------------------------------------------
    doc_title = project_title if project_title else (
        "گزارش جامع تحلیل علم‌سنجی، ترسیم نقشه دانش و مدل‌سازی نمودار راهبردی کالون" if is_bidi
        else "Comprehensive Bibliometric Science Mapping and Callon's Strategic Diagram Report"
    )
    add_styled_paragraph(doc, doc_title, bold=True, size_pt=18, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12,
                         font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    subtitle = (
        f"تدوین‌شده بر اساس استانداردهای ووس‌ویوور (VOSviewer) و کتاب‌سنجی آکادمیک | تاریخ تولید: {datetime.now().strftime('%Y-%m-%d')}" if is_bidi
        else f"Formulated under VOSviewer and Academic Bibliometrics Standards | Generated: {datetime.now().strftime('%Y-%m-%d')}"
    )
    add_styled_paragraph(doc, subtitle, italic=True, size_pt=10.5, color_rgb=(100, 116, 139),
                         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18,
                         font_fa="B Nazanin", font_en="Times New Roman", is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 1: Executive Summary & Corpus Overview
    # --------------------------------------------------------------------------
    h1_text = "۱. چکیده مدیریتی و مشخصات پیکره کتاب‌شناختی" if is_bidi else "1. Executive Summary & Bibliometric Corpus Overview"
    add_styled_paragraph(doc, h1_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    summary_p1 = (
        f"پژوهش حاضر با رویکرد علم‌سنجی و مصورسازی ساختار دانش، به تحلیل کمّی و ساختاری تعداد {len(articles)} سند پژوهشی پرداخته است. "
        f"هدف بنیادین این تحلیل، کشف الگوهای هم‌رخدادی واژگان، خوشه‌بندی ساختارهای مفهومی، ترسیم جبهه‌های پژوهش (Research Fronts) و "
        f"دسته‌بندی خوشه‌های موضوعی بر پایه دو شاخص ساختاری مرکزیت کالون (Callon's Centrality) و تراکم کالون (Callon's Density) در نمودار راهبردی بوده است."
        if is_bidi else
        f"This bibliometric investigation evaluates the intellectual structure of {len(articles)} scientific documents. "
        f"The primary objective is to delineate co-occurrence topologies, conceptual clusters, research frontiers, and strategic thematic quadrants "
        f"evaluated through Callon's centrality and density parameters."
    )
    add_styled_paragraph(doc, summary_p1, size_pt=11, space_after=10, is_bidi=is_bidi)
    
    # Table 1: Corpus Overview Table
    t1_caption = "جدول ۱. مشخصات عمومی پیکره اسناد و شاخص‌های کلان شبکه" if is_bidi else "Table 1. Macro-Structural Characteristics of Bibliometric Corpus"
    add_styled_paragraph(doc, t1_caption, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=4, is_bidi=is_bidi)
    
    t1 = doc.add_table(rows=6, cols=2)
    make_table_apa7(t1, is_bidi=is_bidi)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    years = [a['year'] for a in articles if a.get('year')]
    timespan_val = f"{min(years)} - {max(years)}" if years else "N/A"
    
    t1_rows = [
        ("تعداد کل مقالات و اسناد بررسی‌شده" if is_bidi else "Total Documents Analyzed", str(len(articles))),
        ("محدوده زمانی انتشار اسناد" if is_bidi else "Publication Timespan", timespan_val),
        ("تعداد کل نشریات علمی منبع" if is_bidi else "Total Scientific Journals", str(bradford_res['total_journals'])),
        ("تعداد نویسندگان مشارکت‌کننده" if is_bidi else "Contributing Authors", str(lotka_res['total_authors'])),
        ("تعداد گره‌های واژگانی شبکه هم‌رخدادی" if is_bidi else "Co-Occurrence Network Nodes", str(network_data['total_nodes'])),
        ("چگالی شبکه هم‌رخدادی (Graph Density)" if is_bidi else "Network Density", str(network_data['graph_density']))
    ]
    
    for idx, (label, val) in enumerate(t1_rows):
        format_cell_text(t1.rows[idx].cells[0], label, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_bidi)
        format_cell_text(t1.rows[idx].cells[1], val, bold=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER, is_bidi=is_bidi)
        set_cell_margins(t1.rows[idx].cells[0])
        set_cell_margins(t1.rows[idx].cells[1])
        if idx % 2 == 1:
            set_cell_shading(t1.rows[idx].cells[0], "F8FAFC")
            set_cell_shading(t1.rows[idx].cells[1], "F8FAFC")
    
    add_styled_paragraph(doc, "", space_after=12, is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 2: Bradford's Law & Core Journals
    # --------------------------------------------------------------------------
    h2_text = "۲. تحلیل پراکندگی نشریات بر اساس قانون بردفورد (Bradford's Law)" if is_bidi else "2. Journal Scattering Analysis via Bradford's Law"
    add_styled_paragraph(doc, h2_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    bradford_desc = (
        f"قانون بردفورد نشریات علمی را بر پایه میزان بهره‌وری به سه منطقه هسته (Zone 1)، ثانویه (Zone 2) و حاشیه‌ای (Zone 3) طبقه‌بندی می‌کند. "
        f"در این پژوهش، ضریب پراکندگی بردفورد برابر با k = {bradford_res['multiplier']} محاسبه شد. "
        f"نشریات هسته (Zone 1) که بیشترین چگالی پژوهشی را دارند شامل موارد زیر می‌باشند: {', '.join(bradford_res['core_journals'][:6])}."
        if is_bidi else
        f"Bradford's Law partitions journals into core (Zone 1), secondary (Zone 2), and peripheral (Zone 3) tiers. "
        f"The empirical Bradford multiplier was calculated as k = {bradford_res['multiplier']}. "
        f"The nuclear journals (Zone 1) include: {', '.join(bradford_res['core_journals'][:6])}."
    )
    add_styled_paragraph(doc, bradford_desc, size_pt=11, space_after=10, is_bidi=is_bidi)
    
    # Table 2: Bradford Zones
    t2_caption = "جدول ۲. نشریات هسته و پراکندگی مقالات در مناطق بردفورد" if is_bidi else "Table 2. Bradford's Law Core Journal Distribution"
    add_styled_paragraph(doc, t2_caption, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=4, is_bidi=is_bidi)
    
    sample_zones = bradford_res['zones'][:8]
    t2 = doc.add_table(rows=len(sample_zones) + 1, cols=5)
    make_table_apa7(t2, is_bidi=is_bidi)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    t2_headers = ["نام نشریه علمی", "تعداد اسناد", "درصد سهم", "درصد تجمعی", "منطقه بردفورد"] if is_bidi else ["Journal Name", "Articles", "Share %", "Cum %", "Bradford Zone"]
    for c_i, h in enumerate(t2_headers):
        format_cell_text(t2.rows[0].cells[c_i], h, bold=True, size_pt=10, color_rgb=(255, 255, 255), is_bidi=is_bidi)
        set_cell_shading(t2.rows[0].cells[c_i], "1A365D")
        set_cell_margins(t2.rows[0].cells[c_i])
    
    for r_i, z in enumerate(sample_zones, start=1):
        row = t2.rows[r_i]
        format_cell_text(row.cells[0], z['journal'], bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_bidi)
        format_cell_text(row.cells[1], z['articles'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[2], f"{z['pct']}%", bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[3], f"{z['cum_pct']}%", bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[4], z['zone'], bold=True, size_pt=9.5, is_bidi=is_bidi)
        for cell in row.cells:
            set_cell_margins(cell)
        if r_i % 2 == 0:
            for cell in row.cells:
                set_cell_shading(cell, "F8FAFC")
    
    add_styled_paragraph(doc, "", space_after=12, is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 3: Author Productivity & Lotka's Law
    # --------------------------------------------------------------------------
    h3_text = "۳. ارزیابی بهره‌وری نویسندگان و آزمون قانون لوتکا (Lotka's Law)" if is_bidi else "3. Author Productivity & Lotka's Law Analysis"
    add_styled_paragraph(doc, h3_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    lotka_desc = (
        f"بر طبق قانون لوتکا، سهم دانشمندانی که تنها ۱ مقاله تولید می‌کنند در حدود ۶۰ درصد برآورد می‌شود. "
        f"در مجموعه داده حاضر، نویسندگان برتر بر اساس فراوانی انتشار و استنادات دریافتی استخراج گردیده‌اند. "
        f"شایان ذکر است پژوهشگرانی که بیشترین پیوند بین‌فردی را برقرار کرده‌اند، در جایگاه رهبران فکری (Thought Leaders) این حوزه قرار دارند."
        if is_bidi else
        f"Under Lotka's Law, scholars producing a single manuscript constitute roughly 60% of author population. "
        f"Core thought leaders exhibiting elevated publication volume and citation impact were isolated."
    )
    add_styled_paragraph(doc, lotka_desc, size_pt=11, space_after=10, is_bidi=is_bidi)
    
    # Table 3: Top Authors
    t3_caption = "جدول ۳. پژوهشگران برجسته و فراوانی تولیدات علمی" if is_bidi else "Table 3. Prolific Scholars & Authorship Productivity"
    add_styled_paragraph(doc, t3_caption, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=4, is_bidi=is_bidi)
    
    top_auths = lotka_res['top_authors'][:7]
    t3 = doc.add_table(rows=len(top_auths) + 1, cols=4)
    make_table_apa7(t3, is_bidi=is_bidi)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    t3_headers = ["نام پژوهشگر / نویسنده", "تعداد مقالات", "مجموع استنادات", "رده بهره‌وری"] if is_bidi else ["Author Name", "Publications", "Citations", "Productivity Tier"]
    for c_i, h in enumerate(t3_headers):
        format_cell_text(t3.rows[0].cells[c_i], h, bold=True, size_pt=10, color_rgb=(255, 255, 255), is_bidi=is_bidi)
        set_cell_shading(t3.rows[0].cells[c_i], "1A365D")
        set_cell_margins(t3.rows[0].cells[c_i])
    
    for r_i, auth in enumerate(top_auths, start=1):
        row = t3.rows[r_i]
        format_cell_text(row.cells[0], auth['author'], bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_bidi)
        format_cell_text(row.cells[1], auth['papers'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[2], auth['citations'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[3], auth['tier'], bold=True, size_pt=9.5, is_bidi=is_bidi)
        for cell in row.cells:
            set_cell_margins(cell)
        if r_i % 2 == 0:
            for cell in row.cells:
                set_cell_shading(cell, "F8FAFC")
    
    add_styled_paragraph(doc, "", space_after=12, is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 4: Keyword Co-Occurrence & Network Centrality
    # --------------------------------------------------------------------------
    h4_text = "۴. تحلیل شبکه هم‌رخدادی واژگان و شاخص‌های مرکزیت ساختاری" if is_bidi else "4. Keyword Co-Occurrence Topology & Structural Centrality"
    add_styled_paragraph(doc, h4_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    topo_desc = (
        f"شبکه هم‌رخدادی واژگان کلیدی نشان‌دهنده ساختار دانشی و ارتباطات مفهومی بین سازه‌هاست. "
        f"شاخص مرکزیت درجه (Degree) بازتاب‌دهنده حضور محوری سازه در مقالات بوده، در حالی که مرکزیت بینابینی (Betweenness Centrality) "
        f"واژگانی را مشخص می‌سازد که به عنوان پل مفهومی (Conceptual Bridge) میان دو جریان پژوهشی عمل می‌کنند. "
        f"مرکزیت نزدیکی (Closeness Centrality) نیز سرعت و سهولت دسترسی یک مفهوم به سایر سازه‌ها را می‌سنجد."
        if is_bidi else
        f"Keyword co-occurrence reveals the intellectual topology of the discipline. "
        f"Degree centrality indicates foundational prominence, betweenness isolates intellectual bridges connecting disparate paradigms, "
        f"and closeness measures diffusion efficiency across the network."
    )
    add_styled_paragraph(doc, topo_desc, size_pt=11, space_after=10, is_bidi=is_bidi)
    
    # Table 4: Keyword Centrality
    t4_caption = "جدول ۴. شاخص‌های مرکزیت ساختاری واژگان کلیدی برتر" if is_bidi else "Table 4. Structural Centrality Metrics of Top Keywords"
    add_styled_paragraph(doc, t4_caption, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=4, is_bidi=is_bidi)
    
    top_metrics = network_data['node_metrics'][:10]
    t4 = doc.add_table(rows=len(top_metrics) + 1, cols=6)
    make_table_apa7(t4, is_bidi=is_bidi)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    t4_headers = ["واژه کلیدی", "رخداد", "پیوند کل", "مرکزیت درجه", "مرکزیت بینابینی", "خوشه"] if is_bidi else ["Keyword", "Occurrences", "TLS", "Degree", "Betweenness", "Cluster"]
    for c_i, h in enumerate(t4_headers):
        format_cell_text(t4.rows[0].cells[c_i], h, bold=True, size_pt=10, color_rgb=(255, 255, 255), is_bidi=is_bidi)
        set_cell_shading(t4.rows[0].cells[c_i], "1A365D")
        set_cell_margins(t4.rows[0].cells[c_i])
    
    for r_i, m in enumerate(top_metrics, start=1):
        row = t4.rows[r_i]
        format_cell_text(row.cells[0], m['keyword'], bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_bidi)
        format_cell_text(row.cells[1], m['occurrences'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[2], m['total_link_strength'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[3], m['degree'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[4], m['betweenness'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[5], f"Cluster {m['cluster']}", bold=True, size_pt=9.5, is_bidi=is_bidi)
        for cell in row.cells:
            set_cell_margins(cell)
        if r_i % 2 == 0:
            for cell in row.cells:
                set_cell_shading(cell, "F8FAFC")
    
    add_styled_paragraph(doc, "", space_after=12, is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 5: Thematic Clusters & Callon's Strategic Diagram
    # --------------------------------------------------------------------------
    h5_text = "۵. مدل‌سازی خوشه‌های موضوعی و نمودار راهبردی کالون (Callon's Strategic Diagram)" if is_bidi else "5. Thematic Clustering & Callon's Strategic Diagram"
    add_styled_paragraph(doc, h5_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    callon_desc = (
        f"بر پایه مدل تحلیل راهبردی کالون، هر خوشه موضوعی بر اساس دو محور تحلیل می‌شود: "
        f"مرکزیت کالون (میزان پیوند خوشه با سایر حوزه‌ها) و تراکم کالون (میزان بلوغ و پیوستگی درونی میان واژگان خوشه). "
        f"نقاط مبنای تفکیک ربع‌های چهارگانه برابر با میانه مرکزیت ({network_data['med_centrality']}) و میانه تراکم ({network_data['med_density']}) تعیین شدند: \n"
        f"• ربع اول (موتور محرک): حوزه‌های پژوهشی محوری با تراکم بالا و پیوند گسترده با ادبیات کلان.\n"
        f"• ربع دوم (مباحث تخصصی و حاشیه‌ای): حوزه‌های دارای پیوستگی مفهومی قوی اما ایزوله نسبت به بدنه اصلی.\n"
        f"• ربع سوم (مباحث نوظهور یا رو به زوال): مباحث حاشیه‌ای با پیوندهای ضعیف که نیازمند پایش تحولی هستند.\n"
        f"• ربع چهارم (مفاهیم پایه و بین‌رشته‌ای): سازه‌های بنیادین که بستر اصلی حوزه را تشکیل می‌دهند اما تخصصی نشده‌اند."
        if is_bidi else
        f"Callon's strategic diagram partitions thematic clusters across two axes: Centrality (external linkage) and Density (internal cohesion). "
        f"Median split thresholds were set at Centrality = {network_data['med_centrality']} and Density = {network_data['med_density']}: \n"
        f"• Quadrant I (Motor Themes): Core research frontiers, highly mature and well-connected.\n"
        f"• Quadrant II (Niche Themes): Specialized topics with intense internal cohesion but isolated from main paradigms.\n"
        f"• Quadrant III (Emerging/Declining Themes): Peripheral concepts exhibiting weak internal and external ties.\n"
        f"• Quadrant IV (Basic Themes): Foundational transversals underpinning the discipline."
    )
    add_styled_paragraph(doc, callon_desc, size_pt=11, space_after=10, is_bidi=is_bidi)
    
    # Table 5: Clusters & Quadrants
    t5_caption = "جدول ۵. خوشه‌های موضوعی شناسایی‌شده و طبقه‌بندی در ربع‌های نمودار راهبردی" if is_bidi else "Table 5. Thematic Clusters & Strategic Quadrant Classification"
    add_styled_paragraph(doc, t5_caption, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=4, is_bidi=is_bidi)
    
    clusters = network_data['cluster_stats']
    t5 = doc.add_table(rows=len(clusters) + 1, cols=6)
    make_table_apa7(t5, is_bidi=is_bidi)
    t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    t5_headers = ["شناسه خوشه", "عنوان اصلی خوشه", "تعداد واژگان", "مرکزیت کالون", "تراکم کالون", "ربع راهبردی"] if is_bidi else ["Cluster ID", "Dominant Label", "Size", "Centrality", "Density", "Strategic Quadrant"]
    for c_i, h in enumerate(t5_headers):
        format_cell_text(t5.rows[0].cells[c_i], h, bold=True, size_pt=10, color_rgb=(255, 255, 255), is_bidi=is_bidi)
        set_cell_shading(t5.rows[0].cells[c_i], "1A365D")
        set_cell_margins(t5.rows[0].cells[c_i])
    
    for r_i, c in enumerate(clusters, start=1):
        row = t5.rows[r_i]
        format_cell_text(row.cells[0], f"Cluster {c['cluster_id']}", bold=True, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[1], c['label'], bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_bidi)
        format_cell_text(row.cells[2], c['size'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[3], c['callon_centrality'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[4], c['callon_density'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        quad_str = c.get('quadrant_fa', c.get('quadrant')) if is_bidi else c.get('quadrant')
        format_cell_text(row.cells[5], quad_str, bold=True, size_pt=9.0, is_bidi=is_bidi)
        for cell in row.cells:
            set_cell_margins(cell)
        if r_i % 2 == 0:
            for cell in row.cells:
                set_cell_shading(cell, "F8FAFC")
    
    add_styled_paragraph(doc, "", space_after=16, is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 6: High-Resolution Embedded Visualizations (300 DPI)
    # --------------------------------------------------------------------------
    h6_text = "۶. تصاویر نقشه‌برداری ساختار دانش و نمودار راهبردی (Visual Science Maps)" if is_bidi else "6. Science Mapping & Strategic Diagram Visualizations"
    add_styled_paragraph(doc, h6_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    if os.path.exists(network_map_img):
        fig1_caption = "شکل ۱. نقشه هم‌رخدادی واژگان کلیدی و خوشه‌های مفهومی (VOSviewer Standard Layout)" if is_bidi else "Figure 1. Keyword Co-Occurrence Knowledge Map"
        add_styled_paragraph(doc, fig1_caption, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                             align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6, is_bidi=is_bidi)
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.add_run().add_picture(network_map_img, width=Inches(6.2))
        add_styled_paragraph(doc, "", space_after=14, is_bidi=is_bidi)
    
    if os.path.exists(strategic_map_img):
        fig2_caption = "شکل ۲. نمودار راهبردی کالون و تفکیک خوشه‌ها در ربع‌های چهارگانه (Callon's Strategic Diagram)" if is_bidi else "Figure 2. Callon's 4-Quadrant Strategic Diagram"
        add_styled_paragraph(doc, fig2_caption, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                             align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6, is_bidi=is_bidi)
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.add_run().add_picture(strategic_map_img, width=Inches(6.2))
        add_styled_paragraph(doc, "", space_after=14, is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 7: Implications for Thesis Chapter 2 & Future Research Frontiers
    # --------------------------------------------------------------------------
    h7_text = "۷. دلالت‌های نظری برای فصل دوم رساله و افق‌های نوپدید پژوهشی" if is_bidi else "7. Theoretical Implications for Chapter 2 Literature Review"
    add_styled_paragraph(doc, h7_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    implications_text = (
        f"یافته‌های تحلیل علم‌سنجی حاضر برای تدوین فصل دوم رساله (مبانی نظری و پیشینه پژوهش) دارای دلالت‌های اساسی است:\n"
        f"۱. تبیین چهارچوب نظری رساله باید بر محور خوشه‌های ربع اول (موتورهای محرک) مستقر گردد، چرا که این مفاهیم بیشترین پذیرش علمی و پیوند مفهومی را دارند.\n"
        f"۲. مفاهیم ربع چهارم (مفاهیم پایه) می‌بایست به عنوان متغیرهای تعدیل‌گر، زمینه‌ای یا پایه‌ای در مدل مفهومی پژوهش جانمایی شوند.\n"
        f"۳. حوزه‌های واقع در ربع سوم (مباحث نوظهور) خلاءهای پژوهشی (Research Gaps) اصیلی را فراهم می‌آورند که پرداختن به آن‌ها اصالت و نوآوری رساله را به اثبات می‌رساند."
        if is_bidi else
        f"The empirical science mapping provides three pivotal strategic directives for Chapter 2 synthesis:\n"
        f"1. The conceptual model must anchor on Quadrant I Motor Themes representing mature, accepted research paradigms.\n"
        f"2. Quadrant IV Basic Themes should function as contextual or moderating foundations.\n"
        f"3. Quadrant III Emerging Themes represent authentic intellectual frontiers and literature gaps justifying novel empirical inquiries."
    )
    add_styled_paragraph(doc, implications_text, size_pt=11, space_after=12, is_bidi=is_bidi)
    
    file_name = "گزارش_تحلیل_علم‌سنجی_و_ترسیم_نقشه_دانش.docx" if is_bidi else "Bibliometric_Science_Mapping_Report.docx"
    doc_path = os.path.join(output_dir, file_name)
    doc.save(doc_path)
    return doc_path


# ==============================================================================
# Master CLI Controller
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="VOSviewer/Bibliometrix Science Mapping & Network Analysis Engine (AcademicSuite Skill #24)"
    )
    parser.add_argument("-i", "--input", help="Path to input literature file (.json, .csv, or .ris)")
    parser.add_argument("-o", "--output-dir", default=".", help="Directory to save generated outputs")
    parser.add_argument("-t", "--analysis-type", default="keywords", choices=["keywords", "authors", "journals"],
                        help="Analysis topology type (default: keywords)")
    parser.add_argument("-m", "--min-freq", type=int, default=1, help="Minimum occurrence frequency threshold (default: 1)")
    parser.add_argument("--top-n", type=int, default=30, help="Maximum items included in network mapping (default: 30)")
    parser.add_argument("-l", "--language", default="fa", choices=["fa", "en"], help="Report language: 'fa' (Persian, default) or 'en'")
    parser.add_argument("--title", help="Custom project title for the bibliometric report")
    parser.add_argument("--vosviewer", action="store_true", default=True, help="Export native VOSviewer map and network files")
    
    args = parser.parse_args()
    
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Ingestion
    if args.input:
        input_file = os.path.abspath(args.input)
    else:
        # Check if default sample payload exists
        script_dir = os.path.dirname(os.path.abspath(__file__))
        skill_root = os.path.dirname(script_dir)
        default_sample = os.path.join(skill_root, "examples", "sample_bibliometric_payload.json")
        if os.path.exists(default_sample):
            input_file = default_sample
        else:
            raise FileNotFoundError("No input file provided and sample payload not found.")
    
    print(f"[*] Ingesting bibliometric literature: {input_file}")
    articles, file_title, file_lang, timespan = load_bibliometric_data(input_file)
    
    project_title = args.title or file_title
    language = args.language or file_lang or 'fa'
    
    print(f"[*] Loaded {len(articles)} documents. Running Bradford's Law & Lotka's Law...")
    
    # 2. Bradford & Lotka Analysis
    bradford_res = analyze_bradfords_law(articles)
    lotka_res = analyze_lotkas_law(articles)
    
    # 3. Network Co-Occurrence & Callon Strategic Modeling
    print(f"[*] Constructing co-occurrence network (min_freq={args.min_freq}, top_n={args.top_n})...")
    network_data = build_cooccurrence_network(articles, min_freq=args.min_freq, top_n=args.top_n)
    
    print(f"[*] Network generated: {network_data['total_nodes']} nodes, {network_data['total_edges']} edges, {len(network_data['cluster_stats'])} clusters.")
    
    # 4. Visual Plots (300 DPI)
    print(f"[*] Generating 300-DPI visual plots...")
    net_img, strat_img, pos = generate_visual_plots(network_data, output_dir, language=language)
    print(f"    [+] Network Map: {net_img}")
    print(f"    [+] Strategic Diagram: {strat_img}")
    
    # 5. VOSviewer Native Files
    if args.vosviewer:
        print(f"[*] Exporting VOSviewer native files...")
        vos_map, vos_net = export_vosviewer_files(network_data, pos, output_dir)
        print(f"    [+] VOSviewer Map: {vos_map}")
        print(f"    [+] VOSviewer Network: {vos_net}")
    
    # 6. Excel 5-Sheet Matrix
    print(f"[*] Exporting 5-sheet Excel matrix...")
    excel_path = export_excel_matrix(articles, bradford_res, lotka_res, network_data, output_dir, language=language)
    print(f"    [+] Excel Matrix: {excel_path}")
    
    # 7. Word Report (OpenXML BiDi APA 7)
    print(f"[*] Compiling APA 7th Edition Word report...")
    doc_path = export_word_report(
        articles, bradford_res, lotka_res, network_data, project_title,
        net_img, strat_img, output_dir, language=language
    )
    print(f"    [+] Word Report: {doc_path}")
    
    # 8. JSON Ledger
    summary_json = {
        "project_title": project_title,
        "language": language,
        "timestamp": datetime.now().isoformat(),
        "total_documents": len(articles),
        "total_journals": bradford_res['total_journals'],
        "bradford_multiplier": bradford_res['multiplier'],
        "bradford_core_journals": bradford_res['core_journals'],
        "total_authors": lotka_res['total_authors'],
        "network_nodes": network_data['total_nodes'],
        "network_edges": network_data['total_edges'],
        "graph_density": network_data['graph_density'],
        "median_centrality": network_data['med_centrality'],
        "median_density": network_data['med_density'],
        "clusters": [
            {
                "id": c['cluster_id'],
                "label": c['label'],
                "size": c['size'],
                "centrality": c['callon_centrality'],
                "density": c['callon_density'],
                "quadrant": c.get('quadrant_fa' if language == 'fa' else 'quadrant'),
                "members": c['members']
            } for c in network_data['cluster_stats']
        ],
        "top_keywords": network_data['node_metrics'][:15],
        "artifacts": {
            "word_report": os.path.basename(doc_path),
            "excel_matrix": os.path.basename(excel_path),
            "network_map_image": os.path.basename(net_img),
            "strategic_map_image": os.path.basename(strat_img),
            "vosviewer_map": "vosviewer_map.txt" if args.vosviewer else None,
            "vosviewer_network": "vosviewer_network.txt" if args.vosviewer else None
        }
    }
    
    json_path = os.path.join(output_dir, "bibliometric_summary.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary_json, f, ensure_ascii=False, indent=2)
    print(f"    [+] JSON Summary: {json_path}")
    
    print("\n[SUCCESS] Bibliometric Science Mapping completed successfully!")


if __name__ == "__main__":
    main()
