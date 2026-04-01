"""
text2ascii CLI — Convert text into ASCII art banners and Unicode block art.

Usage:
    text2ascii "Hello World"
    text2ascii "Hello" --font slant --color cyan
    text2ascii "Hi" --unicode
    text2ascii "Hello" --save output.txt
    text2ascii "Hello" --persistent
    text2ascii --list-fonts
"""

import argparse
import os
import pydoc
import shutil
import sys

import colorama
import pyfiglet

from text2ascii.unicode_renderer import render as _unicode_render

# ---------------------------------------------------------------------------
# Color name → colorama constant mapping
# ---------------------------------------------------------------------------
_COLOR_MAP = {
    "red": colorama.Fore.RED,
    "green": colorama.Fore.GREEN,
    "yellow": colorama.Fore.YELLOW,
    "blue": colorama.Fore.BLUE,
    "magenta": colorama.Fore.MAGENTA,
    "cyan": colorama.Fore.CYAN,
    "white": colorama.Fore.WHITE,
    "bright_red": colorama.Fore.LIGHTRED_EX,
    "bright_green": colorama.Fore.LIGHTGREEN_EX,
    "bright_yellow": colorama.Fore.LIGHTYELLOW_EX,
    "bright_blue": colorama.Fore.LIGHTBLUE_EX,
    "bright_magenta": colorama.Fore.LIGHTMAGENTA_EX,
    "bright_cyan": colorama.Fore.LIGHTCYAN_EX,
    "bright_white": colorama.Fore.LIGHTWHITE_EX,
}

_VALID_COLORS = sorted(_COLOR_MAP.keys())


def setup_windows_utf8() -> None:
    """Configure Windows terminal for UTF-8 output (no-op on other platforms)."""
    if sys.platform != "win32":
        return
    # Silently set UTF-8 code page in the console
    os.system("chcp 65001 >nul 2>&1")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        # May fail in IDLE, pytest capture, or redirected contexts — ignore
        pass


def render_figlet(text: str, font: str = "standard", width: int | None = None) -> str:
    """
    Render text using a figlet font via pyfiglet.

    Args:
        text:  Input text.
        font:  Figlet font name (default 'standard').
        width: Max output width. Uses terminal width if None.

    Returns:
        Rendered ASCII art string.

    Raises:
        SystemExit: If the font is not found.
    """
    if width is None:
        width = shutil.get_terminal_size(fallback=(80, 24)).columns

    try:
        return pyfiglet.figlet_format(text, font=font, width=width)
    except pyfiglet.FontNotFound:
        _fatal(
            f"Font '{font}' not found.\n"
            f"Run 'text2ascii --list-fonts' to see all available fonts."
        )


