"""
Unicode block renderer for text2ascii.

Converts text into chunky block-letter art using Unicode block characters.
Each character is rendered as a 5x7 pixel bitmap using block characters like █.

Bitmap encoding: each character is stored as 7 integers.
Each integer encodes one row of 5 pixels, MSB = leftmost pixel.
Bit value 1 = filled pixel, 0 = empty.
Example: 0b11111 (31) = full row █████, 0b10001 (17) = █   █
"""

CHAR_HEIGHT = 7
CHAR_WIDTH = 5
CHAR_GAP = 1  # blank columns between characters

# Block character options (index 0 is default)
BLOCK_CHARS = ["█", "▓", "▒", "░"]

# ---------------------------------------------------------------------------
# 5x7 pixel bitmaps for printable ASCII characters.
# Each list has 7 ints; each int's top 5 bits encode a row (MSB = leftmost).
# Sourced/adapted from classic 5x7 LCD/LED font traditions (public domain).
# Unused characters fall back to a blank of the same dimensions.
# ---------------------------------------------------------------------------
PIXEL_MAP: dict[str, list[int]] = {
    # Uppercase letters (input is normalized to uppercase)
    "A": [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    "B": [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
    "C": [0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
    "D": [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
    "E": [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
    "F": [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
    "G": [0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01110],
    "H": [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    "I": [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11111],
    "J": [0b11111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100],
    "K": [0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
    "L": [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
    "M": [0b10001, 0b11011, 0b10101, 0b10001, 0b10001, 0b10001, 0b10001],
    "N": [0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001],
    "O": [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    "P": [0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
    "Q": [0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
    "R": [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
    "S": [0b01110, 0b10001, 0b10000, 0b01110, 0b00001, 0b10001, 0b01110],
    "T": [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    "U": [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    "V": [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    "W": [0b10001, 0b10001, 0b10001, 0b10001, 0b10101, 0b11011, 0b10001],
    "X": [0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
    "Y": [0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
    "Z": [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
    # Digits
    "0": [0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
    "1": [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11111],
    "2": [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111],
    "3": [0b11111, 0b00010, 0b00100, 0b00110, 0b00001, 0b10001, 0b01110],
    "4": [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
    "5": [0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
    "6": [0b01110, 0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
    "7": [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
    "8": [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
    "9": [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00001, 0b01110],
    # Space
    " ": [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    # Punctuation
    "!": [0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00000, 0b00100],
    ".": [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100],
    "?": [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b00000, 0b00100],
    "-": [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
    "_": [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111],
    "'": [0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    '"': [0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    "(": [0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010],
    ")": [0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000],
    "/": [0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000],
    "\\": [0b10000, 0b01000, 0b01000, 0b00100, 0b00010, 0b00010, 0b00001],
    "@": [0b01110, 0b10001, 0b10111, 0b10101, 0b10111, 0b10000, 0b01110],
    "#": [0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010],
    "+": [0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000],
    "=": [0b00000, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000],
    "*": [0b00000, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0b00000],
    ":": [0b00000, 0b00100, 0b00000, 0b00000, 0b00000, 0b00100, 0b00000],
    ";": [0b00000, 0b00100, 0b00000, 0b00000, 0b00000, 0b00100, 0b01000],
    ",": [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b01000],
    "<": [0b00001, 0b00010, 0b00100, 0b01000, 0b00100, 0b00010, 0b00001],
    ">": [0b10000, 0b01000, 0b00100, 0b00010, 0b00100, 0b01000, 0b10000],
    "[": [0b01110, 0b01000, 0b01000, 0b01000, 0b01000, 0b01000, 0b01110],
    "]": [0b01110, 0b00010, 0b00010, 0b00010, 0b00010, 0b00010, 0b01110],
    "&": [0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101],
    "%": [0b11000, 0b11001, 0b00010, 0b00100, 0b01000, 0b10011, 0b00011],
    "$": [0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100],
    "^": [0b00100, 0b01010, 0b10001, 0b00000, 0b00000, 0b00000, 0b00000],
    "~": [0b00000, 0b01000, 0b10101, 0b00010, 0b00000, 0b00000, 0b00000],
    "`": [0b01000, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    "|": [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    "{": [0b00110, 0b00100, 0b00100, 0b01000, 0b00100, 0b00100, 0b00110],
    "}": [0b01100, 0b00100, 0b00100, 0b00010, 0b00100, 0b00100, 0b01100],
}

# Fallback for unknown characters (blank block)
_BLANK = [0b00000] * CHAR_HEIGHT


def _render_line(chars: list[str], on: str, off: str) -> str:
    """Render a single line of characters as CHAR_HEIGHT rows of block pixels."""
    rows: list[list[str]] = [[] for _ in range(CHAR_HEIGHT)]
    gap = off * CHAR_GAP

    for i, ch in enumerate(chars):
        bitmap = PIXEL_MAP.get(ch.upper(), _BLANK)
        for row_idx in range(CHAR_HEIGHT):
            row_bits = bitmap[row_idx]
            row_str = ""
            for bit_pos in range(CHAR_WIDTH - 1, -1, -1):
                row_str += on if (row_bits >> bit_pos) & 1 else off
            rows[row_idx].append(row_str)

        # Add gap between characters (but not after the last one)
        if i < len(chars) - 1:
            for row_idx in range(CHAR_HEIGHT):
                rows[row_idx].append(gap)

    return "\n".join("".join(row) for row in rows)


def render(
    text: str,
    char: str = "█",
    bg: str = " ",
    width: int | None = None,
) -> str:
    """
    Render text as Unicode block art.

    Args:
        text:  The input text to render.
        char:  The block character to use for filled pixels (default '█').
        bg:    The background character for empty pixels (default ' ').
        width: Maximum output width in characters. Text is word-wrapped.
               If None, no wrapping is applied.

    Returns:
        A multi-line string ready to print.
    """
    if not text:
        return ""

    # Normalize: each character takes CHAR_WIDTH + CHAR_GAP columns,
    # minus the trailing gap on the last char.
    char_render_width = CHAR_WIDTH + CHAR_GAP

    lines: list[str] = []

    if width is not None:
        # Word-wrap: split into words, build lines that fit within width
        words = text.split()
        current_line_words: list[str] = []
        current_width = 0

        for word in words:
            word_width = len(word) * char_render_width - CHAR_GAP
            # +char_render_width for the space separator between words (space char)
            needed = word_width if not current_line_words else current_width + char_render_width + word_width

            if current_line_words and needed > width:
                # Flush current line
                lines.append(_render_line(list(" ".join(current_line_words)), char, bg))
                lines.append("")  # blank line between text lines
                current_line_words = [word]
                current_width = word_width
            else:
                current_line_words.append(word)
                current_width = needed

        if current_line_words:
            lines.append(_render_line(list(" ".join(current_line_words)), char, bg))
    else:
        # Render as-is (may be very wide)
        for line_text in text.splitlines():
            if line_text:
                lines.append(_render_line(list(line_text), char, bg))
                lines.append("")
            else:
                lines.append("")

        # Remove trailing blank line
        while lines and lines[-1] == "":
            lines.pop()

    return "\n".join(lines)


def _build_pixel_grid(text: str) -> list[list[bool]]:
    """
    Build a 2D boolean grid for a single line of text.
    Returns a list of rows, each row a list of bools (True = filled pixel).
    """
    chars = list(text)
    total_cols = len(chars) * (CHAR_WIDTH + CHAR_GAP) - CHAR_GAP
    grid = [[False] * total_cols for _ in range(CHAR_HEIGHT)]

    col_offset = 0
    for ch in chars:
        bitmap = PIXEL_MAP.get(ch.upper(), _BLANK)
        for row_idx in range(CHAR_HEIGHT):
            for bit_pos in range(CHAR_WIDTH - 1, -1, -1):
                col = col_offset + (CHAR_WIDTH - 1 - bit_pos)
                grid[row_idx][col] = bool((bitmap[row_idx] >> bit_pos) & 1)
        col_offset += CHAR_WIDTH + CHAR_GAP

    return grid


def render_3d(
    text: str,
    width: int | None = None,
    depth: int = 1,
) -> str:
    """
    Render text as Unicode block art with a 3D drop-shadow effect.

    The front face uses '█', the shadow uses '░', and pixels where
    both overlap use '▓', creating a diagonal depth illusion.

    Args:
        text:  Input text.
        width: Max output width for word-wrapping.
        depth: Shadow offset in pixels (default 2).

    Returns:
        A multi-line string ready to print.
    """
    if not text:
        return ""

    char_render_width = CHAR_WIDTH + CHAR_GAP

    # Collect lines of text (word-wrapped if width given)
    text_lines: list[str] = []
    if width is not None:
        words = text.split()
        current_words: list[str] = []
        current_w = 0
        for word in words:
            word_w = len(word) * char_render_width - CHAR_GAP
            needed = word_w if not current_words else current_w + char_render_width + word_w
            if current_words and needed > width:
                text_lines.append(" ".join(current_words))
                current_words = [word]
                current_w = word_w
            else:
                current_words.append(word)
                current_w = needed
        if current_words:
            text_lines.append(" ".join(current_words))
    else:
        text_lines = [l for l in text.splitlines() if l] or [text]

    output_lines: list[str] = []

    for line_text in text_lines:
        grid = _build_pixel_grid(line_text)
        rows = len(grid)
        cols = len(grid[0]) if grid else 0

        # Canvas is expanded by depth in both directions for the shadow
        canvas_rows = rows + depth
        canvas_cols = cols + depth

        # Build combined canvas: 0=bg, 1=shadow only, 2=main only, 3=both
        canvas = [[0] * canvas_cols for _ in range(canvas_rows)]

        # Place shadow (offset +depth rows, +depth cols)
        for r in range(rows):
            for c in range(cols):
                if grid[r][c]:
                    canvas[r + depth][c + depth] |= 1

        # Place main layer
        for r in range(rows):
            for c in range(cols):
                if grid[r][c]:
                    canvas[r][c] |= 2

        # Map to characters
        _map = {0: " ", 1: "░", 2: "█", 3: "▓"}
        rendered_rows = ["".join(_map[canvas[r][c]] for c in range(canvas_cols)) for r in range(canvas_rows)]

        # Strip trailing spaces from each row
        output_lines.extend(row.rstrip() for row in rendered_rows)
        output_lines.append("")

    # Remove trailing blank line
    while output_lines and output_lines[-1] == "":
        output_lines.pop()

    return "\n".join(output_lines)
