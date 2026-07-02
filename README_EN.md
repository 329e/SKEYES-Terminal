# SKEYES Terminal

**SKEYES Terminal** is a standalone Windows application (`.exe`) that
is itself a command terminal: a black, neon-green themed window
(matching the SKEYES logo) where you type system commands just like
in `cmd.exe` or Git Bash — with the addition of multiple tabs,
autocompletion, session saving, and a fully customizable
configuration.

No installation needed on the target machine: once built,
`SKEYES_Terminal.exe` runs entirely on its own.

---

## Table of contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Commands and shortcuts](#commands-and-shortcuts)
- [Customization (config.json)](#customization-configjson)
- [Project structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Features

### Full terminal
- Runs any system command, just like a real terminal.
- **Two shells to choose from**, switchable on the fly: `cmd.exe`
  (Windows) or **Git Bash**.
- The working directory is preserved between commands (`cd` behaves
  as expected).

### Multiple tabs
- Open several independent terminal sessions in the same window
  (`+ Tab` button), each with its own directory, shell, and history.
- Close a tab with the **✕** button or `Ctrl+W`.

### Real-time output
- Command output is displayed **as it's produced** (streaming), not
  only once the command finishes — useful for long-running commands.
- `stdout` (normal output) and `stderr` (errors) are shown in
  **different colors**.
- **■ Stop** button to interrupt a running command.

### Proper handling of interactive commands
- Full-screen programs like `nano`, `vim`, `less`, `top`, `ssh`,
  `git log`, `python`, etc. need a real terminal (TTY) to work.
  SKEYES Terminal automatically detects them and opens them in a
  **real, separate console window**, where they run normally.
- If a regular command stays silent for more than a few seconds, an
  info message warns you it might be waiting for input.

### Quality of life
- **Tab-completion** for known commands and file paths.
- Command history navigable with the Up/Down arrow keys.
- `Ctrl+L` clears the screen (like `clear`), while keeping the banner
  and info messages visible.
- **💾 Save** button: exports the active tab's content to a
  timestamped `.txt` file (`logs/` folder).

### Customizable without recompiling
- Colors, font, ASCII banner, environment variables, and command
  lists are all driven by an external `config.json` file, freely
  editable.

---

## Installation

### Requirements (on the machine you build from)
- **Windows**
- **Python 3.9 or later**, with `pip` available in `PATH`
- (Recommended) **Git Bash** installed, to use the built-in bash
  shell: https://git-scm.com/downloads

### Steps

1. **Copy the whole project folder** onto your Windows machine.

2. **Run the automatic build**: double-click `build\build.bat`.
   This script will:
   - install `PyInstaller` if needed,
   - compile the app into a single `.exe` file,
   - apply the SKEYES icon,
   - copy `config.json` and `icon.ico` next to the exe,
   - create the `logs/` folder.

   Result: `dist\SKEYES_Terminal.exe` (+ `config.json`, `icon.ico`,
   `logs\`).

3. **(Optional) Create a desktop shortcut**: double-click
   `build\create_shortcut.bat`. It adds a shortcut with the SKEYES
   icon to your desktop.

4. **(Optional) Sign the executable** if you own a code-signing
   certificate: `build\sign.bat "certificate.pfx" "password"`. This
   avoids the Windows SmartScreen warning on first launch. Without a
   certificate, you can skip this — just click "More info" → "Run
   anyway" the first time.

Once these steps are done, **you can copy the `dist\` folder**
(exe + config.json + icon.ico + logs\) **to any other Windows
machine**: no Python or recompiling needed.

---

## Usage

Double-click `SKEYES_Terminal.exe` (or your desktop shortcut).

The window opens with the SKEYES banner and a first tab
"Terminal 1". Type a command in the field at the bottom and press
Enter:

```
[cmd] C:\Users\you> dir
[cmd] C:\Users\you> cd Documents
[cmd] C:\Users\you\Documents> git status
```

- Use the **CMD** / **Git Bash** buttons at the top to choose which
  shell runs your commands (or type `!cmd` / `!bash`).
- Open a new tab with **+ Tab** for a parallel session.
- Close a tab with **✕** or `Ctrl+W`.
- A command like `nano file.txt` will automatically open a dedicated
  console window, since `nano` needs a real terminal.

---

## Commands and shortcuts

| Command / Shortcut     | Effect |
|--------------------------|--------------------------------------------|
| `help`                   | Shows help inside the terminal              |
| `clear` / `cls`          | Clears the screen (banner reappears)        |
| `cd <path>`              | Changes the current directory               |
| `!cmd`                   | Switches execution to `cmd.exe`             |
| `!bash`                  | Switches execution to Git Bash              |
| `exit` / `quit`          | Closes the active tab (or the app if last)  |
| `Tab`                    | Command / path autocompletion               |
| `Ctrl+L`                 | Clears the screen                           |
| `Ctrl+W`                 | Closes the active tab                       |
| Up / Down arrows         | Navigates command history                   |
| **+ Tab** button          | Opens a new terminal session                |
| **■ Stop** button         | Interrupts the running command              |
| **💾 Save** button         | Exports the session to `logs/`             |

---

## Customization (config.json)

The `config.json` file (next to the exe) controls the app's
appearance and behavior, without recompiling:

```json
{
  "colors": {
    "bg": "#000000",
    "fg": "#39FF88",
    "error": "#ff5555",
    "stdout": "#39FF88",
    "stderr": "#ffb347"
  },
  "font_family": ["Cascadia Mono", "Consolas", "Courier New"],
  "font_size": 11,
  "banner": "Your own ASCII text/logo here",
  "env": {
    "MY_VARIABLE": "value"
  },
  "interactive_commands": ["nano", "vim", "ssh", "..."],
  "known_commands": ["dir", "cd", "git", "..."],
  "stuck_warning_seconds": 4
}
```

- **colors**: every color used in the interface.
- **font_family / font_size**: the font used (first one found on the
  system from the list).
- **banner**: the text shown on startup and after `clear`.
- **env**: environment variables injected into every command that
  runs.
- **interactive_commands**: commands opened in a separate console
  window.
- **known_commands**: commands suggested by `Tab` autocompletion.
- **stuck_warning_seconds**: delay before the "stuck command" warning.

Only the keys you want to change need to be present in the file;
defaults cover the rest.

---

## Project structure

```
SKEYES_Terminal/
├── app/
│   ├── terminal_app.py      <- Application source code
│   ├── config.json           <- Configuration (colors, env, ...)
│   ├── icon.ico               <- SKEYES icon
│   └── logo_source.png        <- Original logo
├── build/
│   ├── build.bat              <- Automatically builds the exe
│   ├── create_shortcut.bat    <- Creates a desktop shortcut
│   └── sign.bat                <- Optional exe signing
├── logs/                       <- Saved sessions (Save button)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Troubleshooting

**"Standard input is not a terminal" or garbled output**
→ You ran an interactive command that wasn't recognized as such. Add
it to `interactive_commands` in `config.json`.

**Windows SmartScreen blocks the exe**
→ Normal for an unsigned executable. Click "More info" → "Run
anyway", or sign the exe with `build\sign.bat` if you have a
certificate.

**Git Bash not detected**
→ Install Git for Windows (https://git-scm.com/downloads), make sure
`bash.exe` is in `PATH`, or add its exact path to
`GIT_BASH_CANDIDATES` (`app/terminal_app.py`).

**Can't type in the terminal**
→ Click once inside the input field at the bottom of the window to
give it focus.

**A command seems stuck**
→ Check for a "command isn't responding" message; click **■ Stop**
then relaunch it (known interactive commands automatically open in a
dedicated window).
