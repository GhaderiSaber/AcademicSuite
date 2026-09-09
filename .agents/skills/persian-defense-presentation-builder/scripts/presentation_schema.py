#!/usr/bin/env python3
"""
Presentation Schema & Truth Model (persian-defense-presentation-builder v3.0.0)
=============================================================================
Defines the intermediate slide specification, Research Truth Model,
color palettes, and layout family classifications for 16:9 defense presentations.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pptx.dml.color import RGBColor

# ---------------------------------------------------------------------------
# Visual Themes & Design Tokens (16:9 Widescreen: 13.333" x 7.5")
# ---------------------------------------------------------------------------
PALETTES: Dict[str, Dict[str, RGBColor]] = {
    "academic_navy": {
        "primary": RGBColor(248, 250, 252),        # Crisp White #F8FAFC (Title & Main)
        "secondary": RGBColor(96, 165, 250),      # Light Academic Sapphire #60A5FA
        "accent": RGBColor(245, 158, 11),          # Warm Amber Gold #F59E0B
        "accent_light": RGBColor(254, 243, 199),  # Soft Gold Tint #FEF3C7
        "accent_dark": RGBColor(217, 119, 6),      # Deep Warm Amber #D97706
        "emerald": RGBColor(16, 185, 129),         # Forest Emerald #10B981
        "emerald_light": RGBColor(209, 250, 229), # Soft Mint Tint #ECFDF5
        "bg_slide": RGBColor(7, 13, 31),           # Modern Dark Midnight Navy #070D1F
        "card_bg": RGBColor(19, 32, 66),           # Deep Slate Navy Card #132042
        "card_border": RGBColor(37, 54, 98),       # Subtle Indigo/Slate Border #253662
        "card_border_gold": RGBColor(245, 158, 11),# Gold Border #F59E0B
        "text_dark": RGBColor(248, 250, 252),      # Text on Cards (Crisp White)
        "text_body": RGBColor(203, 213, 225),      # Slate 300 #CBD5E1
        "text_muted": RGBColor(148, 163, 184),    # Slate 400 #94A3B8
        "text_light": RGBColor(255, 255, 255),    # Crisp White #FFFFFF
        "tbl_header": RGBColor(29, 46, 94),       # Header Blue #1D2E5E
        "tbl_stripe": RGBColor(13, 23, 51),       # Stripe Navy #0D1733
        "badge_bg": RGBColor(24, 39, 79),         # Badge Fill
        "badge_border": RGBColor(59, 130, 246),   # Badge Border #3B82F6
        "badge_text": RGBColor(96, 165, 250),     # Badge Text #60A5FA
        "cover_bg": RGBColor(7, 13, 31),          # Midnight Obsidian #070D1F
        "cover_card": RGBColor(19, 32, 66),       # Translucent Slate Card #132042
        "cover_border": RGBColor(37, 54, 98),     # Slate Hairline #253662
        "danger": RGBColor(239, 68, 68),          # Coral Red #EF4444
        "danger_light": RGBColor(127, 29, 29)
    },
    "emerald_slate": {
        "primary": RGBColor(19, 78, 74),
        "secondary": RGBColor(15, 118, 110),
        "accent": RGBColor(5, 150, 105),
        "accent_light": RGBColor(209, 250, 229),
        "accent_dark": RGBColor(4, 120, 87),
        "emerald": RGBColor(5, 150, 105),
        "emerald_light": RGBColor(209, 250, 229),
        "bg_slide": RGBColor(240, 253, 244),
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(209, 250, 229),
        "card_border_gold": RGBColor(5, 150, 105),
        "text_dark": RGBColor(19, 42, 31),
        "text_body": RGBColor(51, 65, 85),
        "text_muted": RGBColor(75, 85, 99),
        "text_light": RGBColor(255, 255, 255),
        "tbl_header": RGBColor(19, 78, 74),
        "tbl_stripe": RGBColor(236, 253, 245),
        "badge_bg": RGBColor(236, 253, 245),
        "badge_border": RGBColor(167, 243, 208),
        "badge_text": RGBColor(4, 120, 87),
        "cover_bg": RGBColor(12, 35, 33),
        "cover_card": RGBColor(19, 52, 49),
        "cover_border": RGBColor(30, 75, 71),
        "danger": RGBColor(190, 18, 60),
        "danger_light": RGBColor(255, 241, 242)
    },
    "royal_burgundy": {
        "primary": RGBColor(74, 14, 23),
        "secondary": RGBColor(136, 19, 55),
        "accent": RGBColor(197, 160, 89),
        "accent_light": RGBColor(254, 243, 199),
        "accent_dark": RGBColor(180, 83, 9),
        "emerald": RGBColor(5, 150, 105),
        "emerald_light": RGBColor(209, 250, 229),
        "bg_slide": RGBColor(255, 251, 235),
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(254, 215, 170),
        "card_border_gold": RGBColor(197, 160, 89),
        "text_dark": RGBColor(31, 41, 55),
        "text_body": RGBColor(51, 65, 85),
        "text_muted": RGBColor(107, 114, 128),
        "text_light": RGBColor(255, 255, 255),
        "tbl_header": RGBColor(74, 14, 23),
        "tbl_stripe": RGBColor(254, 243, 199),
        "badge_bg": RGBColor(255, 241, 242),
        "badge_border": RGBColor(254, 205, 211),
        "badge_text": RGBColor(159, 18, 57),
        "cover_bg": RGBColor(40, 8, 14),
        "cover_card": RGBColor(60, 12, 21),
        "cover_border": RGBColor(85, 20, 32),
        "danger": RGBColor(190, 18, 60),
        "danger_light": RGBColor(255, 241, 242)
    }
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
