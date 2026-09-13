#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
citation_visualizer_engine.py — Historical Direct Citation & Main Path Analysis Engine
AcademicSuite Skill #25: citation-network-visualizer
=====================================================================================
Automates Eugene Garfield's Algorithmic Historiography (HistCite chronomaps),
Local Citation Score (LCS) vs Global Citation Score (GCS) modeling, and
Hummon & Doreian's (1989) Main Path Analysis (Search Path Count - SPC) to
illuminate the historical intellectual backbone and paradigm shifts of scientific disciplines.

Exports:
  1. Dual 300-DPI Visual Figures: `citation_chronomap.png` & `main_path_trajectory.png`.
  2. 5-Sheet Excel Matrix: `citation_matrix.xlsx`.
  3. Publication-Grade Word Report: `Historiographic_Citation_Network_Report.docx`.
  4. Machine-Readable JSON Ledger: `citation_summary.json`.
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
# Data Ingestion & Validation
# ==============================================================================

def load_citation_data(input_path):
    """
    Ingest direct citation network payload from JSON or CSV.
    Returns: (articles, project_title, language, domain)
    """
    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    ext = os.path.splitext(input_path)[1].lower()
    
    if ext == '.json':
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            articles = data.get('articles', []) or data.get('studies', [])
            project_title = data.get('project_title') or (f"تحلیل مسیر استنادی: {data.get('query')}" if data.get('query') else 'Historical Direct Citation Analysis')
            language = data.get('language', 'fa')
            domain = data.get('domain', 'Academic Literature')
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
                        a['year'] = 2020
                else:
                    a['year'] = 2020
                if 'citations' not in a or not isinstance(a.get('citations'), (int, float)):
                    a['citations'] = a.get('citations') if isinstance(a.get('citations'), int) else 5
                if 'cited_doc_ids' not in a:
                    a['cited_doc_ids'] = []
            return articles, project_title, language, domain
        elif isinstance(data, list):
            return data, 'Historical Direct Citation Analysis', 'fa', 'Academic Literature'
    
    elif ext == '.csv':
        articles = []
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                doc_id = row.get('id') or f"DOC_{i+1:02d}"
                title = row.get('Title') or row.get('title') or f"Document {doc_id}"
                authors_str = row.get('Authors') or row.get('authors') or ""
                authors = [a.strip() for a in authors_str.split(';') if a.strip()]
                if not authors and ',' in authors_str:
                    authors = [a.strip() for a in authors_str.split(',') if a.strip()]
                
                journal = row.get('Journal') or row.get('Source title') or "Academic Journal"
                year_str = row.get('Year') or row.get('year') or "2020"
                try:
                    year = int(year_str)
                except ValueError:
                    year = 2020
                
                cit_str = row.get('Citations') or row.get('Cited by') or "0"
                try:
                    citations = int(cit_str)
                except ValueError:
                    citations = 0
                
                cited_str = row.get('cited_doc_ids') or row.get('Cited References') or ""
                cited_ids = [c.strip() for c in cited_str.split(';') if c.strip()]
                
                articles.append({
                    "id": doc_id,
                    "title": title,
                    "authors": authors,
                    "journal": journal,
                    "year": year,
                    "citations": citations,
                    "cited_doc_ids": cited_ids,
                    "keywords": []
                })
        return articles, 'Historical Direct Citation Analysis from CSV', 'fa', 'Scientific Domain'
    
    else:
        raise ValueError(f"Unsupported input file format: {ext}. Expected .json or .csv")


# ==============================================================================
# Computational Core: DAG Construction, LCS/GCS & Search Path Count (SPC)
# ==============================================================================

