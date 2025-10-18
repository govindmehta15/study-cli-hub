# 🧠 CLI Study Hub — v2.0  
### _A community-driven command-line learning platform_

---

## 🚀 Overview

**CLI Study Hub v2** is an upgraded open-source **Command Line Interface (CLI)** application for learners, contributors, and developers who love minimal, distraction-free studying — right from their terminal.

In **Version 2**, you can:
- Create your **own user folder** to maintain private or personalized notes.
- Access **global subjects** shared by the community.
- Work in a **GitHub-synced environment**, with recommended manual sync commands.
- Enjoy a **more interactive CLI** experience using natural commands like `study physics`, `learn 1`, or `edit 2`.

> 🌍 “Built for learners, by learners — open, collaborative, and terminal-friendly.”

---

## ✨ What's New in v2.0

| Feature | Description |
|----------|-------------|
| 👤 **User-specific notes** | Create user folders with subjects and notes inside your username directory. |
| 🧭 **Interactive commands** | Use words like `study`, `read`, `learn`, `edit`, `open` instead of just numbers. |
| 🔄 **GitHub Sync Recommendations** | App suggests `git pull` at startup and `git push` when exiting for smooth sync. |
| 💬 **Enhanced CLI UX** | Clear layout, borders, emojis, color-coded highlights, and easy navigation. |
| 🧱 **Mixed structure** | Community-wide subjects exist at the root level; user-specific subjects live inside user folders. |
| 🛠️ **Smart subject handling** | Add, edit, or view notes dynamically with confirmations and activity logs. |

---

## 💡 Installation & Setup Guide

### 🪟 Windows
```bash
# Step 1: Clone repository
git clone https://github.com/govindmehta15/study-cli-hub.git
cd cli-study-hub

# Step 2: Install dependencies
pip install windows-curses

# Step 3: Run the app
python study.py
````

### 🍎 macOS / 🐧 Linux

```bash
# Step 1: Clone repository
git clone https://github.com/<your-username>/cli-study-hub.git
cd cli-study-hub

# Step 2: Run the app directly
python3 study.py
```

---

## 🧭 Usage Guide

### 🏁 Start the App

```bash
python study.py
```

### 🧍 Create or Choose User

* When you start, you’ll be asked:

  > “Enter your username (or press Enter to use Global Mode):”
* If you enter `govind`, it creates/loads `/subjects/govind/`
* You can still access public/global notes in `/subjects/`

---

## ⚙️ Core Commands

### 🏠 Main Menu

| Command           | Action                                  |
| ----------------- | --------------------------------------- |
| `study <subject>` | Opens a subject (e.g., `study Physics`) |
| `learn <number>`  | Opens subject by number                 |
| `create subject`  | Adds a new subject                      |
| `list`            | Shows all available subjects            |
| `switch user`     | Change to another user’s folder         |
| `exit`            | Exits the CLI app safely                |

---

### 📘 Inside a Subject

| Command       | Action                   |
| ------------- | ------------------------ |
| `read <note>` | Open a note file         |
| `new note`    | Add a new note           |
| `edit <note>` | Edit a note file         |
| `back`        | Go back to subjects list |

---

### 📖 Reading Mode

| Key           | Function                      |
| ------------- | ----------------------------- |
| `↑` / `↓`     | Scroll line by line           |
| `SPACE + ↑/↓` | Highlight text                |
| `q`           | Quit reading mode             |
| `r`           | Refresh view                  |
| `/`           | Search within file            |
| `h`           | Show help guide inside reader |

---

## 🌱 File & Folder Structure

```
cli-study-hub/
│
├── study.py                  # Main CLI script
├── subjects/                 # Contains all study materials
│   ├── global/               # Global open notes for all users
│   │   ├── Physics/
│   │   └── Maths/
│   ├── govind/               # User-specific folder
│   │   ├── Physics/
│   │   │   ├── description_Physics.txt
│   │   │   └── chapter1.txt
│   │   └── AI/
│   │       └── intro.txt
│   └── other_users/          # More user folders
└── README.md
```

---

## 🧩 GitHub Sync Recommendations

Since multiple contributors may edit the same notes, follow this safe **manual sync workflow**:

### 🕐 Before Starting

```bash
git pull
```

> This ensures you have the latest community updates.

### 🧠 While Working

You can freely add/edit subjects and notes using CLI commands.

### 🏁 Before Exiting

The app reminds you:

```bash
🔄 Tip: To sync your changes to GitHub:
git add .
git commit -m "Updated notes by <your-username>"
git push
```

> 🔐 Keep your personal notes in your own folder (e.g., `/subjects/govind/`) to avoid merge conflicts.

---

## 💬 Example CLI Session

```bash
$ python study.py
Welcome to CLI Study Hub 📘
Enter your username (press Enter for Global Mode): govind

✨ Hello, Govind! Your personal study folder is ready.

Available subjects:
1. Physics
2. AI
Type 'study Physics' or 'learn 1' to open.
> study Physics

📖 Notes in Physics:
1. chapter1.txt
2. waves.txt
Type 'read waves' or 'edit chapter1'
> read waves
```

---

## 🧰 Requirements

| Tool          | Version                        |
| ------------- | ------------------------------ |
| Python        | ≥ 3.7                          |
| Git           | Recommended for syncing        |
| Windows users | `windows-curses` auto-installs |

---

## 👥 Contribution Guide

We ❤️ contributions!

1. Fork the repository
2. Create your user folder (e.g., `/subjects/alex/`)
3. Add new notes or subjects
4. Commit your changes
5. Push and open a Pull Request

> ✏️ Use clear titles and commit messages like:
>
> ```
> Added 'AI Basics' notes under user Govind
> ```

---

## 🌐 For Non-CLI Users

Not a CLI fan? No worries!

You can:

* Browse all notes on GitHub → `/subjects/`
* Open `.txt` files directly in your browser
* Download subject folders for offline reading

Perfect for quick reference or mobile learning. 📱

---

## 🧾 Example Git Commands Summary

| Action              | Command                        |
| ------------------- | ------------------------------ |
| Pull latest updates | `git pull`                     |
| Stage all changes   | `git add .`                    |
| Commit changes      | `git commit -m "Your message"` |
| Push updates        | `git push`                     |

> ⚠️ *Note:* Always pull before you push to avoid conflicts.

---

## ❤️ About the Project

**CLI Study Hub v2** is an open-source educational initiative by **[Govind Mehta](https://github.com/govindmehta15)** 🇮🇳
It aims to make collaborative note-sharing **simple, lightweight, and community-powered** — accessible through any terminal.

> 🌱 “Empowering students to study, share, and grow — one note at a time.”

---

## ⭐ Support & Community

If you like this project:

* 🌟 Star it on GitHub
* 🧠 Contribute new subjects
* 💬 Share it with your learning groups

**Join the open-source learning movement today!**


