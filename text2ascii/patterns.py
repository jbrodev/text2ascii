"""
ASCII/Unicode pattern and scene generator for text2ascii.

Generates procedural ASCII art scenes: starry night, garden, storm, forest, ocean.
Each call produces a unique random variation.
"""

import os
import random

THEMES = ["starry-night", "garden", "storm", "forest", "ocean"]


# ---------------------------------------------------------------------------
# Grid helpers
# ---------------------------------------------------------------------------

def _grid(w: int, h: int, fill: str = " ") -> list[list[str]]:
    return [[fill] * w for _ in range(h)]


def _set(g: list[list[str]], r: int, c: int, ch: str) -> None:
    if 0 <= r < len(g) and 0 <= c < len(g[0]):
        g[r][c] = ch


def _write(g: list[list[str]], r: int, c: int, text: str) -> None:
    for i, ch in enumerate(text):
        _set(g, r, c + i, ch)


def _lines(g: list[list[str]]) -> list[str]:
    return ["".join(row) for row in g]


# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------

def generate_starry_night(w: int, h: int) -> list[str]:
    g = _grid(w, h)
    stars = ["*", "·", "+", ".", "°", "✦", "✧", "'"]

    # Stars in upper 3/4
    for r in range(h - 3):
        for c in range(w):
            if random.random() < 0.10:
                _set(g, r, c, random.choice(stars))

    # Moon (upper-right area)
    mr = random.randint(1, 3)
    mc = random.randint(w - 14, w - 6)
    moon_type = random.choice(["right", "left", "full"])
    if moon_type == "full":
        _write(g, mr,     mc, " (   ) ")
        _write(g, mr + 1, mc, "(  O  )")
        _write(g, mr + 2, mc, " (   ) ")
    elif moon_type == "right":
        _write(g, mr,     mc, "( )")
        _write(g, mr + 1, mc, "(  )")
        _write(g, mr + 2, mc, "( )")
    else:
        _write(g, mr,     mc, "( )")
        _write(g, mr + 1, mc, "(  )")
        _write(g, mr + 2, mc, "( )")

    # Shooting star (50% chance)
    if random.random() < 0.55:
        sr = random.randint(0, 3)
        sc = random.randint(3, w // 2)
        length = random.randint(7, 14)
        for i in range(length):
            _set(g, sr + i // 4, sc + i, "-")
        _set(g, sr, sc - 1, "*")

    # Horizon / silhouette hills
    hill_row = h - 3
    c = 0
    while c < w:
        seg = random.randint(4, 10)
        if random.random() < 0.4 and c + seg + 4 < w:
            rise = random.randint(2, 5)
            _write(g, hill_row, c, "_" * (seg // 2))
            _set(g, hill_row, c + seg // 2, "/")
            _write(g, hill_row - 1, c + seg // 2 + 1, "‾" * rise)
            _set(g, hill_row, c + seg // 2 + rise + 1, "\\")
            _write(g, hill_row, c + seg // 2 + rise + 2, "_" * (seg // 2))
        else:
            _write(g, hill_row, c, "_" * seg)
        c += seg

    # Fill below hills
    for r in range(hill_row + 1, h):
        for c2 in range(w):
            _set(g, r, c2, "_")

    return _lines(g)


def generate_garden(w: int, h: int) -> list[str]:
    g = _grid(w, h)

    # Faint sky texture
    for r in range(h // 2):
        for c in range(w):
            if random.random() < 0.02:
                _set(g, r, c, random.choice([".", "'", "`"]))

    # Sun (upper-left)
    sr = random.randint(1, 3)
    sc = random.randint(2, 10)
    _write(g, sr - 1, sc - 1, " \\|/ ")
    _write(g, sr,     sc - 2, "--(O)--")
    _write(g, sr + 1, sc - 1, " /|\\ ")

    # Clouds (1-3)
    for _ in range(random.randint(1, 3)):
        cr = random.randint(1, h // 4)
        cc = random.randint(12, w - 14)
        cl = random.randint(6, 12)
        _write(g, cr - 1, cc + 2, "(" + "~" * (cl - 2) + ")")
        _write(g, cr,     cc,     "(" + "~" * cl + ")")

    # Flowers
    ground_row = h - 3
    blooms = ["*", "@", "o", "O", "w", "W", "✿", "❀"]
    num_flowers = random.randint(7, 14)
    cols = random.sample(range(2, w - 2), min(num_flowers, w - 4))
    for fc in cols:
        stem_h = random.randint(2, 5)
        bloom = random.choice(blooms)
        for s in range(stem_h):
            row = ground_row - 1 - s
            _set(g, row, fc, "|")
            if s == stem_h // 2:
                leaf_side = fc - 1 if random.random() < 0.5 else fc + 1
                _set(g, row, leaf_side, random.choice(["/", "\\"]))
        _set(g, ground_row - stem_h - 1, fc, bloom)

    # Butterflies / bees
    for _ in range(random.randint(1, 3)):
        _write(g, random.randint(h // 4, h - 6), random.randint(2, w - 5),
               random.choice([">v<", "^.^", "~.~", "✿"]))

    # Ground
    for c in range(w):
        _set(g, ground_row, c, random.choice(['"', "'", "-", "_", "_", "_"]))
    for c in range(w):
        _set(g, ground_row + 1, c, "_")
    if ground_row + 2 < h:
        for c in range(w):
            _set(g, ground_row + 2, c, "_")

    return _lines(g)


def generate_storm(w: int, h: int) -> list[str]:
    g = _grid(w, h)
    cloud_cols: set[int] = set()

    # Clouds
    for _ in range(random.randint(2, 4)):
        cr = random.randint(0, h // 5)
        cc = random.randint(0, w - 18)
        cl = random.randint(10, 16)
        _write(g, cr,     cc + 2,  "(" + "~" * cl + ")")
        _write(g, cr + 1, cc,      "(" + "~" * (cl + 4) + ")")
        _write(g, cr + 2, cc + 1,  "(" + "~" * (cl + 2) + ")")
        for col in range(cc, cc + cl + 6):
            cloud_cols.add(col)

    # Rain
    for c in range(w):
        density = 0.40 if c in cloud_cols else 0.15
        for r in range(h // 4, h - 1):
            if random.random() < density:
                _set(g, r, c, random.choice(["|", "'", "`"]))

    # Lightning (1-2 bolts)
    for _ in range(random.randint(1, 2)):
        lc = random.randint(w // 5, 4 * w // 5)
        r, c = h // 5, lc
        _set(g, r, c, "*")
        direction = 1
        while r < h - 2:
            r += 1
            c = max(0, min(w - 1, c + direction))
            _set(g, r, c, "\\" if direction == 1 else "/")
            if random.random() < 0.45:
                direction *= -1

    # Puddles
    for c in range(w):
        _set(g, h - 1, c, "~" if random.random() < 0.5 else "_")

    return _lines(g)


def generate_forest(w: int, h: int) -> list[str]:
    g = _grid(w, h)
    ground_row = h - 2

    # Sky — night or day
    if random.random() < 0.5:
        for r in range(h // 2):
            for c in range(w):
                if random.random() < 0.06:
                    _set(g, r, c, random.choice(["*", ".", "'", "°"]))
        mr, mc = random.randint(1, 3), random.randint(w - 12, w - 4)
        _write(g, mr, mc, "( )")
    else:
        _write(g, 1, 3, " \\|/ ")
        _write(g, 2, 2, "--(O)--")
        _write(g, 3, 3, " /|\\ ")
        for _ in range(random.randint(1, 2)):
            _write(g, random.randint(1, h // 4), random.randint(14, w - 12), "(~~~)")

    # Trees
    x = random.randint(1, 4)
    while x < w - 6:
        tw = random.choice([5, 7, 9])
        th = random.randint(5, min(10, ground_row - 1))
        canopy_rows = th - 2
        for level in range(canopy_rows):
            w_at = 1 + level * 2
            row = ground_row - (canopy_rows - level) - 1
            sc = x + (tw - w_at) // 2
            interior = "*" * max(0, w_at - 2)
            _write(g, row, sc, "/" + interior + "\\")
        trunk_c = x + tw // 2
        _set(g, ground_row - 1, trunk_c, "|")
        _set(g, ground_row,     trunk_c, "|")
        x += tw + random.randint(1, 5)

    # Ground
    for c in range(w):
        _set(g, ground_row, c, random.choice(['"', "'", "_", "_", "_"]))
    for c in range(w):
        if ground_row + 1 < h:
            _set(g, ground_row + 1, c, "_")

    return _lines(g)


def generate_ocean(w: int, h: int) -> list[str]:
    g = _grid(w, h)
    sky_rows = h // 4

    # Sky
    for r in range(sky_rows):
        for c in range(w):
            if random.random() < 0.04:
                _set(g, r, c, random.choice([".", "*", "'"]))

    # Sun or moon
    if random.random() < 0.6:
        _write(g, 1, w - 9,  " \\|/ ")
        _write(g, 2, w - 10, "--(O)--")
        _write(g, 3, w - 9,  " /|\\ ")
    else:
        _write(g, 1, w - 6, "( )")

    # Horizon
    for c in range(w):
        _set(g, sky_rows, c, "-")

    # Boat
    bc = random.randint(5, w - 14)
    _write(g, sky_rows - 3, bc + 3, "|")
    _write(g, sky_rows - 2, bc + 2, "/|")
    _write(g, sky_rows - 1, bc,     "_____|")
    _write(g, sky_rows,     bc - 1, "\\_____|/")

    # Waves
    for r in range(sky_rows + 1, h - 1):
        depth = r - sky_rows
        offset = (r * 3) % 7
        for c in range(w):
            base = 0.25 + depth * 0.04
            if (c + offset) % random.randint(3, 7) < 2 and random.random() < base:
                _set(g, r, c, "~")

    # Fish
    for _ in range(random.randint(3, 7)):
        fr = random.randint(sky_rows + 2, h - 2)
        fc = random.randint(1, w - 6)
        _write(g, fr, fc, random.choice(["><>", "<><", "><)>", ">o>"]))

    # Sea floor
    for c in range(w):
        _set(g, h - 1, c, random.choice(["_", "_", "^", "w"]))

    return _lines(g)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate(theme: str, width: int = 80, height: int = 20) -> list[str]:
    """
    Generate a random ASCII art scene.

    Args:
        theme:  One of 'starry-night', 'garden', 'storm', 'forest', 'ocean', 'random'.
        width:  Canvas width in characters.
        height: Canvas height in lines.

    Returns:
        List of strings, one per line.
    """
    theme = theme.lower().strip()
    if theme == "random":
        theme = random.choice(THEMES)
    dispatch = {
        "starry-night": generate_starry_night,
        "garden":       generate_garden,
        "storm":        generate_storm,
        "forest":       generate_forest,
        "ocean":        generate_ocean,
    }
    fn = dispatch.get(theme)
    if fn is None:
        valid = ", ".join(THEMES + ["random"])
        raise ValueError(f"Unknown theme '{theme}'. Available: {valid}")
    return fn(width, height)


# ---------------------------------------------------------------------------
# Rainbow / gradient colorization
# ---------------------------------------------------------------------------

def _hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    """Convert HSL (h: 0-360, s/l: 0-1) to RGB (0-255 each)."""
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if   h < 60:  r, g, b = c, x, 0.0
    elif h < 120: r, g, b = x, c, 0.0
    elif h < 180: r, g, b = 0.0, c, x
    elif h < 240: r, g, b = 0.0, x, c
    elif h < 300: r, g, b = x, 0.0, c
    else:          r, g, b = c, 0.0, x
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


def supports_truecolor() -> bool:
    """Return True if the terminal likely supports 24-bit truecolor."""
    colorterm = os.environ.get("COLORTERM", "").lower()
    return colorterm in ("truecolor", "24bit")


def rainbow_colorize(lines: list[str], cycles: float = 2.0) -> str:
    """
    Wrap each non-space character in ANSI truecolor escape codes,
    cycling through the full hue spectrum across the output.

    Args:
        lines:  Lines of text to colorize.
        cycles: How many full hue rotations across the total output.
    """
    total = sum(len(l) for l in lines)
    step = (360.0 * cycles) / max(total, 1)
    RESET = "\x1b[0m"
    hue = 0.0
    out: list[str] = []
    for line in lines:
        row: list[str] = []
        for ch in line:
            if ch == " ":
                row.append(" ")
            else:
                r, g, b = _hsl_to_rgb(hue % 360, 1.0, 0.55)
                row.append(f"\x1b[38;2;{r};{g};{b}m{ch}{RESET}")
            hue += step
        out.append("".join(row))
    return "\n".join(out)


def rainbow_print(lines: list[str]) -> None:
    """Print lines with rainbow ANSI coloring."""
    print(rainbow_colorize(lines))
