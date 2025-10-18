# 🧠 CLI Study Hub v4.0 — Complete Interactive Study Companion

Welcome to **CLI Study Hub v4.0**, a fully-featured, open-source **command-line study application** designed for learners, contributors, and technical users who prefer a terminal-first workflow.

> 📚 Goal: Build a **community-driven digital notebook** that works right in your terminal — lightweight, fast, and ultra-interactive with complete GitHub integration.

---

## 🚀 Complete Feature Set

### 📖 **Interactive Reading Experience**
✅ **Arrow-key navigation** — ↑/↓ scroll line by line  
✅ **Page navigation** — PgUp/PgDn jump multiple lines  
✅ **Spacebar highlighting** — mark important lines  
✅ **Search functionality** — find text within files  
✅ **Help system** — built-in help with 'h' key  

### 📁 **Universal File Management**
✅ **ALL file types supported** — Text, documents, images, archives, executables, media  
✅ **CLI-only viewing** — No system applications, everything opens in terminal  
✅ **Interactive file browser** — navigate and select files visually  
✅ **Smart file upload** — with duplicate handling for any file type  
✅ **File editing** — with reason tracking and backup system  
✅ **Hex dump viewer** — for binary files and unknown formats  
✅ **Error handling** — graceful handling of corrupted or unsupported files  

### 🏗️ **Organization & Structure**
✅ **User-specific folders** — personal notes separate from global subjects  
✅ **Subject management** — create subjects with descriptions  
✅ **Note creation** — create new notes directly in CLI  
✅ **Rich file display** — color-coded file types and sizes  

### 🔄 **GitHub Integration**
✅ **Git status checking** — shows uncommitted changes  
✅ **Sync prompts** — recommends git pull/push commands  
✅ **Repository awareness** — detects git repository status  
✅ **Collaboration ready** — designed for team study repositories  

### 🎨 **User Experience**
✅ **Cross-platform** — Windows, macOS, Linux  
✅ **Rich CLI interface** — tables, panels, color-coded output  
✅ **Error handling** — centralized exception management  
✅ **Command validation** — helpful error messages  
✅ **Clean navigation** — never get lost with 'back' commands  

---

## 💡 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/govindmehta15/cli-study-hub.git
cd cli-study-hub
````

### 2️⃣ Install Dependencies

**Option A: Automatic Installation (Recommended)**
```bash
python3 install.py
```

**Option B: Using requirements.txt**
```bash
pip install -r requirements.txt
```

**Option C: Manual Installation**
```bash
pip install rich PyPDF2 python-docx getch lxml
```

> 💡 **Dependencies**: `rich` → beautiful CLI, `PyPDF2` → PDF preview, `python-docx` → DOCX preview, `getch` → cross-platform key input, `lxml` → XML processing for Word docs.

### 3️⃣ Run the CLI App

**Option A: Smart Startup (Recommended)**
```bash
python3 start.py
```

**Option B: Direct Start**
```bash
python3 study.py
```

> 🎯 **Smart Features**: Auto-installs dependencies, auto-syncs with GitHub, auto-pushes changes on exit!

---

## 🧭 Complete CLI Commands & Workflow

### 🏠 **Main Menu Commands**
- `study <subject>` — Open subject (use number or name)
- `learn <subject>` — Open subject (use number or name)  
- `create subject` — Add new subject with description
- `list` — Refresh subjects list
- `switch user` — Switch between user folders or global mode
- `exit` — Exit CLI with GitHub sync reminder

### 📝 **Subject Menu Commands**
- `read <note>` — Open note in interactive reader
- `edit <note>` — Edit note with reason tracking
- `new note` — Create new note file
- `upload` — Upload file via interactive file browser
- `back` — Return to main menu

### 📖 **Interactive Reader Controls**
- `↑/↓` — Scroll line by line
- `PgUp/PgDn` — Jump multiple lines
- `SPACE` — Highlight/unhighlight current line
- `/` — Search for text in file
- `h` — Show help
- `q` — Quit reader

### 🔄 **Automatic GitHub Integration**
- **Auto-Pull**: Automatically pulls latest changes on startup
- **Auto-Push**: Automatically commits and pushes changes on exit
- **Signal Handling**: Gracefully saves changes even if interrupted (Ctrl+C)
- **Status Checking**: Shows repository status and uncommitted changes

