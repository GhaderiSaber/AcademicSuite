#!/usr/bin/env python3
"""
Presentation Schema & Truth Model (persian-defense-presentation-builder v3.0.0)
=============================================================================
Defines the intermediate slide specification, Research Truth Model,
color palettes, and layout family classifications for 16:9 defense presentations.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from pptx.dml.color import RGBColor

# ---------------------------------------------------------------------------
# Visual Themes & Design Tokens (16:9 Widescreen: 13.333" x 7.5")
# ---------------------------------------------------------------------------
PALETTES: Dict[str, Dict[str, RGBColor]] = {
    # 1. Official Academic Navy (Formal Defense Light Mode - University Hall Standard)
    "academic_navy": {
        "primary": RGBColor(13, 32, 64),           # Deep Academic Navy #0D2040 (Titles & Accents)
        "secondary": RGBColor(30, 62, 98),         # Classic University Navy #1E3E62
        "accent": RGBColor(217, 119, 6),           # Warm Amber Gold #D97706
        "accent_light": RGBColor(254, 243, 199),   # Soft Gold Tint #FEF3C7
        "accent_dark": RGBColor(180, 83, 9),       # Deep Gold #B45309
        "emerald": RGBColor(5, 150, 105),          # Forest Emerald #059669
        "emerald_light": RGBColor(209, 250, 229),  # Soft Mint Tint #D1FAE5
        "bg_slide": RGBColor(248, 250, 252),       # High-Legibility Off-White Paper #F8FAFC
        "card_bg": RGBColor(255, 255, 255),        # Crisp Pure White Card #FFFFFF
        "card_border": RGBColor(226, 232, 240),    # Soft Slate Border #E2E8F0
        "card_border_gold": RGBColor(217, 119, 6), # Gold Border #D97706
        "text_dark": RGBColor(15, 23, 42),         # Deep High-Contrast Slate #0F172A
        "text_body": RGBColor(51, 65, 85),         # Highly Legible Body Slate #334155
        "text_muted": RGBColor(100, 116, 139),     # Muted Slate 500 #64748B
        "text_light": RGBColor(255, 255, 255),     # Crisp White for Dark Cards/Headers #FFFFFF
        "tbl_header": RGBColor(13, 32, 64),        # Navy Header #0D2040
        "tbl_stripe": RGBColor(241, 245, 249),     # Slate Stripe #F1F5F9
        "badge_bg": RGBColor(238, 242, 255),       # Soft Indigo Badge Fill #EEF2FF
        "badge_border": RGBColor(199, 210, 254),   # Soft Indigo Border #C7D2FE
        "badge_text": RGBColor(30, 62, 98),        # Navy Badge Text #1E3E62
        "cover_bg": RGBColor(13, 32, 64),          # Prestigious Dark Navy Cover #0D2040
        "cover_card": RGBColor(27, 49, 87),        # Translucent Navy Cover Card #1B3157
        "cover_border": RGBColor(45, 74, 122),     # Border #2D4A7A
        "danger": RGBColor(220, 38, 38),           # Coral Red #DC2626
        "danger_light": RGBColor(254, 242, 242)    # #FEF2F2
    },
    # 2. Modern Academic Dark (Sleek Glassmorphic & High-Contrast Monitor Dark Mode)
    "academic_dark": {
        "primary": RGBColor(248, 250, 252),        # Crisp White #F8FAFC (Title & Main)
        "secondary": RGBColor(96, 165, 250),       # Light Academic Sapphire #60A5FA
        "accent": RGBColor(245, 158, 11),          # Warm Amber Gold #F59E0B
        "accent_light": RGBColor(254, 243, 199),   # Soft Gold Tint #FEF3C7
        "accent_dark": RGBColor(217, 119, 6),      # Deep Warm Amber #D97706
        "emerald": RGBColor(16, 185, 129),         # Forest Emerald #10B981
        "emerald_light": RGBColor(209, 250, 229),  # Soft Mint Tint #ECFDF5
        "bg_slide": RGBColor(7, 13, 31),           # Modern Dark Midnight Navy #070D1F
        "card_bg": RGBColor(19, 32, 66),           # Deep Slate Navy Card #132042
        "card_border": RGBColor(37, 54, 98),       # Subtle Indigo/Slate Border #253662
        "card_border_gold": RGBColor(245, 158, 11),# Gold Border #F59E0B
        "text_dark": RGBColor(248, 250, 252),      # Text on Cards (Crisp White)
        "text_body": RGBColor(203, 213, 225),      # Slate 300 #CBD5E1
        "text_muted": RGBColor(148, 163, 184),     # Slate 400 #94A3B8
        "text_light": RGBColor(255, 255, 255),     # Crisp White #FFFFFF
        "tbl_header": RGBColor(29, 46, 94),        # Header Blue #1D2E5E
        "tbl_stripe": RGBColor(13, 23, 51),        # Stripe Navy #0D1733
        "badge_bg": RGBColor(24, 39, 79),          # Badge Fill
        "badge_border": RGBColor(59, 130, 246),    # Badge Border #3B82F6
        "badge_text": RGBColor(96, 165, 250),      # Badge Text #60A5FA
        "cover_bg": RGBColor(7, 13, 31),           # Midnight Obsidian #070D1F
        "cover_card": RGBColor(19, 32, 66),        # Translucent Slate Card #132042
        "cover_border": RGBColor(37, 54, 98),      # Slate Hairline #253662
        "danger": RGBColor(239, 68, 68),           # Coral Red #EF4444
        "danger_light": RGBColor(127, 29, 29)
    },
    # 3. Emerald Slate (Life Sciences, Healthcare, & Natural Science Light Mode)
    "emerald_slate": {
        "primary": RGBColor(19, 78, 74),           # Deep Forest Emerald #134E4A
        "secondary": RGBColor(15, 118, 110),       # Teal #0F766E
        "accent": RGBColor(5, 150, 105),           # Forest Green #059669
        "accent_light": RGBColor(209, 250, 229),   # Mint Tint #D1FAE5
        "accent_dark": RGBColor(4, 120, 87),       # Dark Forest #047857
        "emerald": RGBColor(5, 150, 105),
        "emerald_light": RGBColor(209, 250, 229),
        "bg_slide": RGBColor(240, 253, 244),       # Soft Mint Off-White #F0FDF4
        "card_bg": RGBColor(255, 255, 255),        # Crisp Pure White #FFFFFF
        "card_border": RGBColor(209, 250, 229),    # Soft Mint Border #D1FAE5
        "card_border_gold": RGBColor(5, 150, 105),
        "text_dark": RGBColor(19, 42, 31),         # Deep Forest Slate #132A1F
        "text_body": RGBColor(51, 65, 85),         # Slate 700 #334155
        "text_muted": RGBColor(75, 85, 99),        # Gray 600 #4B5563
        "text_light": RGBColor(255, 255, 255),
        "tbl_header": RGBColor(19, 78, 74),
        "tbl_stripe": RGBColor(236, 253, 245),
        "badge_bg": RGBColor(236, 253, 245),
        "badge_border": RGBColor(167, 243, 208),
        "badge_text": RGBColor(4, 120, 87),
        "cover_bg": RGBColor(12, 35, 33),          # Deep Pine Cover #0C2321
        "cover_card": RGBColor(19, 52, 49),
        "cover_border": RGBColor(30, 75, 71),
        "danger": RGBColor(190, 18, 60),
        "danger_light": RGBColor(255, 241, 242)
    },
    # 4. Royal Burgundy (Humanities, Law, & Historical Arts Light Mode)
    "royal_burgundy": {
        "primary": RGBColor(74, 14, 23),           # Deep Burgundy #4A0E17
        "secondary": RGBColor(136, 19, 55),        # Rose Wine #881337
        "accent": RGBColor(197, 160, 89),          # Royal Gold #C5A059
        "accent_light": RGBColor(254, 243, 199),   # Pale Gold Tint #FEF3C7
        "accent_dark": RGBColor(180, 83, 9),       # Dark Amber #B45309
        "emerald": RGBColor(5, 150, 105),
        "emerald_light": RGBColor(209, 250, 229),
        "bg_slide": RGBColor(255, 251, 235),       # Soft Warm Cream #FFFBEB
        "card_bg": RGBColor(255, 255, 255),        # Crisp Pure White #FFFFFF
        "card_border": RGBColor(254, 215, 170),    # Soft Amber Border #FED7AA
        "card_border_gold": RGBColor(197, 160, 89),
        "text_dark": RGBColor(31, 41, 55),         # Charcoal #1F2937
        "text_body": RGBColor(51, 65, 85),         # Slate #334155
        "text_muted": RGBColor(107, 114, 128),     # Gray #6B7280
        "text_light": RGBColor(255, 255, 255),
        "tbl_header": RGBColor(74, 14, 23),
        "tbl_stripe": RGBColor(254, 243, 199),
        "badge_bg": RGBColor(255, 241, 242),
        "badge_border": RGBColor(254, 205, 211),
        "badge_text": RGBColor(159, 18, 57),
        "cover_bg": RGBColor(40, 8, 14),           # Deep Wine Cover #28080E
        "cover_card": RGBColor(60, 12, 21),
        "cover_border": RGBColor(85, 20, 32),
        "danger": RGBColor(190, 18, 60),
        "danger_light": RGBColor(255, 241, 242)
    },
    # 5. Persian Teal Rose (Clinical Psychology & Psychotherapy - Extracted from Saber Ghaderi EFT Deck)
    "persian_teal_rose": {
        "primary": RGBColor(37, 198, 227),         # Vibrant Cyan / Turquoise #25C6E3
        "secondary": RGBColor(232, 5, 84),         # Rose Crimson #E80554
        "accent": RGBColor(169, 226, 111),         # Spring Lime #A9E26F
        "accent_light": RGBColor(236, 248, 223),   # Pale Mint Tint #ECF8DF
        "accent_dark": RGBColor(118, 196, 39),     # Meadow Green #76C427
        "emerald": RGBColor(16, 185, 129),
        "emerald_light": RGBColor(209, 250, 229),
        "bg_slide": RGBColor(255, 255, 255),       # Pure Crisp White #FFFFFF
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(226, 232, 240),
        "card_border_gold": RGBColor(37, 198, 227),
        "text_dark": RGBColor(15, 23, 42),         # Deep Navy Slate #0F172A
        "text_body": RGBColor(30, 41, 59),
        "text_muted": RGBColor(100, 116, 139),
        "text_light": RGBColor(255, 255, 255),
        "tbl_header": RGBColor(37, 198, 227),
        "tbl_stripe": RGBColor(240, 253, 244),
        "badge_bg": RGBColor(224, 247, 250),
        "badge_border": RGBColor(128, 222, 234),
        "badge_text": RGBColor(0, 131, 143),
        "cover_bg": RGBColor(14, 59, 67),          # Deep Teal Cover #0E3B43
        "cover_card": RGBColor(22, 84, 96),
        "cover_border": RGBColor(37, 198, 227),
        "danger": RGBColor(232, 5, 84),
        "danger_light": RGBColor(255, 228, 230)
    },
    # 6. Tehran Classic Azure (Tehran University Defense Classic - Extracted from Azadeh / Elshan / Payannameh)
    "tehran_classic_azure": {
        "primary": RGBColor(91, 155, 213),         # Tehran Soft Azure #5B9BD5
        "secondary": RGBColor(237, 125, 49),       # Warm Terracotta #ED7D31
        "accent": RGBColor(217, 119, 6),           # Warm Amber Gold #D97706
        "accent_light": RGBColor(254, 243, 199),
        "accent_dark": RGBColor(180, 83, 9),
        "emerald": RGBColor(16, 185, 129),
        "emerald_light": RGBColor(209, 250, 229),
        "bg_slide": RGBColor(248, 250, 252),       # Clean Slate Canvas #F8FAFC
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(226, 232, 240),
        "card_border_gold": RGBColor(237, 125, 49),
        "text_dark": RGBColor(15, 23, 42),
        "text_body": RGBColor(51, 65, 85),
        "text_muted": RGBColor(100, 116, 139),
        "text_light": RGBColor(255, 255, 255),
        "tbl_header": RGBColor(91, 155, 213),
        "tbl_stripe": RGBColor(241, 245, 249),
        "badge_bg": RGBColor(239, 246, 255),
        "badge_border": RGBColor(191, 219, 254),
        "badge_text": RGBColor(29, 78, 216),
        "cover_bg": RGBColor(30, 58, 138),         # Deep Navy Cover #1E3A8A
        "cover_card": RGBColor(30, 64, 175),
        "cover_border": RGBColor(96, 165, 250),
        "danger": RGBColor(220, 38, 38),
        "danger_light": RGBColor(254, 226, 226)
    }
}

def hex_to_rgb(hex_str: str) -> RGBColor:
    """Converts #RRGGBB or RRGGBB to pptx RGBColor tuple."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) != 6:
        return RGBColor(128, 128, 128)
    try:
        return RGBColor(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))
    except ValueError:
        return RGBColor(128, 128, 128)

