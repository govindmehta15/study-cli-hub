# 🧠 CLI Study Hub — Open Source Study Notes CLI

Welcome to **CLI Study Hub**, an open-source command-line based study companion for learners, students, and contributors.  
It allows you to **read, create, edit, and contribute** study notes for different subjects — all from your terminal.

> 📚 The goal: To build a **community-driven digital notebook** that works right inside your CLI — lightweight, fast, and accessible for everyone.

---

## 🚀 Features

✅ **Cross-platform** — works on Windows, macOS, and Linux  
✅ **Interactive reading** — smooth scrolling, arrow-key navigation, highlights  
✅ **Add new subjects** — with a short description  
✅ **Add new notes** — directly from the CLI  
✅ **Edit notes with reason tracking** — so contributors can explain updates  
✅ **Simple navigation** — serial-number access, easy “back” commands  
✅ **Open-source collaboration** — clone, study, contribute, and share  
✅ **Git-friendly** — all text-based content, easy to sync and version control  

---

## 💡 How to Use

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/cli-study-hub.git
cd cli-study-hub
````

### 2️⃣ Run the CLI App

```bash
python study.py
```

> 💡 If you’re on **Windows**, and it asks for `windows-curses`, it will install it automatically the first time you run.

---

## 🧭 CLI Commands & Workflow

### 🏠 Main Menu

* `1, 2, 3...` → Open subject by number
* `a` → Add new subject
* `0` → Exit

### 📘 Inside Subject

* `1, 2, 3...` → Open a note file
* `a` → Add new note
* `b` → Go back to subjects

### 📖 Reading Mode

* `↑` / `↓` → Scroll through file
* `SPACE + ↑/↓` → Highlight lines
* `q` → Quit reading mode

### ✏️ Editing

* Choose “Edit file”
* Enter **edit reason**
* File opens in your default editor (`nano` / `notepad`)
* Save and close → Your change is recorded with reason

---

## 🌱 Adding New Content

### ➕ Add a New Subject

When you select `a` from the main menu:

1. Enter subject name
2. Add a **short description**
3. A new folder and `description_subject.txt` file will be created

### ➕ Add a New Note

Inside any subject:

1. Select `a` to add a note
2. Enter note filename (e.g., `chapter1` → creates `chapter1.txt`)
3. Add brief starting content (optional)
4. Start editing directly

---

## 🧩 Folder Structure

```
cli-study-hub/
│
├── study.py                  # Main CLI script
├── subjects/                 # All subjects stored here
│   ├── Physics/
│   │   ├── description_Physics.txt
│   │   ├── chapter1.txt
│   │   └── chapter2.txt
│   ├── Maths/
│   │   ├── description_Maths.txt
│   │   └── integration.txt
│   └── ...
└── README.md
```

---

## 👥 Contribution Guide

We welcome contributions from everyone! 🎉

1. **Fork** the repository
2. **Clone** your fork
3. **Add new subjects or notes** through the CLI
4. **Commit** with a meaningful message
5. **Push** to your fork and open a **Pull Request**

> 🔍 Make sure your notes are clear, accurate, and follow a consistent format for others to understand.

---

## 🧾 Example Flow

```bash
$ python study.py
📚 Subjects Available:
1. Physics
2. Maths
a. Add new subject
0. Exit

Enter choice: 1
📖 Notes in 'Physics':
1. chapter1.txt
a. Add new note
b. Back to subjects
```

Then read, highlight, and enjoy learning directly from your terminal ✨

---

## 🌐 For Non-CLI Users

> 💬 Don’t want to use the CLI?

No problem!
You can still **browse all study notes directly on GitHub** inside the `/subjects` folder.
Each subject has its **description file** and **individual notes**, all in clean, readable `.txt` format.

Perfect for quick reading or sharing links — even on mobile 📱.

---

## 🧰 Requirements

* Python ≥ 3.7
* Git (for cloning)
* Terminal / Command Prompt access

*(Optional: `windows-curses` — auto-installed for Windows)*

---

## ❤️ About the Project

CLI Study Hub is an **open-source educational project** built to promote learning through collaboration.
It’s designed to let anyone:

* Create structured subject-wise notes
* Study efficiently from the terminal
* Contribute and learn together

> 🌍 Built for learners, by learners — one note at a time.

---

## 📧 Author & Community

**Created by:** [Govind Mehta](https://github.com/govindmehta15)
SOFTWARE DEVELOPER & Tech and Product Lead at ElectraWheeler
📍 India 🇮🇳

If you like this project, ⭐ **star it on GitHub** and share it with your study community!
Let’s make learning simpler, faster, and truly open-source. 🌱

```
