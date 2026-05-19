GREEN = "#22c55e"
GREEN_DARK = "#15803d"
GREEN_SOFT = "#dcfce7"
BG = "#f1f5f9"
CARD = "white"
BORDER = "#e2e8f0"
BORDER_DARK = "#cbd5e1"
TEXT = "#0f172a"
MUTED = "#64748b"
DARK_MUTED = "#475569"
DANGER = "#ef4444"
WARNING = "#f97316"
SURFACE_MUTED = "#f8fafc"
SURFACE_HOVER = "#f1f5f9"

INTERACTIVE_TRANSITION = "all 160ms ease"
FOCUS_RING = "0 0 0 3px rgba(34, 197, 94, 0.22)"

BRAND_LOGO_ASSET_PATH = "/brand/logoGIGAJPEG.jpeg"

BASE_PAGE_STYLE = {
    "min_height": "100vh",
    "bg": BG,
    "color": TEXT,
}

FOCUS_VISIBLE_STYLE = {
    "outline": "none",
    "box_shadow": FOCUS_RING,
}

DISABLED_STYLE = {
    "opacity": "0.55",
    "cursor": "not-allowed",
}

CARD_STYLE = {
    "bg": CARD,
    "border": f"1px solid {BORDER}",
    "border_radius": "16px",
    "padding": "1rem",
    "box_shadow": "0 6px 20px rgba(15, 23, 42, 0.06)",
}

INPUT_STYLE = {
    "width": "100%",
    "size": "3",
    "variant": "surface",
    "radius": "large",
    "bg": "white",
    "border_color": BORDER_DARK,
    "transition": INTERACTIVE_TRANSITION,
    "_hover": {"border_color": "#94a3b8"},
    "_focus_visible": {
        "outline": "none",
        "box_shadow": FOCUS_RING,
        "border_color": GREEN_DARK,
    },
    "_disabled": DISABLED_STYLE,
}

TEXTAREA_STYLE = {
    "width": "100%",
    "bg": "white",
    "border_color": BORDER_DARK,
    "border_radius": "12px",
    "transition": INTERACTIVE_TRANSITION,
    "resize": "vertical",
    "_hover": {"border_color": "#94a3b8"},
    "_focus_visible": {
        "outline": "none",
        "box_shadow": FOCUS_RING,
        "border_color": GREEN_DARK,
    },
    "_disabled": DISABLED_STYLE,
}

SELECT_TRIGGER_STYLE = {
    "width": "100%",
    "bg": "white",
    "border": f"1px solid {BORDER_DARK}",
    "border_radius": "12px",
    "transition": INTERACTIVE_TRANSITION,
    "_hover": {"border_color": "#94a3b8"},
    "_focus_visible": {
        "outline": "none",
        "box_shadow": FOCUS_RING,
        "border_color": GREEN_DARK,
    },
}

PRIMARY_BUTTON_STYLE = {
    "bg": GREEN,
    "color": "white",
    "border_radius": "12px",
    "padding_x": "1rem",
    "padding_y": "0.75rem",
    "font_weight": "600",
    "cursor": "pointer",
    "transition": INTERACTIVE_TRANSITION,
    "_hover": {"bg": GREEN_DARK},
    "_focus_visible": FOCUS_VISIBLE_STYLE,
    "_active": {"transform": "translateY(1px)"},
    "_disabled": DISABLED_STYLE,
}

SECONDARY_BUTTON_STYLE = {
    "border_radius": "12px",
    "font_weight": "600",
    "transition": INTERACTIVE_TRANSITION,
    "_focus_visible": FOCUS_VISIBLE_STYLE,
    "_disabled": DISABLED_STYLE,
}

PAGE_TITLE_STYLE = {
    "size": "8",
    "line_height": "1.1",
    "letter_spacing": "-0.02em",
}

PAGE_SUBTITLE_STYLE = {
    "color": MUTED,
    "size": "3",
}

TABLE_SCROLL_STYLE = {
    "width": "100%",
    "overflow_x": "auto",
    "border": f"1px solid {BORDER}",
    "border_radius": "12px",
    "bg": "white",
}

STEP_PENDING = "#94a3b8"
STEP_VISITED_BG = "#e2e8f0"
STEP_VISITED_TEXT = "#334155"
STEPPER_TRACK_BG = "#f8fafc"

