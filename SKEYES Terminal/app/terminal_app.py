"""
SKEYES Terminal v5
-------------------
Terminal Windows autonome (Tkinter), shell CMD ou Git Bash au choix,
avec toutes les améliorations demandées :

Robustesse
  - Décodage UTF-8 tolérant (errors="replace") : plus de crash sur
    accents/caractères spéciaux.
  - Sortie affichée en STREAMING (ligne par ligne) au lieu d'attendre
    la fin de la commande.
  - Bouton "Stop" pour interrompre une commande en cours.

UX
  - stdout et stderr affichés dans des couleurs différentes.
  - Autocomplétion (Tab) des commandes connues et des chemins de fichiers.
  - Détection heuristique de commande "bloquée" (attend une entrée
    interactive) au-delà d'un délai configurable -> avertissement.
  - Onglets multiples : plusieurs sessions de terminal indépendantes
    dans la même fenêtre (bouton "+ Onglet").

Fonctionnalités
  - Bouton "Save" : exporte la session affichée dans un fichier .txt
    horodaté (dossier logs/).
  - Configuration externe app/config.json : couleurs, police, bannière,
    variables d'environnement, liste de commandes interactives/connues.
  - Variables d'environnement personnalisées injectées depuis config.json.
  - Ctrl+L : efface l'écran (comme la commande clear) sans taper de commande.
    (clear/cls réaffiche toujours la bannière, comme en v4.)

Commandes internes :
  help          -> affiche l'aide
  clear / cls   -> efface l'écran (bannière réaffichée)
  exit / quit   -> ferme l'onglet (ou l'appli si dernier onglet)
  cd <chemin>   -> change le répertoire courant
  !cmd          -> bascule le shell d'exécution sur cmd.exe
  !bash         -> bascule le shell d'exécution sur Git Bash
"""

import os
import sys
import json
import time
import shutil
import datetime
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

APP_TITLE = "SKEYES Terminal v6"

DEFAULT_CONFIG = {
    "colors": {
        "bg": "#000000", "fg": "#39FF88", "fg_dim": "#1f8f52",
        "prompt": "#7CFFB2", "error": "#ff5555", "info": "#5fd3ff",
        "stdout": "#39FF88", "stderr": "#ffb347",
        "button_bg": "#0a1f12", "button_active_bg": "#123a20",
        "input_bg": "#020402",
    },
    "font_family": ["Cascadia Mono", "Consolas", "Courier New"],
    "font_size": 11,
    "banner": "\n>_ SKEYES TERMINAL v5 </>   -   tape 'help'\n",
    "env": {},
    "interactive_commands": [
        "nano", "vim", "vi", "emacs", "pico", "less", "more", "man",
        "top", "htop", "ssh", "telnet", "ftp", "sftp", "python",
        "python3", "py", "node", "irb", "psql", "mysql", "git", "tig",
    ],
    "known_commands": [
        "dir", "cls", "clear", "cd", "help", "exit", "quit", "echo",
        "copy", "move", "del", "type", "git", "python", "ping", "ls",
        "pwd", "cat", "grep", "nano", "vim", "ssh",
    ],
    "stuck_warning_seconds": 4,
}

GIT_BASH_CANDIDATES = [
    r"C:\Program Files\Git\bin\bash.exe",
    r"C:\Program Files (x86)\Git\bin\bash.exe",
    r"C:\Git\bin\bash.exe",
]


