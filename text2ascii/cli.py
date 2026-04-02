"""
text2ascii CLI — Convert text into ASCII art banners and Unicode block art.

Usage:
    text2ascii "Hello World"
    text2ascii "Hello" --font slant --color cyan
    text2ascii "Hi" --unicode
    text2ascii "Hello" --save output.txt
    text2ascii "Hello" --persistent
    text2ascii --show
    text2ascii --list-fonts
"""

import argparse
import json
import os
import pydoc
import shutil
import subprocess
import sys

import colorama
import pyfiglet

from text2ascii.unicode_renderer import render as _unicode_render, render_3d as _unicode_render_3d
from text2ascii import patterns as _patterns

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

_VALID_COLORS = sorted(_COLOR_MAP.keys()) + ["rainbow"]


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


def _get_profile_path() -> tuple[str, bool]:
    """
    Return (profile_path, is_powershell) for the current platform/shell.
    """
    if sys.platform == "win32":
        shell = os.environ.get("SHELL", "")
        if shell:
            return os.path.expanduser("~/.bashrc"), False
        # Query PowerShell for its actual $PROFILE path so OneDrive-redirected
        # Documents folders and different PS versions (5 vs 7) are handled correctly.
        for ps_exe in ("pwsh", "powershell"):
            try:
                result = subprocess.run(
                    [ps_exe, "-NoProfile", "-Command", "$PROFILE"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    path = result.stdout.strip()
                    if path:
                        return path, True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        # Fallback: use the classic PS5 path (may be wrong on OneDrive setups)
        profile = os.path.expandvars(
            r"%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
        )
        return profile, True
    elif sys.platform == "darwin":
        shell = os.environ.get("SHELL", "")
        if "fish" in shell:
            return os.path.expanduser("~/.config/fish/config.fish"), False
        if "zsh" in shell or not shell:
            return os.path.expanduser("~/.zshrc"), False
        # bash on macOS: terminal apps open a login shell, which sources .bash_profile
        return os.path.expanduser("~/.bash_profile"), False
    else:
        shell = os.environ.get("SHELL", "")
        if "zsh" in shell:
            return os.path.expanduser("~/.zshrc"), False
        if "fish" in shell:
            return os.path.expanduser("~/.config/fish/config.fish"), False
        return os.path.expanduser("~/.bashrc"), False


def _build_banner_command(args: argparse.Namespace) -> str:
    """Reconstruct the text2ascii command from args (minus --persistent)."""
    parts = ["text2ascii"]
    if args.text:
        parts.append(f'"{args.text}"')
    if args.font and args.font != "standard":
        parts.extend(["-f", args.font])
    if args.unicode:
        parts.append("-u")
    if getattr(args, "three_d", False):
        parts.append("--3d")
    if args.color == "rainbow" or args.rainbow:
        parts.append("--rainbow")
    elif args.color:
        parts.extend(["-c", args.color])
    if args.width:
        parts.extend(["-w", str(args.width)])
    return " ".join(parts)


def save_persistent_banner(output: str, args: argparse.Namespace) -> None:
    """
    Print the banner then write the banner command to the shell startup file
    so it runs automatically on every new terminal session.
    Checks for duplicates before writing.
    """
    print(output)
    print()

    profile, is_powershell = _get_profile_path()
    cmd = _build_banner_command(args)

    # Check for duplicate
    if os.path.exists(profile):
        try:
            existing = open(profile, encoding="utf-8", errors="replace").read()
            if cmd in existing:
                print(f"Banner command already in {profile} — nothing to do.")
                return
        except OSError:
            pass

    # For PowerShell, ensure the profile directory exists
    if is_powershell:
        os.makedirs(os.path.dirname(profile), exist_ok=True)

    try:
        with open(profile, "a", encoding="utf-8") as f:
            f.write(f"\n# text2ascii banner\n{cmd}\n")
        print("─" * 60)
        print(f"  Banner saved to: {profile}")
        print(f"  Command added:   {cmd}")
        print()
        if is_powershell:
            print("  Reload with:  . $PROFILE")
            print()
            print("  If the banner doesn't appear, allow scripts to run once with:")
            print("    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")
        else:
            print(f"  Reload with:  source {profile}")
        print("─" * 60)
    except OSError as e:
        _fatal(f"Could not write to '{profile}': {e}")


def _save_plain(output: str, path: str) -> None:
    """Write output to a file, stripping ANSI escape codes."""
    import re
    clean = re.sub(r"\x1b\[[0-9;]*m", "", output)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(clean)
        print(f"Saved to {path}", file=sys.stderr)
    except OSError as e:
        _fatal(f"Could not write to '{path}': {e}")


def _get_default_config_path() -> str:
    """Return the path to the saved default banner config file."""
    if sys.platform == "win32":
        base = os.path.expandvars(r"%APPDATA%\text2ascii")
    else:
        base = os.path.expanduser("~/.config/text2ascii")
    return os.path.join(base, "default.json")


def save_default_config(args: argparse.Namespace) -> None:
    """Persist the banner args to the default config so --show can replay them."""
    config = {
        "text": args.text,
        "font": args.font,
        "unicode": args.unicode,
        "three_d": getattr(args, "three_d", False),
        "color": args.color,
        "rainbow": args.rainbow,
        "width": args.width,
    }
    path = _get_default_config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f)
    except OSError as e:
        _fatal(f"Could not save default config to '{path}': {e}")


def show_default_banner() -> None:
    """Load and display the saved default banner (set via --persistent)."""
    path = _get_default_config_path()
    if not os.path.exists(path):
        _fatal(
            "No default banner saved yet. "
            "Run: text2ascii \"your text\" --persistent"
        )
    try:
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        _fatal(f"Could not read default config: {e}")

    text = config.get("text") or ""
    if not text.strip():
        _fatal("Saved default banner has no text.")

    width = config.get("width") or shutil.get_terminal_size(fallback=(80, 24)).columns

    if config.get("three_d"):
        output = _unicode_render_3d(text, width=width)
    elif config.get("unicode"):
        output = _unicode_render(text, width=width)
    else:
        output = render_figlet(text, font=config.get("font") or "standard", width=width)

    if config.get("rainbow") or config.get("color") == "rainbow":
        output = _patterns.rainbow_colorize(output.splitlines())
    elif config.get("color"):
        output = colorize(output, config["color"])

    print(output)


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
        "--3d",
        dest="three_d",
        action="store_true",
        help="Add a 3D drop-shadow effect to Unicode block output (implies --unicode).",
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
        "--show",
        action="store_true",
        help="Display your saved default banner instantly (set with --persistent).",
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
    parser.add_argument(
        "-P", "--pattern",
        metavar="THEME",
        help=(
            f"Generate a random ASCII art scene. "
            f"Themes: {', '.join(_patterns.THEMES + ['random'])}. "
            f"Use --list-patterns to see all."
        ),
    )
    parser.add_argument(
        "--list-patterns",
        action="store_true",
        help="List available scene themes and exit.",
    )
    parser.add_argument(
        "-r", "--rainbow",
        action="store_true",
        help="Apply a full-spectrum rainbow gradient (works with --pattern and banners).",
    )
    parser.add_argument(
        "-H", "--height",
        type=int,
        default=None,
        metavar="N",
        help="Scene height in lines for --pattern (default: terminal height).",
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

    # --show: replay the saved default banner
    if args.show:
        show_default_banner()
        return

    # --list-fonts
    if args.list_fonts:
        list_fonts()
        return

    # --list-patterns
    if args.list_patterns:
        print("Available scene themes:")
        for t in _patterns.THEMES:
            print(f"  {t}")
        print("  random  (picks one at random)")
        print("\nUsage: text2ascii --pattern starry-night --rainbow")
        return

    # --pattern: generate a scene instead of converting text
    if args.pattern:
        term = shutil.get_terminal_size(fallback=(80, 24))
        width  = args.width  or term.columns
        height = args.height or max(10, term.lines - 4)
        try:
            lines = _patterns.generate(args.pattern, width=width, height=height)
        except ValueError as e:
            _fatal(str(e))

        if args.rainbow:
            output = _patterns.rainbow_colorize(lines)
        else:
            output = "\n".join(lines)

        if args.save:
            _save_plain(output, args.save)
        else:
            print(output)
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

    # Render banner
    if args.three_d:
        output = _unicode_render_3d(text, width=width)
    elif args.unicode:
        output = _unicode_render(text, width=width)
    else:
        output = render_figlet(text, font=args.font, width=width)

    if not output.strip():
        _fatal("Rendering produced empty output. Try a different font or input.")

    # Apply rainbow or solid color ("rainbow" accepted as --color value too)
    if args.rainbow or args.color == "rainbow":
        output = _patterns.rainbow_colorize(output.splitlines())
    elif args.color:
        output = colorize(output, args.color)

    # Save to file
    if args.save:
        _save_plain(output, args.save)

    # Persistent: write command to shell startup file and save default config
    if args.persistent:
        save_persistent_banner(output, args)
        save_default_config(args)
    else:
        print(output)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(file=sys.stderr)  # newline after ^C
        raise SystemExit(0)