def rgb_to_hex(color: RGBColor) -> str:
    """Converts pptx RGBColor tuple to standard CSS hex string #RRGGBB."""
    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

def load_theme_from_json(json_path: Path) -> Dict[str, RGBColor]:
    """Loads an extracted theme JSON and returns a validated PALETTES-compatible dictionary."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    raw_palette = data.get("palette", {})
    loaded = {}
    default_pal = PALETTES["academic_navy"]
    for key in default_pal:
        if key in raw_palette:
            val = raw_palette[key]
            loaded[key] = hex_to_rgb(val) if isinstance(val, str) else val
        else:
            loaded[key] = default_pal[key]
    return loaded

PALETTES_HEX: Dict[str, Dict[str, str]] = {
    theme_name: {key: rgb_to_hex(val) for key, val in pal.items()}
    for theme_name, pal in PALETTES.items()
}

# ---------------------------------------------------------------------------
# Supported Layout Families (28 Distinct Families defined in v3 Section 1.4)
# ---------------------------------------------------------------------------
SUPPORTED_LAYOUTS = [
    # 1. Cover / Title
    "cover",
    # 2. Section Divider
    "section_divider",
    # 3. Big-idea Statement
    "big_idea",
    # 4. Problem Funnel
    "problem_funnel",
    # 5. Inverted Pyramid
    "inverted_pyramid",
    # 6. Cause -> Mechanism -> Outcome
    "cause_mechanism_outcome",
    "causal_chain",
    # 7. Research-gap Comparison
    "gap_matrix",
    "research_gap",
    # 8. Before / After Conceptual Comparison
    "before_after",
    "comparison",
    # 9. Conceptual / SEM Path Model
    "conceptual_model",
    "path_diagram",
    "split_diagram",
    # 10. Research-process Flow
    "research_design",
    "process_flow",
    # 11. Sample / Participant Flow
    "sample_flow",
    # 12. Instrument Comparison
    "instrument_matrix",
    # 13. Timeline
    "intervention_timeline",
    "timeline",
    # 14. Numeric Result Spotlight
    "result_spotlight",
    # 15. KPI Panel
    "kpi_panel",
    "kpi_dashboard",
    # 16. Bar Chart
    "bar_chart",
    # 17. Dot Plot
    "dot_plot",
    # 18. Slope / Comparison Chart
    "slope_chart",
    "prepost_chart",
    # 19. Distribution / Box / Violin
    "distribution_chart",
    # 20. Correlation / Relationship
    "correlation_matrix",
    "relationship_map",
    # 21. Statistical Result Table
    "stat_table",
    "table",
    # 22. Hypothesis Matrix
    "hypothesis_matrix",
    # 23. Mediation Diagram
    "mediation_diagram",
    # 24. Discussion Mechanism Diagram
    "discussion_mechanism",
    # 25. Implication Map
    "implications",
    # 26. Limitation / Boundary Map
    "limitations",
    # 27. Recommendation Roadmap
    "recommendations",
    # 28. Closing / Q&A
    "closing",
    # Administrative & Legacy Aliases
    "committee",
    "two_column",
    "cards"
]

# Generic card layouts subject to Rule 1.3 (<= 25% of content slides)
GENERIC_CARD_LAYOUTS = {"cards", "cards_grid", "card_grid", "three_card", "four_card"}

# Layout Family Classifications (Rule 1.4: Never use same family twice in a row, <= 30% dominance)
# Maps layout types to the 28 canonical layout families defined in v3 Section 1.4
LAYOUT_FAMILY_MAPPING = {
    # Administrative & Structural (excluded from content repetition checks)
    "cover": "cover",                     # Family 1: Cover / title
    "committee": "administrative",
    "closing": "closing",                 # Family 28: Closing / Q&A
    "section_divider": "transition",      # Family 2: Section divider

    # Content Layout Families (Families 3–27)
    "big_idea": "statement",               # Family 3: Big-idea statement
    "problem_funnel": "funnel",           # Family 4: Problem funnel
    "inverted_pyramid": "funnel",         # Family 5: Inverted pyramid
    "cause_mechanism_outcome": "causal",  # Family 6: Cause -> mechanism -> outcome
    "causal_chain": "causal",
    "gap_matrix": "gap_matrix",           # Family 7: Research-gap comparison
    "research_gap": "gap_matrix",
    "before_after": "comparison",         # Family 8: Before / after comparison
    "comparison": "comparison",
    "conceptual_model": "path_model",     # Family 9: Conceptual / SEM path model
    "path_diagram": "path_model",
    "split_diagram": "path_model",
    "research_design": "process_flow",    # Family 10: Research-process flow
    "process_flow": "process_flow",
    "sample_flow": "sample_flow",         # Family 11: Sample / participant flow
    "instrument_matrix": "instrument_matrix", # Family 12: Instrument comparison
    "intervention_timeline": "timeline",  # Family 13: Timeline
    "timeline": "timeline",
    "result_spotlight": "spotlight",      # Family 14: Numeric result spotlight
    "kpi_panel": "kpi_panel",             # Family 15: KPI panel
    "kpi_dashboard": "kpi_panel",
    "bar_chart": "chart",                 # Family 16: Bar chart
    "dot_plot": "chart",                  # Family 17: Dot plot
    "slope_chart": "chart",               # Family 18: Slope / comparison chart
    "prepost_chart": "chart",
    "distribution_chart": "chart",        # Family 19: Distribution / box / violin
    "correlation_matrix": "relationship", # Family 20: Correlation / relationship
    "relationship_map": "relationship",
    "stat_table": "table",                # Family 21: Statistical result table
    "table": "table",
    "hypothesis_matrix": "hypothesis_matrix", # Family 22: Hypothesis matrix
    "mediation_diagram": "mediation_diagram", # Family 23: Mediation diagram
    "discussion_mechanism": "discussion_mechanism", # Family 24: Discussion mechanism diagram
    "implications": "implication_map",    # Family 25: Implication map
    "limitations": "limitation_map",      # Family 26: Limitation / boundary map
    "recommendations": "recommendation_roadmap", # Family 27: Recommendation roadmap
    "two_column": "explanation",
    "cards": "cards"
}

# Rule 1.3: Hard limit for generic card layouts (<= 25% of content slides)
MAX_CARD_LAYOUT_RATIO = 0.25

# Rule 1.4: Hard limit for any single content layout family dominance (<= 30% of content slides)
MAX_LAYOUT_FAMILY_RATIO = 0.30

# Rule 1.4: Never use the same layout family twice in a row on content slides
ALLOW_CONSECUTIVE_IDENTICAL_FAMILY = False

# Rule 1.5: Target typographic scales in points (16:9 Widescreen)
TYPOGRAPHY_TARGETS = {
    "title": (28, 36),
    "section_label": (14, 18),
    "body": (20, 26),
    "chart_labels": (16, 20),
    "spotlight_number": (34, 52),
    "table_text": (17, 20),
    "footnote_source": (13, 15)
}

# Rule 17: Quality Score rubric weights (100-point total)
QUALITY_SCORE_WEIGHTS = {
    "research_fidelity": 25,
    "narrative_quality": 20,
    "visual_communication": 20,
    "readability_typography": 15,
    "visual_consistency": 10,
    "technical_integrity": 10
}


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------
@dataclass
class ProjectMeta:
    title: str = ""
    subtitle: str = ""
    degree: str = ""
    university: str = ""
    faculty: str = ""
    department: str = ""
    author: str = ""
    supervisor: str = ""
    advisor: str = ""
    internal_examiner: str = ""
    external_examiner: str = ""
    defense_date: str = ""
    theme: str = "academic_navy"

@dataclass
class ResearchTruthModel:
    meta: ProjectMeta = field(default_factory=ProjectMeta)
    research_questions: List[str] = field(default_factory=list)
    hypotheses: List[Dict[str, Any]] = field(default_factory=list)
    variables: List[Dict[str, Any]] = field(default_factory=list)
    design: Dict[str, Any] = field(default_factory=dict)
    sample: Dict[str, Any] = field(default_factory=dict)
    instruments: List[Dict[str, Any]] = field(default_factory=list)
    intervention: List[Dict[str, Any]] = field(default_factory=list)
    descriptives: List[Dict[str, Any]] = field(default_factory=list)
    assumptions: List[Dict[str, Any]] = field(default_factory=list)
    inferential_results: List[Dict[str, Any]] = field(default_factory=list)
    effect_sizes: List[Dict[str, Any]] = field(default_factory=list)
    discussion_claims: List[Dict[str, Any]] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)

def validate_presentation_payload(payload: Dict[str, Any]) -> List[str]:
    """Validates intermediate presentation payload against core schema rules."""
    errors = []
    if not isinstance(payload, dict):
        return ["Payload must be a valid JSON dictionary."]
    
    slides = payload.get("slides")
    if not isinstance(slides, list) or len(slides) == 0:
        errors.append("Payload must contain a non-empty 'slides' list.")
        return errors
    
    meta = payload.get("meta", {})
    if not isinstance(meta, dict):
        errors.append("'meta' must be a dictionary.")

    for idx, slide in enumerate(slides):
        slide_num = slide.get("slide_number", idx + 1)
        layout = slide.get("layout")
        if not layout:
            errors.append(f"Slide {slide_num} is missing 'layout'.")
        elif layout not in SUPPORTED_LAYOUTS:
            errors.append(f"Slide {slide_num} specifies unknown layout '{layout}'.")
        
        # Check title
        if layout not in ["cover", "section_divider", "closing"] and not slide.get("title"):
            errors.append(f"Slide {slide_num} ({layout}) is missing a 'title'.")

    return errors