def base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def load_config():
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # copie profonde
    cfg_path = os.path.join(base_path(), "config.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as fh:
                user_cfg = json.load(fh)
            for key, value in user_cfg.items():
                if isinstance(value, dict) and isinstance(cfg.get(key), dict):
                    cfg[key].update(value)
                else:
                    cfg[key] = value
        except Exception as exc:
            print(f"[SKEYES] config.json invalide, valeurs par défaut utilisées : {exc}")
    return cfg


def find_git_bash():
    which = shutil.which("bash")
    if which:
        return which
    for path in GIT_BASH_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def pick_font_family(preferred_list):
    available = set(tkfont.families())
    for name in preferred_list:
        if name in available:
            return name
    return "Courier"


class TerminalSession(tk.Frame):
    """Un onglet = une session de terminal indépendante."""

    def __init__(self, parent, app, session_num):
        super().__init__(parent, bg=app.colors["bg"])
        self.app = app
        self.session_num = session_num
        c = app.colors

        self.bash_path = app.bash_path
        self.shell_mode = "cmd"
        self.cwd = os.path.expanduser("~")
        self.history = []
        self.history_index = -1
        self.result_queue = queue.Queue()
        self.current_proc = None
        self.last_output_time = None
        self.stuck_warned = False
        self.cmd_start_time = None

        # --- barre du haut (par onglet) ---
        top_bar = tk.Frame(self, bg=c["bg"])
        top_bar.pack(fill="x", side="top")

        self.cmd_btn = tk.Button(
            top_bar, text="CMD", command=lambda: self.set_shell("cmd"),
            bg=c["button_active_bg"], fg=c["fg"], activebackground=c["button_active_bg"],
            activeforeground=c["fg"], relief="flat", font=app.text_font, padx=10, pady=3,
        )
        self.cmd_btn.pack(side="left", padx=(8, 3), pady=5)

        self.bash_btn = tk.Button(
            top_bar, text="Git Bash", command=lambda: self.set_shell("bash"),
            bg=c["button_bg"], fg=c["fg_dim"], activebackground=c["button_active_bg"],
            activeforeground=c["fg"], relief="flat", font=app.text_font, padx=10, pady=3,
        )
        self.bash_btn.pack(side="left", padx=3, pady=5)

        self.stop_btn = tk.Button(
            top_bar, text="■ Stop", command=self.stop_current,
            bg=c["button_bg"], fg=c["error"], activebackground=c["button_active_bg"],
            activeforeground=c["error"], relief="flat", font=app.text_font, padx=10, pady=3,
        )
        self.stop_btn.pack(side="left", padx=3, pady=5)

        self.save_btn = tk.Button(
            top_bar, text="💾 Save", command=self.save_log,
            bg=c["button_bg"], fg=c["info"], activebackground=c["button_active_bg"],
            activeforeground=c["info"], relief="flat", font=app.text_font, padx=10, pady=3,
        )
        self.save_btn.pack(side="left", padx=3, pady=5)

        self.close_btn = tk.Button(
            top_bar, text="✕ Fermer l'onglet", command=lambda: app.close_session(self),
            bg=c["button_bg"], fg=c["error"], activebackground=c["button_active_bg"],
            activeforeground=c["error"], relief="flat", font=app.text_font, padx=10, pady=3,
        )
        self.close_btn.pack(side="left", padx=3, pady=5)

        status = "détecté" if self.bash_path else "introuvable"
        self.status_label = tk.Label(
            top_bar, text=f"Git Bash: {status}", bg=c["bg"], fg=c["fg_dim"], font=app.text_font,
        )
        self.status_label.pack(side="right", padx=10)

        # --- zone de sortie ---
        self.output = tk.Text(
            self, bg=c["bg"], fg=c["fg"], insertbackground=c["fg"],
            font=app.text_font, wrap="word", borderwidth=0,
            highlightthickness=0, padx=10, pady=8,
        )
        self.output.pack(fill="both", expand=True, side="top")
        self.output.tag_configure("prompt", foreground=c["prompt"])
        self.output.tag_configure("error", foreground=c["error"])
        self.output.tag_configure("info", foreground=c["info"])
        self.output.tag_configure("dim", foreground=c["fg_dim"])
        self.output.tag_configure("stdout", foreground=c["stdout"])
        self.output.tag_configure("stderr", foreground=c["stderr"])
        self.output.configure(state="disabled")

        # --- zone de saisie ---
        input_frame = tk.Frame(self, bg=c["bg"])
        input_frame.pack(fill="x", side="bottom")

        self.prompt_label = tk.Label(
            input_frame, text="", bg=c["bg"], fg=c["prompt"], font=app.text_font,
        )
        self.prompt_label.pack(side="left", padx=(10, 0), pady=6)

        self.entry = tk.Entry(
            input_frame, bg=c["input_bg"], fg=c["fg"], insertbackground=c["fg"],
            font=app.text_font, relief="flat",
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=8, pady=6)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.bind("<Up>", self.history_up)
        self.entry.bind("<Down>", self.history_down)
        self.entry.bind("<Tab>", self.on_tab_complete)
        self.entry.bind("<Control-l>", self.on_ctrl_l)
        self.entry.bind("<Control-w>", lambda e: (self.app.close_session(self), "break")[-1])
        self.entry.focus_set()

        self.show_banner()
        self.update_prompt()
        self.after(100, self.poll_queue)

    # ---------- affichage ----------
    def show_banner(self):
        self.print_line(self.app.config["banner"], tag="dim")
        if not self.bash_path:
            self.print_line(
                "Git Bash non détecté automatiquement. Installe-le "
                "(https://git-scm.com/downloads) ou modifie GIT_BASH_CANDIDATES / "
                "config.json si le chemin est différent.",
                tag="error",
            )
        self.print_line(
            "Astuce : les commandes interactives (nano, vim, less, ssh, top, ...) "
            "s'ouvrent dans une fenêtre console séparée. Tab = autocomplétion. "
            "Ctrl+L = effacer l'écran. Ctrl+W ou ✕ = fermer l'onglet. "
            "Onglet '+' = nouvelle session.",
            tag="info",
        )

    def print_line(self, text, tag=None):
        self.output.configure(state="normal")
        if tag:
            self.output.insert("end", text + "\n", tag)
        else:
            self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def update_prompt(self):
        tag = "cmd" if self.shell_mode == "cmd" else "bash"
        self.prompt_label.config(text=f"[{tag}] {self.cwd}>")

    def set_shell(self, mode):
        c = self.app.colors
        if mode == "bash" and not self.bash_path:
            self.print_line("Impossible de basculer : Git Bash introuvable.", tag="error")
            return
        self.shell_mode = mode
        if mode == "cmd":
            self.cmd_btn.configure(bg=c["button_active_bg"], fg=c["fg"])
            self.bash_btn.configure(bg=c["button_bg"], fg=c["fg_dim"])
        else:
            self.bash_btn.configure(bg=c["button_active_bg"], fg=c["fg"])
            self.cmd_btn.configure(bg=c["button_bg"], fg=c["fg_dim"])
        self.update_prompt()

    # ---------- saisie / historique ----------
    def on_ctrl_l(self, event=None):
        self.clear_screen()
        return "break"

    def clear_screen(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
        self.show_banner()

    def history_up(self, event=None):
        if not self.history:
            return
        self.history_index = max(0, self.history_index - 1)
        self.entry.delete(0, "end")
        self.entry.insert(0, self.history[self.history_index])

    def history_down(self, event=None):
        if not self.history:
            return
        self.history_index = min(len(self.history), self.history_index + 1)
        self.entry.delete(0, "end")
        if self.history_index < len(self.history):
            self.entry.insert(0, self.history[self.history_index])

    # ---------- autocomplétion ----------
    def on_tab_complete(self, event=None):
        text = self.entry.get()
        cursor = self.entry.index(tk.INSERT)
        before = text[:cursor]
        after = text[cursor:]

        space_idx = before.rfind(" ")
        token = before[space_idx + 1:]
        is_first_token = " " not in before.strip() and space_idx == -1

        if is_first_token:
            candidates = sorted(set(self.app.config["known_commands"]))
            matches = [c for c in candidates if c.startswith(token.lower())]
        else:
            matches = self._path_matches(token)

        if not matches:
            return "break"
        if len(matches) == 1:
            new_token = matches[0]
            new_before = before[:space_idx + 1] + new_token
            self.entry.delete(0, "end")
            self.entry.insert(0, new_before + after)
            self.entry.icursor(len(new_before))
        else:
            self.print_line("  ".join(matches), tag="dim")
        return "break"

    def _path_matches(self, token):
        token = token.strip('"')
        dirpart, partial = os.path.split(token)
        search_dir = os.path.join(self.cwd, dirpart) if dirpart else self.cwd
        try:
            entries = os.listdir(search_dir)
        except Exception:
            return []
        matches = []
        for entry in entries:
            if entry.lower().startswith(partial.lower()):
                full = os.path.join(dirpart, entry) if dirpart else entry
                if os.path.isdir(os.path.join(search_dir, entry)):
                    full += os.sep
                matches.append(full)
        return sorted(matches)

    # ---------- exécution ----------
    def on_enter(self, event=None):
        cmd = self.entry.get().strip()
        self.entry.delete(0, "end")
        if not cmd:
            return
        self.history.append(cmd)
        self.history_index = len(self.history)

        tag = "cmd" if self.shell_mode == "cmd" else "bash"
        self.print_line(f"[{tag}] {self.cwd}> {cmd}", tag="prompt")

        low = cmd.lower()
        if low in ("exit", "quit"):
            self.app.close_session(self)
            return
        if low in ("clear", "cls"):
            self.clear_screen()
            return
        if low == "help":
            self.print_line(
                "Commandes internes: clear/cls, exit, help, cd <chemin>.\n"
                "!cmd  -> bascule sur cmd.exe   |   !bash -> bascule sur Git Bash\n"
                "Tab = autocomplétion commandes/chemins   |   Ctrl+L = clear\n"
                "Bouton ■ Stop = interrompt la commande en cours\n"
                "Bouton 💾 Save = exporte cette session dans logs/\n"
                "Bouton ✕ Fermer l'onglet, ou Ctrl+W = ferme l'onglet actif\n"
                "Onglet '+' = nouvelle session de terminal indépendante\n"
                "Commandes interactives (nano, vim, less, ssh, top, git log, ...) "
                "-> ouvertes dans une fenêtre console dédiée.",
                tag="dim",
            )
            return
        if low == "!cmd":
            self.set_shell("cmd")
            return
        if low == "!bash":
            self.set_shell("bash")
            return
        if low.startswith("cd "):
            target = cmd[3:].strip().strip('"')
            new_dir = os.path.normpath(os.path.join(self.cwd, target))
            if os.path.isdir(new_dir):
                self.cwd = new_dir
                self.update_prompt()
            else:
                self.print_line(f"Dossier introuvable : {new_dir}", tag="error")
            return

        if self.app.is_interactive(cmd):
            self.launch_interactive(cmd)
            return

        threading.Thread(target=self.run_command, args=(cmd,), daemon=True).start()

    def _build_env(self):
        env = os.environ.copy()
        env.update(self.app.config.get("env", {}))
        return env

    def launch_interactive(self, cmd):
        self.print_line(
            "Commande interactive : ouverture dans une fenêtre console séparée...",
            tag="info",
        )
        try:
            env = self._build_env()
            if self.shell_mode == "bash" and self.bash_path:
                full_cmd = f'{cmd}; echo; read -n1 -p "[Appuie sur une touche pour fermer]"'
                args = [self.bash_path, "-c", full_cmd]
            else:
                full_cmd = f'{cmd} & pause'
                args = ["cmd.exe", "/k", full_cmd]

            subprocess.Popen(
                args, cwd=self.cwd, env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        except Exception as exc:
            self.print_line(f"Impossible d'ouvrir la fenêtre console : {exc}", tag="error")

    def run_command(self, cmd):
        try:
            env = self._build_env()
            if self.shell_mode == "bash" and self.bash_path:
                args = [self.bash_path, "-c", cmd]
                shell = False
            else:
                args = cmd
                shell = True

            proc = subprocess.Popen(
                args, shell=shell, cwd=self.cwd, env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            self.current_proc = proc
            self.cmd_start_time = time.time()
            self.last_output_time = time.time()
            self.stuck_warned = False

            t_out = threading.Thread(target=self._stream_reader, args=(proc.stdout, "stdout"), daemon=True)
            t_err = threading.Thread(target=self._stream_reader, args=(proc.stderr, "stderr"), daemon=True)
            t_out.start()
            t_err.start()
            proc.wait()
            t_out.join()
            t_err.join()
        except FileNotFoundError:
            self.result_queue.put(("stderr", "Commande introuvable.\n"))
        except Exception as exc:
            self.result_queue.put(("stderr", f"{exc}\n"))
        finally:
            self.current_proc = None
            self.cmd_start_time = None

    def _stream_reader(self, pipe, kind):
        try:
            for line in iter(pipe.readline, ""):
                if line == "":
                    break
                self.result_queue.put((kind, line))
                self.last_output_time = time.time()
        except Exception:
            pass
        finally:
            try:
                pipe.close()
            except Exception:
                pass

    def stop_current(self):
        if self.current_proc and self.current_proc.poll() is None:
            try:
                self.current_proc.terminate()
                self.print_line("Commande interrompue (Stop).", tag="error")
            except Exception as exc:
                self.print_line(f"Impossible d'arrêter le process : {exc}", tag="error")
        else:
            self.print_line("Aucune commande en cours dans cet onglet.", tag="dim")

    def save_log(self):
        logs_dir = os.path.join(base_path(), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(logs_dir, f"session_{self.session_num}_{stamp}.txt")
        try:
            content = self.output.get("1.0", "end")
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(content)
            self.print_line(f"Session sauvegardée : {filepath}", tag="info")
        except Exception as exc:
            self.print_line(f"Échec de la sauvegarde : {exc}", tag="error")

    def poll_queue(self):
        try:
            while True:
                kind, payload = self.result_queue.get_nowait()
                if payload:
                    self.print_line(payload.rstrip("\n"), tag=kind if kind in ("stdout", "stderr") else None)
        except queue.Empty:
            pass

        # détection heuristique de commande "bloquée"
        if (
            self.current_proc is not None
            and self.cmd_start_time is not None
            and not self.stuck_warned
        ):
            elapsed_since_output = time.time() - (self.last_output_time or self.cmd_start_time)
            threshold = self.app.config.get("stuck_warning_seconds", 4)
            if elapsed_since_output > threshold:
                self.print_line(
                    "Cette commande ne répond pas depuis quelques secondes : elle "
                    "attend peut-être une entrée interactive. Clique sur ■ Stop puis "
                    "relance-la (les commandes connues comme interactives s'ouvrent "
                    "automatiquement dans une fenêtre dédiée).",
                    tag="info",
                )
                self.stuck_warned = True

        self.after(100, self.poll_queue)


class SkeyesTerminalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config_data = load_config()
        self.colors = self.config_data["colors"]
        self.bash_path = find_git_bash()

        self.title(APP_TITLE)
        self.configure(bg=self.colors["bg"])
        self.geometry("1050x680")
        self.minsize(650, 420)

        try:
            icon_path = os.path.join(base_path(), "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

        family = pick_font_family(self.config_data["font_family"])
        self.text_font = tkfont.Font(family=family, size=self.config_data["font_size"])

        # --- style sombre pour les onglets ---
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(
            "TNotebook", background=self.colors["bg"], borderwidth=0,
        )
        style.configure(
            "TNotebook.Tab", background=self.colors["button_bg"],
            foreground=self.colors["fg_dim"], padding=(12, 6),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.colors["button_active_bg"])],
            foreground=[("selected", self.colors["fg"])],
        )

        top_bar = tk.Frame(self, bg=self.colors["bg"])
        top_bar.pack(fill="x", side="top")
        tk.Button(
            top_bar, text="+ Onglet", command=self.add_session,
            bg=self.colors["button_bg"], fg=self.colors["fg"],
            activebackground=self.colors["button_active_bg"],
            activeforeground=self.colors["fg"], relief="flat",
            font=self.text_font, padx=10, pady=3,
        ).pack(side="left", padx=8, pady=4)

        self.notebook = ttk.Notebook(self, style="TNotebook")
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Ctrl+W ferme l'onglet actif depuis n'importe où dans la fenêtre
        self.bind_all("<Control-w>", lambda e: self.close_session(self._current_session()))

        self.sessions = {}
        self._session_counter = 0
        self.add_session()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _current_session(self):
        try:
            widget_name = self.notebook.select()
            return self.nametowidget(widget_name) if widget_name else None
        except Exception:
            return None

    def on_tab_changed(self, event=None):
        # Corrige le bug "impossible d'écrire" : le champ de saisie doit
        # recevoir le focus explicitement à chaque fois qu'un onglet
        # devient visible (créé OU sélectionné par clic).
        session = self._current_session()
        if session is not None:
            session.entry.focus_set()

    def is_interactive(self, cmd):
        first_word = cmd.strip().split(" ")[0].lower()
        first_word = os.path.basename(first_word)
        if first_word.endswith(".exe"):
            first_word = first_word[:-4]
        return first_word in set(self.config_data["interactive_commands"])

    @property
    def config(self):
        return self.config_data

    def add_session(self):
        self._session_counter += 1
        session = TerminalSession(self.notebook, self, self._session_counter)
        label = f"Terminal {self._session_counter}"
        self.notebook.add(session, text=label)
        self.notebook.select(session)
        self.sessions[session] = label
        return session

    def close_session(self, session):
        if len(self.sessions) <= 1:
            self.on_close()
            return
        self.notebook.forget(session)
        self.sessions.pop(session, None)

    def on_close(self):
        for session in list(self.sessions.keys()):
            if session.current_proc and session.current_proc.poll() is None:
                try:
                    session.current_proc.terminate()
                except Exception:
                    pass
        self.destroy()


if __name__ == "__main__":
    app = SkeyesTerminalApp()
    app.mainloop()