def list_fonts() -> None:
    """Print all available figlet fonts, paginated."""
    fonts = sorted(pyfiglet.FigletFont.getFonts())
    term_width = shutil.get_terminal_size(fallback=(80, 24)).columns
    col_width = 22
    cols = max(1, term_width // col_width)

    lines = [f"Available fonts ({len(fonts)} total):", ""]
    for i in range(0, len(fonts), cols):
        row = fonts[i : i + cols]
        lines.append("  " + "  ".join(f.ljust(col_width - 2) for f in row))

    lines += ["", "Usage: text2ascii 'text' --font <name>"]
    pydoc.pager("\n".join(lines))


def colorize(text: str, color_name: str) -> str:
    """Wrap text with ANSI color codes using colorama."""
    fore = _COLOR_MAP.get(color_name.lower())
    if fore is None:
        return text
    return fore + text + colorama.Style.RESET_ALL


def print_persistent_instructions(output: str, args: argparse.Namespace) -> None:
    """
    Print the banner and instructions for making it permanent in the user's
    shell startup file. Never writes any files automatically.
    """
    print(output)
    print()
    print("─" * 60)
    print("  HOW TO MAKE THIS BANNER PERMANENT")
    print("─" * 60)

    # Reconstruct the command that was run (minus --persistent)
    parts = ["text2ascii"]
    if args.text:
        parts.append(f'"{args.text}"')
    if args.font and args.font != "standard":
        parts.extend(["-f", args.font])
    if args.unicode:
        parts.append("-u")
    if args.color:
        parts.extend(["-c", args.color])
    if args.width:
        parts.extend(["-w", str(args.width)])
    cmd = " ".join(parts)

    line_to_add = cmd

    if sys.platform == "win32":
        shell = os.environ.get("SHELL", "")
        if shell:
            # Git Bash / MSYS on Windows
            profile = os.path.expanduser("~/.bashrc")
            print(f"\n  Shell startup file: {profile}")
            print(f"\n  Add this line to run your banner on every terminal open:")
            print(f'\n      echo \'{line_to_add}\' >> "{profile}"')
            print(f"  Or open {profile} in a text editor and add:")
            print(f"\n      {line_to_add}")
        else:
            # PowerShell
            profile = os.path.expandvars(
                r"%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
            )
            print(f"\n  PowerShell profile: {profile}")
            print(f"\n  Run these commands in PowerShell:")
            print(f"\n      # Create profile if it doesn't exist:")
            print(f"      New-Item -Force -ItemType File -Path $PROFILE | Out-Null")
            print(f"\n      # Add your banner command:")
            print(f'      Add-Content -Path $PROFILE -Value \'{line_to_add}\'')
    elif sys.platform == "darwin":
        profile = os.path.expanduser("~/.zshrc")
        print(f"\n  Shell startup file: {profile}")
        print(f"\n  Run this to add your banner permanently:")
        print(f'\n      echo \'{line_to_add}\' >> {profile}')
        print(f"\n  Or open {profile} in a text editor and add:")
        print(f"\n      {line_to_add}")
    else:
        profile = os.path.expanduser("~/.bashrc")
        print(f"\n  Shell startup file: {profile}")
        print(f"\n  Run this to add your banner permanently:")
        print(f'\n      echo \'{line_to_add}\' >> {profile}')
        print(f"\n  Or open {profile} in a text editor and add:")
        print(f"\n      {line_to_add}")

    print()
    print("  After editing, reload your shell with:  source " + (
        profile if sys.platform != "win32" else "$PROFILE"
    ))
    print("─" * 60)


def _fatal(message: str) -> None:
    """Print an error message to stderr and exit with code 1."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="text2ascii",
        description="Convert text into large ASCII art banners and Unicode block art.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  text2ascii \"Hello World\"\n"
            "  text2ascii \"Hello\" --font slant --color cyan\n"
            "  text2ascii \"Hi\" --unicode\n"
            "  text2ascii \"Hello\" --save banner.txt\n"
            "  text2ascii \"Hello\" --persistent\n"
            "  text2ascii --list-fonts"
        ),
    )

    parser.add_argument(
        "text",
        nargs="?",
        help='Text to convert. Use - to read from stdin.',
    )
    parser.add_argument(
        "-f", "--font",
        default="standard",
        metavar="FONT",
        help='Figlet font name (default: standard). See --list-fonts.',
    )
    parser.add_argument(
        "--list-fonts",
        action="store_true",
        help="List all available figlet fonts and exit.",
    )
    parser.add_argument(
        "-u", "--unicode",
        action="store_true",
        help="Use Unicode block characters (█) instead of figlet ASCII art.",
    )
    parser.add_argument(
        "-s", "--save",
        metavar="FILE",
        help="Save the output to a text file.",
    )
    parser.add_argument(
        "-p", "--persistent",
        action="store_true",
        help="Print instructions for adding this banner to your shell startup file.",
    )
    parser.add_argument(
        "-w", "--width",
        type=int,
        default=None,
        metavar="N",
        help="Maximum output width in characters (default: terminal width).",
    )
    parser.add_argument(
        "-c", "--color",
        choices=_VALID_COLORS,
        metavar="COLOR",
        help=f"Colorize output. Choices: {', '.join(_VALID_COLORS)}",
    )
    return parser


def main() -> None:
    """CLI entry point."""
    # Initialize colorama for cross-platform ANSI support
    colorama.init(autoreset=True)

    # Handle Windows UTF-8 setup before any output
    setup_windows_utf8()

    parser = _build_parser()
    args = parser.parse_args()

    # --list-fonts: show available fonts and exit
    if args.list_fonts:
        list_fonts()
        return

    # Get input text
    if args.text is None:
        parser.print_help()
        return
    elif args.text == "-":
        text = sys.stdin.read().strip()
        if not text:
            _fatal("No text received from stdin.")
    else:
        text = args.text

    if not text.strip():
        _fatal("Please provide non-empty text to convert.")

    # Determine render width
    width = args.width or shutil.get_terminal_size(fallback=(80, 24)).columns

    # Render
    if args.unicode:
        output = _unicode_render(text, width=width)
    else:
        output = render_figlet(text, font=args.font, width=width)

    if not output.strip():
        _fatal("Rendering produced empty output. Try a different font or input.")

    # Apply color
    if args.color:
        output = colorize(output, args.color)

    # Save to file
    if args.save:
        try:
            with open(args.save, "w", encoding="utf-8") as f:
                # Write without ANSI codes if colorized
                clean = output
                if args.color:
                    # Strip ANSI for file output
                    import re
                    clean = re.sub(r"\x1b\[[0-9;]*m", "", output)
                f.write(clean)
            print(f"Saved to {args.save}", file=sys.stderr)
        except OSError as e:
            _fatal(f"Could not write to '{args.save}': {e}")

    # Persistent instructions or plain print
    if args.persistent:
        print_persistent_instructions(output, args)
    else:
        print(output)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(file=sys.stderr)  # newline after ^C
        raise SystemExit(0)
