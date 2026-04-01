"""
text2ascii — Convert text to ASCII art banners and Unicode block art.

Usage as a library:
    from text2ascii import render_figlet, render_unicode
"""

__version__ = "0.1.0"

from text2ascii.unicode_renderer import render as render_unicode

def render_figlet(text: str, font: str = "standard", width: int | None = None) -> str:
    """Render text using a figlet font. See text2ascii.cli for full CLI options."""
    from text2ascii.cli import render_figlet as _rf
    return _rf(text, font=font, width=width)

__all__ = ["render_figlet", "render_unicode", "__version__"]
