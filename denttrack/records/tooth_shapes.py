"""
Generates the SVG path data for one anatomically-styled tooth, split into
5 clickable/droppable surface zones, laid out the way a real 2D frontal
dental chart shows them: mesial and distal as the left/right thirds of the
crown face, occlusal/incisal as the center third, buccal as a thin outer
rim wrapping the crown, and lingual as a small inner core. This matches
clinical convention (mesial = toward the front midline, distal = toward
the back of the arch) far more closely than stacking all 5 zones in
horizontal bands top-to-bottom.

Coordinate system: each tooth is drawn in a local 40 (wide) x 56 (tall)
box. For lower-arch teeth the whole shape is flipped vertically — "upper"
teeth have their crown at the bottom of the box (hanging down from the
top jaw into the mouth) and "lower" teeth have their crown at the top of
the box (sticking up from the bottom jaw). This mirrors the real chart
layout where the upper arch hangs down and the lower arch sticks up,
meeting in the middle.
"""

W, H = 40, 56


def _flip_y(path_d, height=H):
    """Flip a path's y-coordinates for lower-arch teeth (mirrors vertically)."""
    # Not used directly — shapes are authored separately per arch below for
    # clarity instead of doing string-math on path commands.
    return path_d


def _shape_incisor(arch):
    """Central/lateral incisor — flat chisel edge, slightly tapered root side."""
    if arch == "upper":
        crown_top, crown_bot = 6, 40
        outline = f"M10,{crown_top} Q8,{(crown_top+crown_bot)/2} 11,{crown_bot} Q20,{crown_bot+4} 29,{crown_bot} Q32,{(crown_top+crown_bot)/2} 30,{crown_top} Q20,{crown_top-3} 10,{crown_top} Z"
        occlusal_y = crown_bot - 9
    else:
        crown_top, crown_bot = 16, 50
        outline = f"M10,{crown_top+4} Q8,{(crown_top+crown_bot)/2} 11,{crown_bot} Q20,{crown_bot+3} 29,{crown_bot} Q32,{(crown_top+crown_bot)/2} 30,{crown_top+4} Q20,{crown_top} 10,{crown_top+4} Z"
        occlusal_y = crown_top + 13
    return outline, crown_top, crown_bot, occlusal_y


def _shape_canine(arch):
    """Canine — single pointed cusp."""
    if arch == "upper":
        crown_top, crown_bot = 6, 40
        outline = (f"M9,{crown_top+3} Q7,{(crown_top+crown_bot)/2} 11,{crown_bot-3} "
                    f"Q20,{crown_bot+7} 29,{crown_bot-3} Q33,{(crown_top+crown_bot)/2} 31,{crown_top+3} "
                    f"Q26,{crown_top-1} 22,{crown_top+1} L20,{crown_top-5} L18,{crown_top+1} "
                    f"Q14,{crown_top-1} 9,{crown_top+3} Z")
        occlusal_y = crown_bot - 6
    else:
        crown_top, crown_bot = 16, 50
        outline = (f"M9,{crown_top+6} Q7,{(crown_top+crown_bot)/2} 11,{crown_bot-2} "
                    f"Q20,{crown_bot+3} 29,{crown_bot-2} Q33,{(crown_top+crown_bot)/2} 31,{crown_top+6} "
                    f"Q26,{crown_top+2} 22,{crown_top} L20,{crown_top+6} L18,{crown_top} "
                    f"Q14,{crown_top+2} 9,{crown_top+6} Z")
        occlusal_y = crown_top + 9
    return outline, crown_top, crown_bot, occlusal_y


def _shape_premolar(arch):
    """Premolar — two rounded cusps, oval-ish crown."""
    if arch == "upper":
        crown_top, crown_bot = 8, 40
        outline = (f"M8,{crown_top+4} Q6,{(crown_top+crown_bot)/2} 9,{crown_bot-2} "
                    f"Q20,{crown_bot+5} 31,{crown_bot-2} Q34,{(crown_top+crown_bot)/2} 32,{crown_top+4} "
                    f"Q27,{crown_top} 24,{crown_top+3} L20,{crown_top-2} L16,{crown_top+3} "
                    f"Q13,{crown_top} 8,{crown_top+4} Z")
        occlusal_y = crown_bot - 9
    else:
        crown_top, crown_bot = 16, 48
        outline = (f"M8,{crown_top+5} Q6,{(crown_top+crown_bot)/2} 9,{crown_bot-3} "
                    f"Q20,{crown_bot+2} 31,{crown_bot-3} Q34,{(crown_top+crown_bot)/2} 32,{crown_top+5} "
                    f"Q27,{crown_top+1} 24,{crown_top+4} L20,{crown_top} L16,{crown_top+4} "
                    f"Q13,{crown_top+1} 8,{crown_top+5} Z")
        occlusal_y = crown_top + 11
    return outline, crown_top, crown_bot, occlusal_y