def build_citation_network(articles, main_path_type="global"):
    """
    Constructs the directed acyclic citation graph (DAG), computes LCS/GCS,
    Search Path Count (SPC) edge weights, and extracts the Main Path.
    Knowledge flows temporally: u -> v means u is cited by v (u precedes v).
    """
    doc_map = {a['id']: a for a in articles}
    
    # 1. Calculate Local Citation Score (LCS) and Local Cited References (LCR)
    # LCS(u): how many documents in this corpus cite u
    lcs_counter = Counter()
    lcr_counter = Counter()
    
    for a in articles:
        v_id = a['id']
        for u_id in a.get('cited_doc_ids', []):
            if u_id in doc_map:
                lcs_counter[u_id] += 1
                lcr_counter[v_id] += 1
    
    # 2. Build Directed Graph G (Historical Flow: u -> v)
    G = nx.DiGraph()
    for a in articles:
        u_id = a['id']
        gcs = a.get('citations', 0)
        lcs = lcs_counter[u_id]
        lcr = lcr_counter[u_id]
        ratio = round(lcs / max(1, gcs), 4)
        
        # Primary short label for diagrams (e.g. "Hayes (1999)")
        first_author = a.get('authors', ['Unknown'])[0].split(',')[0].strip() if a.get('authors') else 'Unknown'
        raw_year = a.get('year_ad') if a.get('year_ad') is not None else a.get('year', 2020)
        try:
            y_str = str(raw_year).strip()
            for f_d, e_d in zip('۰۱۲۳۴۵۶۷۸۹', '0123456789'):
                y_str = y_str.replace(f_d, e_d)
            year = int(y_str)
        except (ValueError, TypeError):
            year = 2020
        short_label = f"{first_author} ({year})"
        
        G.add_node(
            u_id,
            title=a.get('title', ''),
            authors=a.get('authors', []),
            journal=a.get('journal', ''),
            year=year,
            gcs=gcs,
            lcs=lcs,
            lcr=lcr,
            ratio=ratio,
            short_label=short_label
        )
    
    # Add directed temporal edges: u (cited) -> v (citing)
    for a in articles:
        v_id = a['id']
        v_year = a.get('year', 2020)
        for u_id in a.get('cited_doc_ids', []):
            if u_id in doc_map and u_id != v_id:
                u_year = doc_map[u_id].get('year', 2020)
                # Ensure causal temporal consistency: u_year <= v_year
                if u_year <= v_year:
                    G.add_edge(u_id, v_id)
                else:
                    # If anomalous year, add in correct temporal order
                    G.add_edge(v_id, u_id)
    
    # 3. Ensure Strict DAG (Break any feedback loops if present)
    if not nx.is_directed_acyclic_graph(G):
        cycles = list(nx.simple_cycles(G))
        for cycle in cycles:
            # remove the edge that goes backward in time or last edge
            u, v = cycle[0], cycle[1]
            if G.has_edge(u, v):
                G.remove_edge(u, v)
    
    # 4. Search Path Count (SPC) Computation via Topological Dynamic Programming
    topo_order = list(nx.topological_sort(G))
    
    # Number of paths from all sources to node u
    paths_from_sources = {}
    for node in topo_order:
        preds = list(G.predecessors(node))
        if not preds:
            paths_from_sources[node] = 1
        else:
            paths_from_sources[node] = sum(paths_from_sources[p] for p in preds)
    
    # Number of paths from node v to all sinks
    paths_to_sinks = {}
    for node in reversed(topo_order):
        succs = list(G.successors(node))
        if not succs:
            paths_to_sinks[node] = 1
        else:
            paths_to_sinks[node] = sum(paths_to_sinks[s] for s in succs)
    
    # Compute SPC weight for every edge (u, v)
    spc_weights = {}
    for u, v in G.edges():
        spc = paths_from_sources[u] * paths_to_sinks[v]
        spc_weights[(u, v)] = spc
        G[u][v]['spc'] = spc
    
    # Identify Source and Sink nodes
    sources = [n for n in G.nodes() if G.in_degree(n) == 0]
    sinks = [n for n in G.nodes() if G.out_degree(n) == 0]
    
    # 5. Extract Main Path
    main_path_nodes = []
    main_path_edges = []
    
    if main_path_type == "local":
        # Local Main Path: Greedy from source with max outgoing edge
        if sources:
            curr = max(sources, key=lambda s: max([G[s][v]['spc'] for v in G[s]] or [0]))
            main_path_nodes.append(curr)
            while G.out_degree(curr) > 0:
                succs = list(G.successors(curr))
                next_node = max(succs, key=lambda n: G[curr][n]['spc'])
                main_path_edges.append((curr, next_node))
                main_path_nodes.append(next_node)
                curr = next_node
    
    elif main_path_type == "key-route":
        # Key-Route Main Path: Anchored around overall max SPC edge
        if spc_weights:
            max_edge = max(spc_weights.items(), key=lambda x: x[1])[0]
            u_star, v_star = max_edge
            
            # Trace backward from u_star to source
            curr = u_star
            back_path = [curr]
            while G.in_degree(curr) > 0:
                preds = list(G.predecessors(curr))
                prev_node = max(preds, key=lambda p: G[p][curr]['spc'])
                back_path.append(prev_node)
                curr = prev_node
            back_path.reverse()
            
            # Trace forward from v_star to sink
            curr = v_star
            fwd_path = [curr]
            while G.out_degree(curr) > 0:
                succs = list(G.successors(curr))
                next_node = max(succs, key=lambda n: G[curr][n]['spc'])
                fwd_path.append(next_node)
                curr = next_node
            
            main_path_nodes = back_path + fwd_path
            for i in range(len(main_path_nodes) - 1):
                main_path_edges.append((main_path_nodes[i], main_path_nodes[i+1]))
        else:
            main_path_nodes = list(G.nodes())[:5]
    
    else:  # Default: Global Main Path (Cumulative Weight Maximization)
        # Dynamic programming for longest path on DAG with edge weight = SPC
        dist = {n: -1 for n in G.nodes()}
        parent = {n: None for n in G.nodes()}
        
        for s in sources:
            dist[s] = 0
            
        for u in topo_order:
            if dist[u] >= 0:
                for v in G.successors(u):
                    w = G[u][v]['spc']
                    if dist[u] + w > dist[v]:
                        dist[v] = dist[u] + w
                        parent[v] = u
        
        # Best sink
        if sinks:
            best_sink = max(sinks, key=lambda s: dist[s])
            if dist[best_sink] > 0:
                curr = best_sink
                while curr is not None:
                    main_path_nodes.append(curr)
                    curr = parent[curr]
                main_path_nodes.reverse()
                for i in range(len(main_path_nodes) - 1):
                    main_path_edges.append((main_path_nodes[i], main_path_nodes[i+1]))
            else:
                main_path_nodes = sources[:1]
        else:
            main_path_nodes = list(G.nodes())[:5]
    
    # 6. Node Ranking & Chronological Sorting
    ranked_nodes = []
    for n in G.nodes():
        d = G.nodes[n]
        is_main = (n in main_path_nodes)
        ranked_nodes.append({
            "id": n,
            "short_label": d['short_label'],
            "title": d['title'],
            "authors": d['authors'],
            "journal": d['journal'],
            "year": d['year'],
            "lcs": d['lcs'],
            "gcs": d['gcs'],
            "ratio": d['ratio'],
            "lcr": d['lcr'],
            "is_main_path": is_main,
            "in_degree": G.in_degree(n),
            "out_degree": G.out_degree(n)
        })
    
    # Sort by LCS descending, then Year
    ranked_nodes.sort(key=lambda x: (x['lcs'], x['gcs']), reverse=True)
    
    # Chronological sort
    chrono_nodes = sorted(ranked_nodes, key=lambda x: (x['year'], x['id']))
    
    return {
        "graph": G,
        "ranked_nodes": ranked_nodes,
        "chrono_nodes": chrono_nodes,
        "sources": sources,
        "sinks": sinks,
        "main_path_nodes": main_path_nodes,
        "main_path_edges": main_path_edges,
        "spc_weights": spc_weights,
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "graph_density": round(nx.density(G), 4)
    }


