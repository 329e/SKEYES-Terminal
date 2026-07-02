# SKEYES Terminal

**SKEYES Terminal** est une application Windows autonome (`.exe`) qui
est elle-même un terminal de commande : une fenêtre graphique noire
au thème vert néon (assortie au logo SKEYES), dans laquelle tu tapes
des commandes système comme dans `cmd.exe` ou Git Bash, avec en plus
des onglets multiples, de l'autocomplétion, un système de sauvegarde
de session et une configuration entièrement personnalisable.

Pas besoin d'installer quoi que ce soit sur la machine cible : une
fois compilé, `SKEYES_Terminal.exe` fonctionne seul.

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Commandes et raccourcis](#commandes-et-raccourcis)
- [Personnalisation (config.json)](#personnalisation-configjson)
- [Structure du projet](#structure-du-projet)
- [Dépannage](#dépannage)

---

## Fonctionnalités

### Terminal complet
- Exécute n'importe quelle commande système, comme un vrai terminal.
- **Deux shells au choix**, avec bascule à la volée : `cmd.exe`
  (Windows) ou **Git Bash**.
- Le répertoire de travail est conservé entre les commandes (`cd`
  fonctionne comme attendu).

### Onglets multiples
- Ouvre plusieurs sessions de terminal indépendantes dans la même
  fenêtre (bouton `+ Onglet`), chacune avec son propre répertoire,
  son shell et son historique.
- Ferme un onglet avec le bouton **✕** ou `Ctrl+W`.

### Sortie en temps réel
- Les commandes affichent leur résultat **au fur et à mesure**
  (streaming), pas seulement une fois terminées — utile pour les
  commandes longues.
- `stdout` (sortie normale) et `stderr` (erreurs) sont affichés dans
  des **couleurs différentes**.
- Bouton **■ Stop** pour interrompre une commande en cours.

### Commandes interactives gérées proprement
- Les programmes plein écran comme `nano`, `vim`, `less`, `top`,
  `ssh`, `git log`, `python`, etc. ont besoin d'un vrai terminal (TTY)
  pour fonctionner. SKEYES Terminal les détecte automatiquement et les
  ouvre dans une **vraie fenêtre console séparée**, où ils s'exécutent
  normalement.
- Si une commande normale reste silencieuse plus de quelques secondes,
  un message d'info te prévient qu'elle attend peut-être une saisie.

### Confort d'utilisation
- **Autocomplétion** (`Tab`) des commandes et des chemins de fichiers.
- Historique des commandes navigable (flèches Haut/Bas).
- `Ctrl+L` efface l'écran (comme `clear`), tout en gardant la bannière
  et les infos affichées.
- Bouton **💾 Save** : exporte le contenu de l'onglet actif dans un
  fichier `.txt` horodaté (dossier `logs/`).

### Personnalisable sans recompiler
- Couleurs, police, bannière ASCII, variables d'environnement et
  listes de commandes pilotées par un fichier `config.json` externe,
  modifiable librement.

---

## Installation

### Prérequis (sur la machine où tu compiles)
- **Windows**
- **Python 3.9 ou supérieur**, avec `pip` disponible dans le `PATH`
- (Recommandé) **Git Bash** installé, pour profiter du shell bash
  intégré : https://git-scm.com/downloads

### Étapes

1. **Copie tout le dossier du projet** sur ta machine Windows.

2. **Lance la compilation automatique** : double-clique sur
   `build\build.bat`.
   Ce script va :
   - installer `PyInstaller` si besoin,
   - compiler l'application en un seul fichier `.exe`,
   - lui appliquer l'icône SKEYES,
   - copier `config.json` et `icon.ico` à côté de l'exe,
   - créer le dossier `logs/`.

   Résultat : `dist\SKEYES_Terminal.exe` (+ `config.json`, `icon.ico`,
   `logs\`).

3. **(Optionnel) Crée un raccourci Bureau** : double-clique sur
   `build\create_shortcut.bat`. Il ajoute un raccourci avec l'icône
   SKEYES sur ton Bureau.

4. **(Optionnel) Signe l'exécutable** si tu as un certificat de
   signature de code : `build\sign.bat "certificat.pfx" "motdepasse"`.
   Cela évite l'avertissement Windows SmartScreen à la première
   ouverture. Sans certificat, tu peux ignorer cette étape — il suffit
   de cliquer "Informations complémentaires" → "Exécuter quand même"
   la première fois.

Une fois ces étapes faites, **tu peux copier le dossier `dist\`
(exe + config.json + icon.ico + logs\) sur n'importe quelle autre
machine Windows** : plus besoin de Python ni de recompiler.

---

## Utilisation

Double-clique sur `SKEYES_Terminal.exe` (ou ton raccourci Bureau).

La fenêtre s'ouvre avec la bannière SKEYES et un premier onglet
"Terminal 1". Tape une commande dans le champ du bas et appuie sur
Entrée :

```
[cmd] C:\Users\toi> dir
[cmd] C:\Users\toi> cd Documents
[cmd] C:\Users\toi\Documents> git status
```

- Utilise les boutons **CMD** / **Git Bash** en haut pour choisir quel
  shell exécute tes commandes (ou tape `!cmd` / `!bash`).
- Ouvre un nouvel onglet avec **+ Onglet** pour une session parallèle.
- Ferme un onglet avec **✕** ou `Ctrl+W`.
- Une commande comme `nano fichier.txt` ouvrira automatiquement une
  fenêtre console dédiée, car `nano` a besoin d'un vrai terminal.

---

## Commandes et raccourcis

| Commande / Raccourci | Effet |
|-----------------------|--------------------------------------------|
| `help`                | Affiche l'aide dans le terminal            |
| `clear` / `cls`       | Efface l'écran (réaffiche la bannière)     |
| `cd <chemin>`         | Change le répertoire courant               |
| `!cmd`                | Bascule l'exécution sur `cmd.exe`          |
| `!bash`               | Bascule l'exécution sur Git Bash           |
| `exit` / `quit`       | Ferme l'onglet actif (ou l'appli si dernier)|
| `Tab`                 | Autocomplétion commande / chemin           |
| `Ctrl+L`               | Efface l'écran                             |
| `Ctrl+W`               | Ferme l'onglet actif                       |
| Flèches Haut / Bas     | Navigue dans l'historique des commandes    |
| Bouton **+ Onglet**    | Ouvre une nouvelle session de terminal     |
| Bouton **■ Stop**      | Interrompt la commande en cours            |
| Bouton **💾 Save**      | Exporte la session dans `logs/`           |

---

## Personnalisation (config.json)

Le fichier `config.json` (à côté de l'exe) contrôle l'apparence et le
comportement de l'application, sans recompiler :

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
  "banner": "Ton propre texte / logo ASCII ici",
  "env": {
    "MA_VARIABLE": "valeur"
  },
  "interactive_commands": ["nano", "vim", "ssh", "..."],
  "known_commands": ["dir", "cd", "git", "..."],
  "stuck_warning_seconds": 4
}
```

- **colors** : toutes les couleurs de l'interface.
- **font_family / font_size** : police utilisée (première trouvée sur
  le système parmi la liste).
- **banner** : le texte affiché à l'ouverture et après un `clear`.
- **env** : variables d'environnement injectées dans toutes les
  commandes exécutées.
- **interactive_commands** : commandes ouvertes dans une fenêtre
  console séparée.
- **known_commands** : commandes proposées par l'autocomplétion `Tab`.
- **stuck_warning_seconds** : délai avant l'avertissement "commande
  bloquée".

Seules les clés que tu veux changer ont besoin d'être présentes dans
le fichier ; les valeurs par défaut couvrent le reste.

---

## Structure du projet

```
SKEYES_Terminal/
├── app/
│   ├── terminal_app.py      <- Code source de l'application
│   ├── config.json           <- Configuration (couleurs, env, ...)
│   ├── icon.ico               <- Icône SKEYES
│   └── logo_source.png        <- Logo d'origine
├── build/
│   ├── build.bat              <- Compile l'exe automatiquement
│   ├── create_shortcut.bat    <- Crée un raccourci Bureau
│   └── sign.bat                <- Signature optionnelle de l'exe
├── logs/                       <- Sessions sauvegardées (bouton Save)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Dépannage

**"Standard input is not a terminal" ou affichage illisible**
→ Tu as tapé une commande interactive directement sans qu'elle soit
reconnue. Ajoute-la à `interactive_commands` dans `config.json`.

**Windows SmartScreen bloque l'exe**
→ Normal pour un exécutable non signé. Clique "Informations
complémentaires" → "Exécuter quand même", ou signe l'exe avec
`build\sign.bat` si tu as un certificat.

**Git Bash non détecté**
→ Installe Git pour Windows (https://git-scm.com/downloads), ou
vérifie que `bash.exe` est dans le `PATH`, ou ajoute son chemin exact
dans `GIT_BASH_CANDIDATES` (`app/terminal_app.py`).

**Impossible d'écrire dans le terminal**
→ Clique une fois dans le champ de saisie en bas de la fenêtre pour
lui redonner le focus.

**Une commande semble figée**
→ Regarde si un message "commande ne répond pas" apparaît ; clique
**■ Stop** puis relance-la (les commandes interactives connues
s'ouvrent automatiquement dans une fenêtre dédiée).