def _shape_molar(arch):
    """1st/2nd molar — broad 4-cusp crown, widest tooth on the arch."""
    if arch == "upper":
        crown_top, crown_bot = 8, 40
        outline = (f"M5,{crown_top+5} Q3,{(crown_top+crown_bot)/2} 6,{crown_bot-2} "
                    f"Q20,{crown_bot+6} 34,{crown_bot-2} Q37,{(crown_top+crown_bot)/2} 35,{crown_top+5} "
                    f"Q31,{crown_top+1} 28,{crown_top+3} L26,{crown_top-2} L23,{crown_top+2} "
                    f"L20,{crown_top-1} L17,{crown_top+2} L14,{crown_top-2} L12,{crown_top+3} "
                    f"Q9,{crown_top+1} 5,{crown_top+5} Z")
        occlusal_y = crown_bot - 10
    else:
        crown_top, crown_bot = 16, 48
        outline = (f"M5,{crown_top+6} Q3,{(crown_top+crown_bot)/2} 6,{crown_bot-3} "
                    f"Q20,{crown_bot+2} 34,{crown_bot-3} Q37,{(crown_top+crown_bot)/2} 35,{crown_top+6} "
                    f"Q31,{crown_top+2} 28,{crown_top} L26,{crown_top+5} L23,{crown_top+1} "
                    f"L20,{crown_top+4} L17,{crown_top+1} L14,{crown_top+5} L12,{crown_top} "
                    f"Q9,{crown_top+2} 5,{crown_top+6} Z")
        occlusal_y = crown_top + 12
    return outline, crown_top, crown_bot, occlusal_y


def _shape_molar3(arch):
    """3rd molar (wisdom) — similar to molar but squarer, slightly smaller."""
    if arch == "upper":
        crown_top, crown_bot = 9, 39
        outline = (f"M6,{crown_top+4} Q4,{(crown_top+crown_bot)/2} 7,{crown_bot-2} "
                    f"Q20,{crown_bot+4} 33,{crown_bot-2} Q36,{(crown_top+crown_bot)/2} 34,{crown_top+4} "
                    f"Q29,{crown_top} 26,{crown_top+2} L23,{crown_top-1} L20,{crown_top+1} "
                    f"L17,{crown_top-1} L14,{crown_top+2} Q11,{crown_top} 6,{crown_top+4} Z")
        occlusal_y = crown_bot - 9
    else:
        crown_top, crown_bot = 17, 47
        outline = (f"M6,{crown_top+5} Q4,{(crown_top+crown_bot)/2} 7,{crown_bot-3} "
                    f"Q20,{crown_bot+1} 33,{crown_bot-3} Q36,{(crown_top+crown_bot)/2} 34,{crown_top+5} "
                    f"Q29,{crown_top+1} 26,{crown_top+3} L23,{crown_top} L20,{crown_top+2} "
                    f"L17,{crown_top} L14,{crown_top+3} Q11,{crown_top+1} 6,{crown_top+5} Z")
        occlusal_y = crown_top + 10
    return outline, crown_top, crown_bot, occlusal_y


SHAPE_FUNCS = {
    "incisor": _shape_incisor,
    "canine": _shape_canine,
    "premolar": _shape_premolar,
    "molar": _shape_molar,
    "molar3": _shape_molar3,
}