# ==============================================================================
# Visual Plotting: Chronomap & Main Path Trajectory (300 DPI)
# ==============================================================================

def generate_chronomap_plots(citation_data, output_dir, language='fa'):
    """
    Renders and exports:
      1. `citation_chronomap.png`: HistCite-style chronological citation network.
      2. `main_path_trajectory.png`: Isolated Main Path backbone trajectory.
    """
    G = citation_data['graph']
    chrono_nodes = citation_data['chrono_nodes']
    main_nodes = set(citation_data['main_path_nodes'])
    main_edges = set(citation_data['main_path_edges'])
    
    # --------------------------------------------------------------------------
    # Figure 1: HistCite Chronomap (Timeline along X-axis, vertical layer dispersion)
    # --------------------------------------------------------------------------
    plt.figure(figsize=(14, 9), dpi=300)
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Group nodes by year
    year_to_nodes = defaultdict(list)
    for n in chrono_nodes:
        year_to_nodes[n['year']].append(n['id'])
    
    # Assign deterministic (x, y) coordinates based on year and dispersion
    pos = {}
    years = sorted(year_to_nodes.keys())
    
    for y_val in years:
        nodes_in_year = year_to_nodes[y_val]
        num_in_year = len(nodes_in_year)
        for idx, nid in enumerate(nodes_in_year):
            x = y_val
            # Center around 0 vertically
            if num_in_year == 1:
                y = 0.0
            else:
                y = -((num_in_year - 1) / 2.0) * 1.4 + idx * 1.4
            pos[nid] = (x, y)
    
    # Separate Main Path vs Context edges
    other_edges = [e for e in G.edges() if e not in main_edges]
    
    # Draw context edges
    nx.draw_networkx_edges(
        G, pos, edgelist=other_edges,
        arrows=True, arrowstyle='-|>', arrowsize=10,
        edge_color='#94A3B8', width=1.0, alpha=0.45,
        connectionstyle="arc3,rad=0.12"
    )
    
    # Draw Main Path edges (highlighted in crimson)
    if main_edges:
        nx.draw_networkx_edges(
            G, pos, edgelist=list(main_edges),
            arrows=True, arrowstyle='-|>', arrowsize=16,
            edge_color='#DC2626', width=2.8, alpha=0.9,
            connectionstyle="arc3,rad=0.08"
        )
    
    # Draw nodes: sizing by LCS
    for nid, (x, y) in pos.items():
        node_data = G.nodes[nid]
        lcs = node_data['lcs']
        is_main = (nid in main_nodes)
        
        node_size = 350 + lcs * 140
        fill_color = '#EF4444' if is_main else '#3B82F6'
        edge_color = '#7F1D1D' if is_main else '#1E3A8A'
        
        plt.scatter(x, y, s=node_size, color=fill_color, edgecolors=edge_color, linewidth=1.5, zorder=5)
        
        # Label: Short label (e.g. Hayes (1999)) with bounding box
        label_text = node_data['short_label']
        text_color = '#7F1D1D' if is_main else '#0F172A'
        weight_font = 'bold' if is_main else 'normal'
        
        plt.text(
            x, y + 0.35, label_text,
            fontsize=8.0, fontweight=weight_font, ha='center', va='bottom',
            color=text_color, zorder=6,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#CBD5E1', alpha=0.85, linewidth=0.7)
        )
    
    # Set X-axis limits and labels
    min_year = min(years) - 1
    max_year = max(years) + 1
    plt.xlim(min_year, max_year)
    plt.xticks(years, [str(y) for y in years], fontsize=9, fontweight='bold', color='#1E293B', rotation=45)
    
    plt.yticks([])  # Hide Y ticks (spatial dispersion only)
    plt.grid(True, axis='x', linestyle=':', color='#CBD5E1', alpha=0.7)
    
    title_fa = "نگاشت زمانی تاریخ‌نگاری استنادات و خط سیر پارادایمی (HistCite Citation Chronomap)"
    title_en = "Historical Direct Citation Chronomap & Main Path (HistCite Framework)"
    plt.title(title_fa if language == 'fa' else title_en, fontsize=13, fontweight='bold', pad=18, color='#1E293B')
    
    # Custom Legend
    plt.scatter([], [], s=400, color='#EF4444', edgecolors='#7F1D1D', label='Main Path Backbone (مسیر اصلی)')
    plt.scatter([], [], s=300, color='#3B82F6', edgecolors='#1E3A8A', label='Contextual Citation (استناد بافتی)')
    plt.legend(loc='upper left', framealpha=0.9, fontsize=9.5)
    
    plt.tight_layout()
    chronomap_path = os.path.join(output_dir, "citation_chronomap.png")
    plt.savefig(chronomap_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # --------------------------------------------------------------------------
    # Figure 2: Isolated Main Path Trajectory (Sequential Milestone Timeline)
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    
    mp_nodes = citation_data['main_path_nodes']
    num_mp = len(mp_nodes)
    
    if num_mp > 1:
        x_coords = list(range(num_mp))
        y_coords = [0.0] * num_mp
        
        # Connect nodes with gradient flow line
        ax.plot(x_coords, y_coords, color='#DC2626', linewidth=3.5, zorder=2, alpha=0.8)
        
        for idx, nid in enumerate(mp_nodes):
            d = G.nodes[nid]
            lcs = d['lcs']
            node_size = 450 + lcs * 100
            
            ax.scatter(idx, 0, s=node_size, color='#EF4444', edgecolors='#991B1B', linewidth=2.0, zorder=4)
            
            # Step number
            ax.text(idx, 0, f"#{idx+1}", ha='center', va='center', fontsize=9, fontweight='bold', color='white', zorder=5)
            
            # Top annotation: Short label & Year
            ax.annotate(
                f"{d['short_label']}\nLCS={lcs} | GCS={d['gcs']}",
                (idx, 0), xytext=(0, 24), textcoords="offset points",
                ha='center', fontsize=8.5, fontweight='bold', color='#1E293B',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#F8FAFC', edgecolor='#E2E8F0', alpha=0.9)
            )
            
            # Bottom annotation: Title excerpt
            title_snip = (d['title'][:32] + '...') if len(d['title']) > 32 else d['title']
            ax.annotate(
                title_snip,
                (idx, 0), xytext=(0, -32), textcoords="offset points",
                ha='center', fontsize=7.5, color='#475569',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#CBD5E1', alpha=0.8)
            )
        
        ax.set_xlim(-0.6, num_mp - 0.4)
        ax.set_ylim(-1.5, 1.5)
        ax.axis('off')
    
    title_mp_fa = "مسیر اصلی دانش و زنجیره تکامل پارادایمی (Hummon & Doreian Main Path Trajectory)"
    title_mp_en = "Scientific Main Path Trajectory (SPC Backbone Sequence)"
    ax.set_title(title_mp_fa if language == 'fa' else title_mp_en, fontsize=12, fontweight='bold', pad=25, color='#1E293B')
    
    plt.tight_layout()
    trajectory_path = os.path.join(output_dir, "main_path_trajectory.png")
    plt.savefig(trajectory_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return chronomap_path, trajectory_path


# ==============================================================================
# Excel 5-Sheet Matrix Builder
# ==============================================================================

def export_excel_matrix(citation_data, articles, domain, output_dir, language='fa'):
    """
    Exports 5-sheet citation matrix workbook:
      Sheet 1: Overview & Chronology (21 chars)
      Sheet 2: LCS vs GCS Ranking (18 chars)
      Sheet 3: Direct Citation Adjacency (24 chars)
      Sheet 4: Main Path Trajectory (19 chars)
      Sheet 5: Historical Lineages (19 chars)
    """
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Overview & Chronology"
    
    header_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Arial", size=10)
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    
    # --------------------------------------------------------------------------
    # Sheet 1: Overview & Chronology
    # --------------------------------------------------------------------------
    ws1.append(["Metric / Parameter", "Value / Description", "Bibliometric Interpretation"])
    ws1.append(["Analyzed Scientific Domain", domain, "Field-specific citation network boundary"])
    ws1.append(["Total Landmark Documents", citation_data['total_nodes'], "Core publications in the citation DAG"])
    ws1.append(["Direct Citation Links (Edges)", citation_data['total_edges'], "Unidirectional citation linkages"])
    ws1.append(["Network Density", citation_data['graph_density'], "Internal structural cohesion of subfield"])
    
    years = [a['year'] for a in articles if a.get('year')]
    timespan_str = f"{min(years)} - {max(years)}" if years else "N/A"
    ws1.append(["Historical Timespan", timespan_str, "Chronological depth of intellectual lineage"])
    ws1.append(["Root Ancestors (Sources)", len(citation_data['sources']), ", ".join(citation_data['sources'])])
    ws1.append(["Empirical Sinks (Leaves)", len(citation_data['sinks']), ", ".join(citation_data['sinks'])])
    ws1.append(["Main Path Sequence Length", len(citation_data['main_path_nodes']), "Number of milestone papers on backbone"])
    ws1.append([])
    
    ws1.append(["Document ID", "Author & Year", "Title", "Journal", "Year", "LCS", "GCS", "LCS/GCS", "On Main Path"])
    for cell in ws1[ws1.max_row]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    for n in citation_data['chrono_nodes']:
        auth_str = ", ".join(n.get('authors', []))
        is_mp = "YES" if n['is_main_path'] else "No"
        ws1.append([
            n['id'], n['short_label'], n['title'], n['journal'], n['year'],
            n['lcs'], n['gcs'], n['ratio'], is_mp
        ])
    
    # --------------------------------------------------------------------------
    # Sheet 2: LCS vs GCS Ranking
    # --------------------------------------------------------------------------
    ws2 = wb.create_sheet(title="LCS vs GCS Ranking")
    ws2.append(["Rank (LCS)", "ID", "Author & Year", "Title", "LCS (Local Citations)", "GCS (Global Citations)", "Ratio (LCS/GCS)", "LCR (Local References)", "Scientific Status"])
    for cell in ws2[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    for rank, n in enumerate(citation_data['ranked_nodes'], start=1):
        status = "Seminal Cornerstone" if n['lcs'] >= 5 else ("Core Influence" if n['lcs'] >= 2 else "Emerging / Peripheral")
        ws2.append([
            rank, n['id'], n['short_label'], n['title'],
            n['lcs'], n['gcs'], n['ratio'], n['lcr'], status
        ])
    
    # --------------------------------------------------------------------------
    # Sheet 3: Direct Citation Adjacency
    # --------------------------------------------------------------------------
    ws3 = wb.create_sheet(title="Direct Citation Adjacency")
    all_ids = [n['id'] for n in citation_data['chrono_nodes']]
    G = citation_data['graph']
    
    header_row = ["Cited \\ Citing"] + all_ids
    ws3.append(header_row)
    for cell in ws3[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    for u in all_ids:
        row = [u]
        for v in all_ids:
            row.append(1 if G.has_edge(u, v) else 0)
        ws3.append(row)
    
    # --------------------------------------------------------------------------
    # Sheet 4: Main Path Trajectory
    # --------------------------------------------------------------------------
    ws4 = wb.create_sheet(title="Main Path Trajectory")
    ws4.append(["Step", "Predecessor (From)", "Successor (To)", "Transition Years", "SPC Edge Weight", "Cumulative Path Weight", "Landmark Description"])
    for cell in ws4[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    mp_edges = citation_data['main_path_edges']
    cum_spc = 0
    for step_idx, (u, v) in enumerate(mp_edges, start=1):
        spc = G[u][v].get('spc', 1)
        cum_spc += spc
        u_data = G.nodes[u]
        v_data = G.nodes[v]
        trans_years = f"{u_data['year']} -> {v_data['year']}"
        desc = f"{u_data['short_label']} lays groundwork for {v_data['short_label']}"
        ws4.append([step_idx, u_data['short_label'], v_data['short_label'], trans_years, spc, cum_spc, desc])
    
    # --------------------------------------------------------------------------
    # Sheet 5: Historical Lineages
    # --------------------------------------------------------------------------
    ws5 = wb.create_sheet(title="Historical Lineages")
    ws5.append(["Node ID", "Author & Year", "In-Degree (Cited by)", "Out-Degree (Cites)", "Topological Role", "Descendant Reach (Sinks)"])
    for cell in ws5[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    for n in citation_data['chrono_nodes']:
        nid = n['id']
        in_deg = n['in_degree']
        out_deg = n['out_degree']
        if in_deg == 0 and out_deg > 0:
            role = "Root Source / Foundational Inception"
        elif in_deg > 0 and out_deg == 0:
            role = "Empirical Sink / Recent Frontier"
        elif in_deg > 1 and out_deg > 1:
            role = "Conceptual Hub / Paradigm Bridge"
        elif in_deg > 1:
            role = "Convergence Synthesizer"
        elif out_deg > 1:
            role = "Divergence Branching Point"
        else:
            role = "Linear Conduit"
        
        ws5.append([nid, n['short_label'], in_deg, out_deg, role, n['lcs']])
    
    # Apply borders, fonts & auto column widths
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
    
    excel_path = os.path.join(output_dir, "citation_matrix.xlsx")
    wb.save(excel_path)
    return excel_path


# ==============================================================================
# Publication Word Report Compiler (OpenXML BiDi RTL / APA 7)
# ==============================================================================

def export_word_report(citation_data, project_title, domain, chronomap_img, trajectory_img, output_dir, language='fa'):
    """
    Compiles defense-ready APA 7th Edition Word document:
    `Historiographic_Citation_Network_Report.docx`.
    """
    doc = docx.Document()
    is_bidi = (language == 'fa')
    
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
    
    # Title & Subtitle
    doc_title = project_title or (
        "گزارش تاریخ‌نگاری علم، نگاشت زمانی استنادات و تحلیل مسیر اصلی دانش (Main Path Analysis)" if is_bidi
        else "Algorithmic Historiography, Citation Chronomapping & Main Path Analysis Report"
    )
    add_styled_paragraph(doc, doc_title, bold=True, size_pt=18, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12,
                         font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    sub_text = (
        f"تدوین‌شده بر اساس چهارچوب تاریخ‌نگاری الگوریتمی گارفیلد (HistCite) و مدل مسیر اصلی هامون و دورین (۱۹۸۹) | تاریخ: {datetime.now().strftime('%Y-%m-%d')}"
        if is_bidi else
        f"Formulated under Garfield's HistCite Framework and Hummon & Doreian's (1989) Main Path Analysis | Generated: {datetime.now().strftime('%Y-%m-%d')}"
    )
    add_styled_paragraph(doc, sub_text, italic=True, size_pt=10.5, color_rgb=(100, 116, 139),
                         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18,
                         font_fa="B Nazanin", font_en="Times New Roman", is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 1: Executive Summary & Historical Lineage
    # --------------------------------------------------------------------------
    h1_text = "۱. چکیده مدیریتی و ساختار تبارشناسی دانش" if is_bidi else "1. Executive Summary & Historiographic Lineage Overview"
    add_styled_paragraph(doc, h1_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    sum_p1 = (
        f"تحلیل تاریخ‌نگاری حاضر به بررسی ساختار استنادی مستقیم تعداد {citation_data['total_nodes']} اثر برجسته در حوزه «{domain}» "
        f"در قالب یک گراف جهت‌دار بدون دور (DAG) با {citation_data['total_edges']} پیوند استنادی پرداخته است. "
        f"برخلاف تحلیل‌های هم‌استنادی سنتی، تاریخ‌نگاری الگوریتمی (Algorithmic Historiography) و مدل وزن‌دهی مسیر جستجو (SPC) "
        f"امکان ردیابی دقیق زنجیره تکاملی پارادایم‌ها، کشف نقطه‌عطف‌های انشعاب مفاهیم و شناسایی ستون فقرات اصلی دانش (Main Path Backbone) را فراهم می‌آورند."
        if is_bidi else
        f"This historiographic investigation models the direct citation structure of {citation_data['total_nodes']} milestone works in '{domain}', "
        f"forming a Directed Acyclic Graph (DAG) with {citation_data['total_edges']} citation links. "
        f"Unlike standard co-citation mapping, algorithmic historiography and Search Path Count (SPC) edge weighting delineate the exact chronological lineage, "
        f"paradigm shifts, and intellectual backbone trajectory from root inception to the empirical frontier."
    )
    add_styled_paragraph(doc, sum_p1, size_pt=11, space_after=10, is_bidi=is_bidi)
    
    # Table 1: Macro-metrics
    t1_caption = "جدول ۱. شاخص‌های ساختاری گراف استناد مستقیم و تبارشناسی تاریخی" if is_bidi else "Table 1. Structural Properties of Direct Citation Network"
    add_styled_paragraph(doc, t1_caption, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=4, is_bidi=is_bidi)
    
    t1 = doc.add_table(rows=6, cols=2)
    make_table_apa7(t1, is_bidi=is_bidi)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    years = [n['year'] for n in citation_data['chrono_nodes']]
    t_span = f"{min(years)} - {max(years)}" if years else "N/A"
    
    t1_data = [
        ("تعداد آثار و مقالات کلیدی در شبکه" if is_bidi else "Total Milestone Publications", str(citation_data['total_nodes'])),
        ("محدوده زمانی تاریخ‌نگاری (Timespan)" if is_bidi else "Historical Timespan", t_span),
        ("تعداد پیوندهای استنادی مستقیم (Directed Edges)" if is_bidi else "Direct Citation Links (Edges)", str(citation_data['total_edges'])),
        ("چگالی شبکه استنادی (Network Density)" if is_bidi else "Network Density", str(citation_data['graph_density'])),
        ("تعداد ریشه‌های آغازین (Source Ancestors)" if is_bidi else "Foundational Root Sources", str(len(citation_data['sources']))),
        ("تعداد ایستگاه‌های مسیر اصلی دانش (Main Path Nodes)" if is_bidi else "Main Path Milestones Length", str(len(citation_data['main_path_nodes'])))
    ]
    
    for r_i, (k, v) in enumerate(t1_data):
        format_cell_text(t1.rows[r_i].cells[0], k, bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_bidi)
        format_cell_text(t1.rows[r_i].cells[1], v, bold=False, size_pt=10, is_bidi=is_bidi)
        set_cell_margins(t1.rows[r_i].cells[0])
        set_cell_margins(t1.rows[r_i].cells[1])
        if r_i % 2 == 1:
            set_cell_shading(t1.rows[r_i].cells[0], "F8FAFC")
            set_cell_shading(t1.rows[r_i].cells[1], "F8FAFC")
    
    add_styled_paragraph(doc, "", space_after=12, is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 2: Seminal Works & LCS vs GCS
    # --------------------------------------------------------------------------
    h2_text = "۲. رتبه‌بندی استناد محلی (LCS) در برابر استناد جهانی (GCS)" if is_bidi else "2. Local Citation Score (LCS) vs. Global Citation Score (GCS)"
    add_styled_paragraph(doc, h2_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    lcs_desc = (
        f"شاخص استناد محلی (LCS) تعداد دفعاتی را می‌سنجد که یک سند مشخص توسط سایر پژوهش‌های درون همین حوزه مورد استناد قرار گرفته است. "
        f"در مقابل، استناد جهانی (GCS) نفوذ مقاله در کل پایگاه‌های بین‌المللی را بازتاب می‌دهد. نسبت بالای LCS به GCS نشان‌دهنده "
        f"تخصصی بودن سند در تبیین پایه‌های مفهومی این پارادایم است. آثار صدرنشین در جدول زیر به عنوان سنگ‌بناهای اجتناب‌ناپذیر این جریان علمی شناخته می‌شوند."
        if is_bidi else
        f"Local Citation Score (LCS) measures the internal intellectual pull within the immediate domain, whereas Global Citation Score (GCS) "
        f"reflects broader interdisciplinary prestige. High LCS/GCS ratio highlights works that function as indispensable foundations of the local paradigm."
    )
    add_styled_paragraph(doc, lcs_desc, size_pt=11, space_after=10, is_bidi=is_bidi)
    
    # Table 2: Top LCS papers
    t2_caption = "جدول ۲. آثار صدرنشین بر اساس استناد محلی (LCS) و نسبت تأثیرگذاری پارادایمی" if is_bidi else "Table 2. Top Seminal Works Ranked by Local Citation Score (LCS)"
    add_styled_paragraph(doc, t2_caption, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=4, is_bidi=is_bidi)
    
    top_lcs = citation_data['ranked_nodes'][:8]
    t2 = doc.add_table(rows=len(top_lcs) + 1, cols=6)
    make_table_apa7(t2, is_bidi=is_bidi)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    t2_headers = ["نویسنده و سال", "عنوان اثر", "سال", "LCS", "GCS", "نسبت LCS/GCS"] if is_bidi else ["Author & Year", "Title", "Year", "LCS", "GCS", "Ratio"]
    for c_i, h in enumerate(t2_headers):
        format_cell_text(t2.rows[0].cells[c_i], h, bold=True, size_pt=10, color_rgb=(255, 255, 255), is_bidi=is_bidi)
        set_cell_shading(t2.rows[0].cells[c_i], "1A365D")
        set_cell_margins(t2.rows[0].cells[c_i])
    
    for r_i, n in enumerate(top_lcs, start=1):
        row = t2.rows[r_i]
        format_cell_text(row.cells[0], n['short_label'], bold=True, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_bidi)
        format_cell_text(row.cells[1], n['title'][:40] + '...', bold=False, size_pt=9.0, align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_bidi)
        format_cell_text(row.cells[2], n['year'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[3], n['lcs'], bold=True, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[4], n['gcs'], bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[5], f"{n['ratio']:.3f}", bold=False, size_pt=9.5, is_bidi=is_bidi)
        for cell in row.cells:
            set_cell_margins(cell)
        if r_i % 2 == 0:
            for cell in row.cells:
                set_cell_shading(cell, "F8FAFC")
    
    add_styled_paragraph(doc, "", space_after=12, is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 3: Main Path Analysis & Historical Trajectory
    # --------------------------------------------------------------------------
    h3_text = "۳. تحلیل مسیر اصلی دانش و توالی نقاط عطف پارادایمی (Main Path Analysis)" if is_bidi else "3. Main Path Analysis & Historical Trajectory"
    add_styled_paragraph(doc, h3_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    mp_desc = (
        f"مسیر اصلی سراسری (Global Main Path) بر پایه شمارش مسیر جستجو (Search Path Count - SPC) بزرگ‌ترین جریان دانش میان ریشه‌ها و شاخه‌های معاصر را ردیابی می‌کند. "
        f"در این پیکره، مسیر اصلی با {len(citation_data['main_path_nodes'])} ایستگاه کلیدی شناسایی شد که توالی تاریخی زیر را نشان می‌دهد:\n"
    )
    # create sequential bullet text
    for i, nid in enumerate(citation_data['main_path_nodes']):
        node_d = citation_data['graph'].nodes[nid]
        mp_desc += f"  {i+1}. {node_d['short_label']}: {node_d['title'][:65]} (LCS={node_d['lcs']})\n"
    
    add_styled_paragraph(doc, mp_desc, size_pt=10.5, space_after=10, is_bidi=is_bidi)
    
    # Table 3: Main Path Transitions
    t3_caption = "جدول ۳. ایستگاه‌های مسیر اصلی تکامل دانش و وزن پیوند جستجو (SPC)" if is_bidi else "Table 3. Main Path Evolutionary Backbone Transitions"
    add_styled_paragraph(doc, t3_caption, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=4, is_bidi=is_bidi)
    
    mp_edges = citation_data['main_path_edges']
    t3 = doc.add_table(rows=len(mp_edges) + 1, cols=5)
    make_table_apa7(t3, is_bidi=is_bidi)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    t3_headers = ["گام", "اثر مبدأ (Predecessor)", "اثر مقصد (Successor)", "دوره زمانی", "وزن SPC"] if is_bidi else ["Step", "Predecessor", "Successor", "Timespan", "SPC Weight"]
    for c_i, h in enumerate(t3_headers):
        format_cell_text(t3.rows[0].cells[c_i], h, bold=True, size_pt=10, color_rgb=(255, 255, 255), is_bidi=is_bidi)
        set_cell_shading(t3.rows[0].cells[c_i], "1A365D")
        set_cell_margins(t3.rows[0].cells[c_i])
    
    G = citation_data['graph']
    for step_i, (u, v) in enumerate(mp_edges, start=1):
        row = t3.rows[step_i]
        u_d = G.nodes[u]
        v_d = G.nodes[v]
        spc = G[u][v].get('spc', 1)
        
        format_cell_text(row.cells[0], f"#{step_i}", bold=True, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[1], u_d['short_label'], bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_bidi)
        format_cell_text(row.cells[2], v_d['short_label'], bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_bidi)
        format_cell_text(row.cells[3], f"{u_d['year']} -> {v_d['year']}", bold=False, size_pt=9.5, is_bidi=is_bidi)
        format_cell_text(row.cells[4], str(spc), bold=True, size_pt=9.5, is_bidi=is_bidi)
        for cell in row.cells:
            set_cell_margins(cell)
        if step_i % 2 == 0:
            for cell in row.cells:
                set_cell_shading(cell, "F8FAFC")
    
    add_styled_paragraph(doc, "", space_after=16, is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 4: High-Resolution Embedded Visualizations (300 DPI)
    # --------------------------------------------------------------------------
    h4_text = "۴. مصورسازی نگاشت زمانی استنادات و مسیر اصلی (Visual Historiography Maps)" if is_bidi else "4. Historiographic Visualizations & Main Path Chronomaps"
    add_styled_paragraph(doc, h4_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    if os.path.exists(chronomap_img):
        fig1_cap = "شکل ۱. نگاشت زمانی استنادات مستقیم و برجسته‌سازی مسیر اصلی تکامل دانش (HistCite Chronomap)" if is_bidi else "Figure 1. Historical Direct Citation Chronomap & Main Path Backbone"
        add_styled_paragraph(doc, fig1_cap, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                             align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6, is_bidi=is_bidi)
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.add_run().add_picture(chronomap_img, width=Inches(6.2))
        add_styled_paragraph(doc, "", space_after=14, is_bidi=is_bidi)
    
    if os.path.exists(trajectory_img):
        fig2_cap = "شکل ۲. زنجیره توالی مسیر اصلی و نقاط عطف تکامل نظری (Sequential Main Path Backbone)" if is_bidi else "Figure 2. Sequential Main Path Trajectory Milestones"
        add_styled_paragraph(doc, fig2_cap, bold=True, italic=True, size_pt=10.5, color_rgb=(43, 58, 74),
                             align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6, is_bidi=is_bidi)
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.add_run().add_picture(trajectory_img, width=Inches(6.2))
        add_styled_paragraph(doc, "", space_after=14, is_bidi=is_bidi)
    
    # --------------------------------------------------------------------------
    # Section 5: Theoretical Implications for Thesis Chapter 2
    # --------------------------------------------------------------------------
    h5_text = "۵. دلالت‌های ساختاری برای نگارش فصل دوم رساله (مبانی نظری و پیشینه)" if is_bidi else "5. Methodological & Theoretical Directives for Chapter 2"
    add_styled_paragraph(doc, h5_text, bold=True, size_pt=14, color_rgb=(26, 54, 93),
                         align=WD_ALIGN_PARAGRAPH.RIGHT if is_bidi else WD_ALIGN_PARAGRAPH.LEFT,
                         space_after=8, font_fa="B Titr", font_en="Times New Roman", is_bidi=is_bidi)
    
    directives = (
        f"یافته‌های تحلیل تاریخ‌نگاری حاضر جهت تدوین اصولی فصل دوم رساله راهبردهای زیر را دیکته می‌کند:\n"
        f"۱. تبارشناسی نظری (Theoretical Lineage): بررسی مبانی باید از آثار ریشه‌ای مسیر اصلی آغاز شده و نشان دهد که چگونه مفاهیم اولیه با عبور از ایستگاه‌های میانی تکامل یافته‌اند.\n"
        f"۲. مستندسازی پیوندها: در نگارش پیشینه، استناد به آثار دارای بالاترین LCS (مانند آثار کلاستر میانی) ضروری است، چرا که نشان‌دهنده احاطه دانشجو بر شاکله بنیادین پارادایم است.\n"
        f"۳. تبیین خلاء پژوهشی در ایستگاه‌های متأخر: نوآوری پژوهش باید در امتداد آخرین نقطه مسیر اصلی (ایستگاه‌های نهایی) تعریف شود تا اتصال مستقیم رساله با افق جاری علم اثبات گردد."
        if is_bidi else
        f"The algorithmic historiography yields three core structural directives for Chapter 2 synthesis:\n"
        f"1. Theoretical Lineage: Historical review must trace from root ancestors along the Main Path to document intellectual evolution.\n"
        f"2. Foundation Grounding: Citing high-LCS seminal cornerstones is non-negotiable to establish scholarly mastery.\n"
        f"3. Research Gap Positioning: The thesis novelty must dock directly onto the terminal milestones of the Main Path."
    )
    add_styled_paragraph(doc, directives, size_pt=11, space_after=12, is_bidi=is_bidi)
    
    file_name = "Historiographic_Citation_Network_Report.docx"
    doc_path = os.path.join(output_dir, file_name)
    doc.save(doc_path)
    return doc_path


# ==============================================================================
# Master CLI Controller
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Historical Direct Citation & Main Path Analysis Engine (AcademicSuite Skill #25)"
    )
    parser.add_argument("-i", "--input", help="Path to citation network file (.json or .csv)")
    parser.add_argument("-o", "--output-dir", default=".", help="Directory to save generated outputs")
    parser.add_argument("-l", "--language", default="fa", choices=["fa", "en"], help="Report language: 'fa' (Persian, default) or 'en'")
    parser.add_argument("--main-path", default="global", choices=["global", "local", "key-route"],
                        help="Main Path traversal algorithm (default: global)")
    parser.add_argument("--title", help="Custom project title for the report")
    
    args = parser.parse_args()
    
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Data Ingestion
    if args.input:
        input_file = os.path.abspath(args.input)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        skill_root = os.path.dirname(script_dir)
        default_sample = os.path.join(skill_root, "examples", "sample_citation_network_payload.json")
        if os.path.exists(default_sample):
            input_file = default_sample
        else:
            raise FileNotFoundError("No input file supplied and sample payload not found.")
    
    print(f"[*] Ingesting direct citation data: {input_file}")
    articles, file_title, file_lang, domain = load_citation_data(input_file)
    
    project_title = args.title or file_title
    language = args.language or file_lang or 'fa'
    
    print(f"[*] Loaded {len(articles)} documents in domain: '{domain}'")
    
    # 2. Build DAG & Compute Search Path Count (SPC)
    print(f"[*] Building citation DAG and running Main Path Analysis ({args.main_path})...")
    citation_data = build_citation_network(articles, main_path_type=args.main_path)
    
    print(f"[*] Citation DAG generated: {citation_data['total_nodes']} nodes, {citation_data['total_edges']} edges.")
    print(f"    [+] Foundational Sources: {len(citation_data['sources'])} | Sinks: {len(citation_data['sinks'])}")
    print(f"    [+] Main Path Length: {len(citation_data['main_path_nodes'])} milestones.")
    
    # 3. Generate 300-DPI Visual Plots
    print(f"[*] Rendering 300-DPI chronomap and main path plots...")
    chrono_img, traj_img = generate_chronomap_plots(citation_data, output_dir, language=language)
    print(f"    [+] Chronomap: {chrono_img}")
    print(f"    [+] Trajectory: {traj_img}")
    
    # 4. Export 5-Sheet Excel Matrix
    print(f"[*] Exporting 5-sheet Excel matrix...")
    excel_path = export_excel_matrix(citation_data, articles, domain, output_dir, language=language)
    print(f"    [+] Excel Matrix: {excel_path}")
    
    # 5. Compile Publication Word Report
    print(f"[*] Compiling APA 7th Edition Word report...")
    doc_path = export_word_report(citation_data, project_title, domain, chrono_img, traj_img, output_dir, language=language)
    print(f"    [+] Word Report: {doc_path}")
    
    # 6. Export Machine-Readable JSON Ledger
    summary_json = {
        "project_title": project_title,
        "language": language,
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "total_documents": citation_data['total_nodes'],
        "total_edges": citation_data['total_edges'],
        "graph_density": citation_data['graph_density'],
        "main_path_type": args.main_path,
        "main_path_sequence": citation_data['main_path_nodes'],
        "top_seminal_works": citation_data['ranked_nodes'][:10],
        "artifacts": {
            "word_report": os.path.basename(doc_path),
            "excel_matrix": os.path.basename(excel_path),
            "chronomap_image": os.path.basename(chrono_img),
            "main_path_image": os.path.basename(traj_img)
        }
    }
    
    json_path = os.path.join(output_dir, "citation_summary.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary_json, f, ensure_ascii=False, indent=2)
    print(f"    [+] JSON Summary: {json_path}")
    
    print("\n[SUCCESS] Historiographic Citation Analysis & Main Path completed successfully!")


if __name__ == "__main__":
    main()