STEP_ACTION_BAR_STYLE = {
    "width": "100%",
    "padding": "0.75rem",
    "border": f"1px solid {BORDER}",
    "border_radius": "12px",
    "bg": "rgba(255,255,255,0.96)",
    "backdrop_filter": "blur(6px)",
    "position": {"base": "static", "lg": "sticky"},
    "bottom": {"base": "auto", "lg": "0.75rem"},
    "z_index": "4",
}

FORM_BLOCK_STYLE = {
    "width": "100%",
    "border": f"1px solid {BORDER}",
    "border_radius": "14px",
    "bg": "white",
    "padding": "1rem",
    "display": "grid",
    "gap": "0.85rem",
}

FORM_BLOCK_HEADER_STYLE = {
    "width": "100%",
    "display": "flex",
    "align_items": "center",
    "justify_content": "space-between",
    "gap": "0.5rem",
}

FORM_BLOCK_TITLE_STYLE = {
    "font_weight": "700",
    "color": TEXT,
}

FORM_BLOCK_HELPER_STYLE = {
    "size": "2",
    "color": MUTED,
}

FIELD_LABEL_STYLE = {
    "font_weight": "600",
    "size": "2",
    "color": TEXT,
}

CHECKLIST_GRID_STYLE = {
    "width": "100%",
    "display": "grid",
    "gap": "0.65rem",
}

CHECKLIST_ITEM_STYLE = {
    "width": "100%",
    "border": f"1px solid {BORDER}",
    "border_radius": "12px",
    "bg": SURFACE_MUTED,
    "padding": "0.75rem",
}

INFO_SURFACE_STYLE = {
    "width": "100%",
    "border": f"1px solid {BORDER}",
    "border_radius": "12px",
    "bg": SURFACE_MUTED,
    "padding": "0.75rem",
}

FORM_ITEM_CARD_STYLE = {
    "width": "100%",
    "border": f"1px solid {BORDER}",
    "border_radius": "14px",
    "padding": "1rem",
    "bg": "white",
}

EMPTY_STATE_STYLE = {
    "width": "100%",
    "border": "1px dashed #cbd5e1",
    "border_radius": "12px",
    "padding": "1rem",
    "bg": SURFACE_MUTED,
}

CALLOUT_STYLE = {
    "border_radius": "12px",
}

BADGE_PILL_STYLE = {
    "border_radius": "999px",
    "font_weight": "600",
}

BRAND_MARK_STYLE = {
    "border_radius": "12px",
    "overflow": "hidden",
    "bg": "white",
    "border": f"1px solid {BORDER}",
    "display": "flex",
    "align_items": "center",
    "justify_content": "center",
    "flex_shrink": "0",
}

BRAND_TITLE_STYLE = {
    "font_weight": "800",
    "size": "4",
    "color": GREEN_DARK,
    "line_height": "1.05",
}

BRAND_SUBTITLE_STYLE = {
    "size": "1",
    "color": MUTED,
    "text_transform": "uppercase",
    "letter_spacing": "0.08em",
}

SIDEBAR_LINK_WRAPPER_STYLE = {
    "width": "100%",
    "text_decoration": "none",
    "color": "inherit",
    "border_radius": "12px",
    "transition": INTERACTIVE_TRANSITION,
    "_focus_visible": FOCUS_VISIBLE_STYLE,
}

SIDEBAR_LINK_INNER_STYLE = {
    "width": "100%",
    "padding": "0.8rem 0.9rem",
    "border_radius": "12px",
    "transition": INTERACTIVE_TRANSITION,
    "align": "center",
    "spacing": "2",
}

MOBILE_NAV_BAR_STYLE = {
    "width": "100%",
    "bg": "white",
    "border": f"1px solid {BORDER}",
    "border_radius": "14px",
    "padding": "0.6rem 0.75rem",
    "box_shadow": "0 6px 18px rgba(15, 23, 42, 0.06)",
}

MOBILE_DRAWER_PANEL_STYLE = {
    "width": "100%",
    "max_width": "320px",
    "height": "100%",
    "bg": BG,
    "padding": "0.75rem",
    "display": "grid",
    "align_content": "start",
    "gap": "0.6rem",
}