# Root outline (drawn underneath/behind the crown, lighter colored, not
# clickable — purely cosmetic so the tooth reads as a tooth, not a blob).
def _root_path(shape, arch, crown_top, crown_bot):
    cx = W / 2
    if arch == "upper":
        root_top = crown_bot - 6
        root_tip = root_top + 16 if shape in ("incisor", "canine") else root_top + 13
        if shape in ("molar", "molar3"):
            return (f"M14,{root_top} Q12,{root_top+9} 14,{root_tip} L16,{root_top+6} Z "
                     f"M26,{root_top} Q28,{root_top+9} 26,{root_tip} L24,{root_top+6} Z")
        return f"M{cx-4},{root_top} Q{cx-6},{root_top+10} {cx},{root_tip} Q{cx+6},{root_top+10} {cx+4},{root_top} Z"
    else:
        root_top = crown_top + 6
        root_tip = root_top - 16 if shape in ("incisor", "canine") else root_top - 13
        if shape in ("molar", "molar3"):
            return (f"M14,{root_top} Q12,{root_top-9} 14,{root_tip} L16,{root_top-6} Z "
                     f"M26,{root_top} Q28,{root_top-9} 26,{root_tip} L24,{root_top-6} Z")
        return f"M{cx-4},{root_top} Q{cx-6},{root_top-10} {cx},{root_tip} Q{cx+6},{root_top-10} {cx+4},{root_top} Z"


def get_tooth_geometry(shape, arch):
    """
    Returns a dict with the crown outline path, the root path (decorative),
    and 5 surface zones laid out the way a real 2D frontal dental chart
    shows them:

      - Mesial / Distal: left and right vertical thirds of the crown
        (mesial = side nearer the front midline, distal = side nearer the
        back of the arch — this falls out naturally from the left-to-right
        tooth ordering already used by the chart view, so the geometry
        itself doesn't need to know which arch-side a tooth is on).
      - Occlusal / Incisal: the center third — the biting surface.
      - Buccal: a thin outer rim tracing the whole crown (the cheek/lip
        facing surface — on a flat frontal view this wraps the visible
        perimeter of the tooth).
      - Lingual: a small inner core sitting inside that rim (the
        tongue/palate-facing surface).

    Each zone is returned as its own SVG path (the caller clips every path
    to the crown outline, so on screen the rectangles/insets all come out
    tooth-shaped instead of square). Buccal is drawn first as the full
    crown-bounds box; mesial/occlusal/distal thirds paint over its left,
    center, and right; lingual paints last as a small centered patch so it
    reads as a visible "core" rather than another stripe.
    """
    fn = SHAPE_FUNCS[shape]
    outline, crown_top, crown_bot, occlusal_y = fn(arch)
    root = _root_path(shape, arch, crown_top, crown_bot)

    crown_h = crown_bot - crown_top
    third_w = W / 3
    left_x = third_w
    right_x = 2 * third_w
    rim = max(4.0, min(crown_h, W) * 0.24)  # inset thickness for the lingual core

    mesial_path = f"M0,{crown_top} L{left_x},{crown_top} L{left_x},{crown_bot} L0,{crown_bot} Z"
    distal_path = f"M{right_x},{crown_top} L{W},{crown_top} L{W},{crown_bot} L{right_x},{crown_bot} Z"
    occlusal_path = f"M{left_x},{crown_top} L{right_x},{crown_top} L{right_x},{crown_bot} L{left_x},{crown_bot} Z"
    buccal_path = f"M0,{crown_top} L{W},{crown_top} L{W},{crown_bot} L0,{crown_bot} Z"
    lingual_path = (f"M{rim},{crown_top+rim} L{W-rim},{crown_top+rim} "
                     f"L{W-rim},{crown_bot-rim} L{rim},{crown_bot-rim} Z")

    surface_paths = {
        "mesial": mesial_path,
        "distal": distal_path,
        "occlusal": occlusal_path,
        "buccal": buccal_path,
        "lingual": lingual_path,
    }
    # Paint order: buccal (full crown box) first so it forms the visible
    # rim once mesial/occlusal/distal and the lingual core paint on top.
    draw_order = ["buccal", "mesial", "occlusal", "distal", "lingual"]

    return {
        "outline": outline,
        "root": root,
        "crown_top": crown_top,
        "crown_bot": crown_bot,
        "surface_paths": surface_paths,
        "draw_order": draw_order,
        "box_w": W,
        "box_h": H,
        # Divider-line geometry (purely cosmetic — lets the template draw
        # faint lines marking the 3 vertical thirds and the lingual rim
        # even when every surface is "clear" and would otherwise render
        # as one undifferentiated pale rectangle).
        "third_x1": round(left_x, 1),
        "third_x2": round(right_x, 1),
        "rim": round(rim, 1),
        "lingual_w": round(W - 2 * rim, 1),
        "lingual_h": round(crown_h - 2 * rim, 1),
    }
