# text2ascii

```text
  _____________  ________   ___      ___   _____ ______________
 /_  __/ ____/ |/ /_  __/  |__ \    /   | / ___// ____/  _/  _/
  / / / __/  |   / / /     __/ /   / /| | \__ \/ /    / / / /
 / / / /___ /   | / /     / __/   / ___ |___/ / /____/ /_/ /
/_/ /_____//_/|_|/_/     /____/  /_/  |_/____/\____/___/___/
```

Convert any text into large ASCII art banners (figlet-style) and chunky Unicode block letters. Works as a CLI tool and as a retro single-page website.

![text2ascii preview](preview.png)

---

## Installation

**Requires Python 3.9+**

```bash
pip install git+https://github.com/jbrodev/text2ascii.git
```

This installs the `text2ascii` command globally.

**For development:**

```bash
git clone https://github.com/jbrodev/text2ascii.git
cd text2ascii
pip install -e .
```

---

## CLI Usage

```
text2ascii "Your Text Here"
```

### Options

| Flag | Short | Description |
|------|-------|-------------|
| `--font NAME` | `-f` | Figlet font (default: `standard`) |
| `--list-fonts` | | List all available fonts |
| `--unicode` | `-u` | Use Unicode block characters (█) |
| `--save FILE` | `-s` | Save output to a text file |
| `--persistent` | `-p` | Write banner command to your shell startup file and save as default |
| `--show` | | Display your saved default banner instantly |
| `--width N` | `-w` | Max width in characters (default: terminal width) |
| `--color NAME` | `-c` | Colorize output (see colors below) |
| `--rainbow` | `-r` | Full-spectrum rainbow gradient |
| `--pattern THEME` | `-P` | Generate a random ASCII art scene |
| `--list-patterns` | | List available scene themes |
| `--height N` | `-H` | Scene height for `--pattern` (default: terminal height) |

**Available colors:** `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`,
`bright_red`, `bright_green`, `bright_yellow`, `bright_blue`, `bright_magenta`, `bright_cyan`, `bright_white`, `rainbow`

> `--color rainbow` and `--rainbow` are interchangeable.

**Available pattern themes:**

| Theme | Description |
|-------|-------------|
| `starry-night` | Night sky with stars, a moon, shooting stars, and a silhouette horizon |
| `garden` | Sun, clouds, flowers with stems and leaves, butterflies |
| `storm` | Storm clouds, rain, lightning bolts, puddles |
| `forest` | Trees of varying heights, ground cover, day or night sky |
| `ocean` | Waves, fish, a sailboat, horizon line, sea floor |
| `random` | Picks one of the above at random each time |

> Every press generates a unique variation — no two scenes are the same.

### Examples

```bash
# Basic usage
text2ascii "Hello World"

# Different font
text2ascii "Hello" --font slant

# Unicode block art
text2ascii "Hi" --unicode

# Colored output
text2ascii "Hello" --font doom --color cyan

# Rainbow gradient
text2ascii "Hello" --color rainbow
text2ascii "Hello" --rainbow

# Pattern scenes
text2ascii --pattern starry-night
text2ascii --pattern random --rainbow
text2ascii --list-patterns

# Save to file
text2ascii "Hello" --save banner.txt

# Show all fonts
text2ascii --list-fonts

# Read from stdin
echo "Hello" | text2ascii -

# Save as default banner (writes to shell startup file)
text2ascii "Hello World" --persistent

# Display your saved default banner on demand
text2ascii --show
```

### Example Output

```text
  _   _      _ _        __        __         _     _ _
 | | | | ___| | | ___   \ \      / /__  _ __| | __| | |
 | |_| |/ _ \ | |/ _ \   \ \ /\ / / _ \| '__| |/ _` | |
 |  _  |  __/ | | (_) |   \ V  V / (_) | |  | | (_| |_|
 |_| |_|\___|_|_|\___/     \_/\_/ \___/|_|  |_|\__,_(_)
```

---

## Making a Banner Permanent

Run with `--persistent` to automatically write the banner command to your shell startup file:

```bash
text2ascii "Hello World" --font doom --persistent
```

This writes the command to the correct profile for your shell and platform, then prints a confirmation with the path and reload instructions. It also saves the banner as your default so `--show` works instantly later.

**Shell and platform support:**

| Platform | Shell | Profile written |
|----------|-------|-----------------|
| Windows | PowerShell (5 or 7) | `$PROFILE` (queried live — works with OneDrive-redirected Documents) |
| Windows | Git Bash / MSYS2 | `~/.bashrc` |
| macOS | zsh (default) | `~/.zshrc` |
| macOS | bash | `~/.bash_profile` |
| macOS / Linux | fish | `~/.config/fish/config.fish` |
| Linux | bash | `~/.bashrc` |
| Linux | zsh | `~/.zshrc` |

> Works in all integrated IDE terminals (VS Code, Cursor, JetBrains, etc.) — the shell detection reads your `SHELL` environment variable, which IDEs inherit automatically.

Reload your shell after running:

```bash
source ~/.bashrc        # bash (Linux)
source ~/.zshrc         # zsh (macOS/Linux)
. $PROFILE              # PowerShell
```

**PowerShell note:** If the banner doesn't appear after reloading, allow local scripts to run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Displaying Your Banner On Demand

Once you've run `--persistent`, you can redisplay your banner at any time — useful for labeling your terminal, marking sections in a session, or just showing it off:

```bash
text2ascii --show
```

No arguments needed. It replays your saved default banner with all the original options (font, color, unicode, etc.). The default is stored in:

- **Windows:** `%APPDATA%\text2ascii\default.json`
- **macOS / Linux:** `~/.config/text2ascii/default.json`

To change your default, just run `--persistent` again with your new settings.

---

## Website

**[jbrodev.github.io/text2ascii](https://jbrodev.github.io/text2ascii/)**

No install required. Open the site, type your text, pick a style and color, then hit Convert.

- Choose from **ASCII art** (15 fonts), **Unicode blocks**, or **Unicode 3D**
- Pick a color — previewed in the terminal, not the browser
- **Copy to clipboard** or **download as `.txt`**
- The **Terminal Commands** panel generates ready-to-paste commands for your shell:
  - Run once in your current session
  - Save permanently so it appears every time you open a terminal
  - Fix it if you accidentally added it twice

---

## Windows Notes

- Use **Windows Terminal** for best Unicode (█) support
- Recommended fonts: **Cascadia Code**, **Consolas**, or **Lucida Console**
- Git Bash, WSL, PowerShell 5, and PowerShell 7 all work
- `--persistent` correctly handles **OneDrive-redirected Documents folders** by querying PowerShell directly for `$PROFILE` rather than assuming a fixed path
- Integrated terminals in **Cursor, VS Code, and JetBrains** are fully supported

---

## Custom Fonts

Drop any `.flf` figlet font file into the `fonts/` directory:

```
text2ascii/
└── fonts/
    └── myfont.flf
```

Then use it with:

```bash
text2ascii "Hello" --font myfont
```

Hundreds of free `.flf` fonts are available at [patorjk.com/software/taag](http://patorjk.com/software/taag) and the [figlet font archive](http://www.figlet.org/fontdb.cgi).

---

## License

MIT — see [LICENSE](LICENSE)
