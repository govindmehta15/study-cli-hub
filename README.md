# 📘 Study CLI Hub

A **cross-platform Command Line Interface (CLI)** study tool made for learners, by learners.  
You can **read, add, and edit** study notes directly from your terminal — all notes are stored in **subject-wise folders** inside this open-source GitHub repository.

This project works seamlessly on **Windows**, **macOS**, and **Linux**.  
It’s a simple yet powerful way to **study, organize, and contribute notes** using nothing more than your terminal.

---

## 🚀 Quick Start Guide

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/govindmehta/study-cli-hub.git
cd study-cli-hub
````

### 2️⃣ Run the CLI Script

```bash
python study.py
```

If you get a permission error on Mac/Linux, make it executable first:

```bash
chmod +x study.py
```

Then run:

```bash
./study.py
```

---

## 🧠 How It Works

Once you run the script, the terminal opens the **main CLI menu**:

### 📚 Main Menu – All Subjects

```bash
📘 All Subjects:

[1] Physics
[2] Chemistry
[3] Maths

Commands:
 open <id>  → open subject folder
 add        → add new subject
 exit       → quit program
```

---

### 🗂 Inside a Subject Folder

After you open a subject (e.g., `open 1` for Physics):

```bash
📂 Subject: Physics

[1] laws_of_motion.txt
[2] gravitation.txt

Commands:
 read <id>  → read note file
 edit <id>  → edit file (with reason)
 add        → add new note
 back       → go back to subjects
```

---

## 🧩 CLI Commands Reference

| Command           | Description                             | Example  |
| ----------------- | --------------------------------------- | -------- |
| `open <id>`       | Open subject folder using serial number | `open 1` |
| `read <id>`       | Read a note file by number              | `read 2` |
| `edit <id>`       | Edit a note with reason (auto backup)   | `edit 1` |
| `add`             | Add new note (inside a subject)         | `add`    |
| `add` (main menu) | Create new subject (with description)   | `add`    |
| `back`            | Go back to previous menu                | `back`   |
| `exit`            | Exit the CLI application                | `exit`   |

---

## ✍️ Example Usage

### Step 1 — List Subjects

```
> python study.py
📘 All Subjects:
[1] LLM
[2] GenAI
[3] Statistics
```

### Step 2 — Open a Subject

```
> open 1
📂 Subject: LLM
[1] Intro.txt
[2] BasicofLLM.txt
```

### Step 3 — Read a Note

```
> read 2
📖 Physics/gravitation.txt
==========================
Gravitation is the force of attraction between two bodies having mass...
```

### Step 4 — Edit a Note

```
> edit 2
Editing: Physics/gravitation.txt
Enter new content:
>>> Added example of Newton’s Law of Gravitation
Enter reason for edit: Added example for clarity
✅ File updated successfully and backup saved.
```

### Step 5 — Add a New Note

```
> add
Enter note title: Work and Energy
Enter note content:
>>> Work is defined as the product of force and displacement...
✅ Note 'Work and Energy' added successfully!
```

### Step 6 — Go Back

```
> back
```

---

## 📂 Repository Structure

```
study-cli-hub/
├── study.py                ← main CLI script
├── subjects/
│   ├── Physics/
│   │   ├── laws_of_motion.txt
│   │   ├── gravitation.txt
│   ├── Chemistry/
│   │   ├── atomic_structure.txt
│   │   ├── chemical_bonding.txt
│   └── Maths/
│       ├── calculus.txt
│       ├── algebra.txt
└── README.md
```

---

## 🛠️ Requirements

* Python **3.7+**
* Works on **Windows, macOS, and Linux**
* No external dependencies (pure Python standard library)

---

## 💡 Features

✅ Cross-platform CLI interface
✅ Simple serial-number navigation
✅ Subject and topic organization
✅ Read-only or edit modes (with backup and reason)
✅ Add new subjects (with description)
✅ Easy note contributions via GitHub
✅ 100% open-source and beginner-friendly

---

## 🤝 Contributing

We welcome contributions!
Here’s how you can help:

1. **Fork** this repository
2. **Add or edit notes** using the CLI
3. **Commit** your changes

   ```bash
   git add .
   git commit -m "Added new topic: Ohm's Law under Physics"
   ```
4. **Push** to your fork

   ```bash
   git push origin main
   ```
5. Create a **Pull Request** to the main repo.

🪄 Your contribution will appear in the shared knowledge base for everyone!

---

## 🧭 Project Vision

> “Learning should be accessible, simple, and collaborative.”

The goal of **Study CLI Hub** is to create a **community-driven command-line study space**
where learners can store, share, and review academic content across subjects —
all within their terminal, all open-source, and all together.

---

## 📜 License

This project is licensed under the **MIT License** — free to use, modify, and share.

---

## 👨‍💻 Author

**Govind Mehta**
🚀 Developer & Technical Lead, Electra Wheeler
📍 India
🌐 GitHub: https://github.com/govindmehta15

---

# study-cli-hub