### 🤖 **Full Automation**
- **Dependency Management**: Auto-installs missing packages on startup
- **Application Restart**: Automatically restarts after installing dependencies
- **Error Recovery**: Graceful handling of all errors and edge cases
- **Cross-Platform**: Works on Windows, macOS, and Linux

### 🏠 Main Menu

| Command          | Action                               |
| ---------------- | ------------------------------------ |
| `1, 2, 3...`     | Open subject by number               |
| `create subject` | Add new subject                      |
| `switch user`    | Switch to another user folder        |
| `exit` / `quit`  | Exit the app (Git sync prompt shown) |

---

### 📘 Inside Subject

| Command              | Action                                                   |
| -------------------- | -------------------------------------------------------- |
| `1, 2, 3...`         | Open a note by number                                    |
| `read <filename>`    | Read text-based file with arrow scrolling & highlighting |
| `view <filename>`    | Preview `.pdf`, `.docx`, or `.csv`                       |
| `analyze <filename>` | Preview `.csv` first rows                                |
| `upload`             | Upload a file from your computer                         |
| `back`               | Go back to subjects menu                                 |

---

### 📖 Reading Mode (Text Files Only)

* `↑` / `↓` → Scroll line by line
* `Page Up / Page Down` → Jump 10 lines
* `Space` → Highlight/unhighlight current visible lines
* `q` → Quit reading mode and return to notes menu

> Highlights remain active during session; useful for marking important lines while studying.

---

## 🌱 Adding New Content

### ➕ Add a New Subject

* Enter `create subject` in main menu
* Provide **subject name** and **short description**
* New folder + `description_<subject>.txt` file is created

### ➕ Add or Upload Notes

* Inside subject, use:

  * `read <filename>` → Create & edit inline text notes
  * `upload` → Upload files from local system (`txt`, `md`, `py`, `csv`, `pdf`, `docx`)
* CLI ensures **file exists, format is allowed**, and avoids overwriting

---

## 🧩 Folder Structure

```
cli-study-hub/
│
├── study.py                  # Main CLI script
├── file_viewer.py            # Scrollable viewer with arrow keys & highlighting
├── file_uploader.py          # File upload handler
├── error_handler.py          # Rich error logging
├── subjects/                 # All subjects stored here
│   ├── GlobalSubject/
│   │   ├── description_GlobalSubject.txt
│   │   ├── note1.txt
│   │   └── note2.pdf
│   └── username1/
│       ├── Physics/
│       │   ├── description_Physics.txt
│       │   └── chapter1.md
│       └── Maths/
└── README.md
```

---

## 👥 Contribution Guide

We welcome contributions from everyone! 🎉

1. **Fork** the repository
2. **Clone** your fork
3. **Add new subjects or notes** via CLI
4. **Commit** with meaningful messages
5. **Push** and open a **Pull Request**

> 🔍 Make notes clear, accurate, and consistent for others to study.

---

## 🌐 GitHub Sync Recommendations

* **Before starting:**

```bash
git pull --rebase
```

* **After finishing:**

```bash
git add .
git commit -m "Update notes"
git push
```

> Ensures no conflicts and keeps your notes updated.

---

## 🌐 For Non-CLI Users

* Browse all study notes directly on GitHub in `/subjects`
* Each subject has a description file and notes in **readable formats**
* Works on **desktop or mobile**

---

## 🧰 Requirements

* Python ≥ 3.7
* Git (for cloning & syncing)
* Terminal / Command Prompt
* Optional: `keyboard`, `PyPDF2`, `python-docx`

---

## ❤️ About the Project

CLI Study Hub is an **open-source educational project** designed for **technical learners**:

* Create structured subject-wise notes
* Study efficiently from the terminal
* Contribute and collaborate globally
* Multi-format support & interactive reading

> 🌍 Built for learners, by learners — one note at a time.

---

## 📧 Author & Community

**Created by:** [Govind Mehta](https://github.com/govindmehta)
📍 India 🇮🇳

⭐ Star on GitHub and share with your study community!
Help us make learning faster, interactive, and fully open-source.

```

---

this README is **fully updated for v3.2**, highlighting:

- Scrollable CLI text files  
- Multi-format support & upload  
- User folders + global subjects  
- GitHub sync guidance  
- Rich menus & commands  


```
