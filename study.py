#!/usr/bin/env python3
import os
import platform
import subprocess
import time
from datetime import datetime

# ==============================
#   CONFIGURATION
# ==============================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SUBJECTS_DIR = os.path.join(ROOT_DIR, "subjects")
USERS_DIR = os.path.join(ROOT_DIR, "users")


# ==============================
#   UTILITY FUNCTIONS
# ==============================
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPress ENTER to continue...")


def ensure_dirs():
    os.makedirs(SUBJECTS_DIR, exist_ok=True)
    os.makedirs(USERS_DIR, exist_ok=True)


def print_header(title):
    clear_screen()
    print("=" * 60)
    print(f"📚  {title}")
    print("=" * 60)


def list_folders(path):
    if not os.path.exists(path):
        os.makedirs(path)
    items = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    return items


def list_files(path):
    if not os.path.exists(path):
        os.makedirs(path)
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files


# ==============================
#   GIT COMMAND UTILITIES
# ==============================
def run_git_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError:
        print("⚠️  Git command failed. Check your connection or setup.")


def git_pull():
    print("🔄 Syncing latest changes from GitHub...")
    run_git_command("git pull origin main")


def git_push():
    print("📤 Pushing your changes to GitHub...")
    run_git_command('git add .')
    msg = input("📝 Commit message: ").strip()
    if not msg:
        msg = f"Updated study notes on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    run_git_command(f'git commit -m "{msg}"')
    run_git_command("git push origin main")


# ==============================
#   FILE OPERATIONS
# ==============================
def read_file(path):
    print_header(f"Reading: {os.path.basename(path)}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        index = 0
        while True:
            clear_screen()
            print(f"📖 {os.path.basename(path)}")
            print("-" * 60)
            for i in range(index, min(index + 20, len(lines))):
                print(lines[i].rstrip())
            print("-" * 60)
            print("↑/↓ to scroll | SPACE+↑/↓ highlight | q to quit")
            key = input("Command: ").strip().lower()
            if key == "q":
                break
            elif key == "up" or key == "u":
                index = max(0, index - 20)
            elif key == "down" or key == "d":
                index = min(len(lines) - 1, index + 20)
    except Exception as e:
        print(f"⚠️ Error reading file: {e}")
    pause()


def edit_file(path):
    editor = "notepad" if platform.system() == "Windows" else os.getenv("EDITOR", "nano")
    print(f"✏️  Opening editor ({editor})...")
    time.sleep(1)
    os.system(f"{editor} {path}")
    print("✅ Changes saved.")
    pause()


# ==============================
#   NOTE & SUBJECT CREATION
# ==============================
def add_subject(path):
    subject_name = input("Enter new subject name: ").strip()
    if not subject_name:
        print("❌ Invalid name.")
        return
    new_dir = os.path.join(path, subject_name)
    os.makedirs(new_dir, exist_ok=True)
    desc_path = os.path.join(new_dir, f"description_{subject_name}.txt")
    desc = input("Add short description: ").strip()
    with open(desc_path, "w", encoding="utf-8") as f:
        f.write(desc)
    print(f"✅ Created subject: {subject_name}")
    pause()


def add_note(path):
    note_name = input("Enter note filename (without extension): ").strip()
    if not note_name:
        print("❌ Invalid name.")
        return
    note_path = os.path.join(path, f"{note_name}.txt")
    with open(note_path, "w", encoding="utf-8") as f:
        content = input("Add initial content (optional):\n")
        f.write(content)
    print(f"✅ Created note: {note_name}.txt")
    pause()


# ==============================
#   NAVIGATION
# ==============================
def explore_subjects(path):
    while True:
        print_header(f"Subjects in {path}")
        folders = list_folders(path)
        for i, folder in enumerate(folders, start=1):
            print(f"{i}. {folder}")
        print("\na. ➕ Add new subject")
        print("b. 🔙 Back")
        choice = input("\nEnter command (learn 1 / a / b): ").strip().lower()

        if choice.startswith("learn") or choice.startswith("study"):
            parts = choice.split()
            if len(parts) > 1 and parts[1].isdigit():
                idx = int(parts[1]) - 1
                if 0 <= idx < len(folders):
                    explore_notes(os.path.join(path, folders[idx]))
        elif choice in ["a", "add", "new subject"]:
            add_subject(path)
        elif choice in ["b", "back"]:
            break


def explore_notes(path):
    while True:
        print_header(f"Notes in {path}")
        files = list_files(path)
        for i, file in enumerate(files, start=1):
            print(f"{i}. {file}")
        print("\na. ➕ Add new note")
        print("b. 🔙 Back")
        choice = input("\nEnter command (read 1 / edit 2 / a / b): ").strip().lower()

        if choice.startswith("read"):
            parts = choice.split()
            if len(parts) > 1 and parts[1].isdigit():
                idx = int(parts[1]) - 1
                if 0 <= idx < len(files):
                    read_file(os.path.join(path, files[idx]))
        elif choice.startswith("edit"):
            parts = choice.split()
            if len(parts) > 1 and parts[1].isdigit():
                idx = int(parts[1]) - 1
                if 0 <= idx < len(files):
                    edit_file(os.path.join(path, files[idx]))
        elif choice in ["a", "add", "new note"]:
            add_note(path)
        elif choice in ["b", "back"]:
            break


def explore_users():
    while True:
        print_header("User Folders")
        users = list_folders(USERS_DIR)
        for i, u in enumerate(users, start=1):
            print(f"{i}. {u}")
        print("\na. ➕ Add new user")
        print("b. 🔙 Back")

        choice = input("\nEnter command (enter govind / a / b): ").strip().lower()

        if choice.startswith("enter"):
            parts = choice.split()
            if len(parts) > 1:
                uname = parts[1]
                upath = os.path.join(USERS_DIR, uname, "subjects")
                os.makedirs(upath, exist_ok=True)
                explore_subjects(upath)
        elif choice in ["a", "add", "new user"]:
            uname = input("Enter new username: ").strip()
            if uname:
                os.makedirs(os.path.join(USERS_DIR, uname, "subjects"), exist_ok=True)
                print(f"✅ Created user folder: {uname}")
                pause()
        elif choice in ["b", "back"]:
            break


# ==============================
#   MAIN PROGRAM
# ==============================
def main():
    ensure_dirs()
    clear_screen()
    print("🌍 Welcome to CLI Study Hub — v2.0")
    print("===========================================")
    print("⚙️  Checking for updates from GitHub...")
    git_pull()
    time.sleep(1)

    while True:
        print_header("Main Menu")
        print("1. 🌐 Explore Global Subjects")
        print("2. 👤 Explore User Folders")
        print("3. 🔄 Git Sync Commands")
        print("0. 🚪 Exit")

        cmd = input("\nEnter command (explore 1 / 2 / sync / exit): ").strip().lower()

        if cmd in ["1", "explore 1", "global"]:
            explore_subjects(SUBJECTS_DIR)
        elif cmd in ["2", "explore 2", "users"]:
            explore_users()
        elif cmd in ["3", "sync", "git"]:
            print("\n🔧 Git Commands:")
            print("1. Pull latest updates")
            print("2. Push your changes")
            print("b. Back")
            sub = input("\nSelect: ").strip()
            if sub == "1":
                git_pull()
            elif sub == "2":
                git_push()
        elif cmd in ["0", "exit", "quit"]:
            print("\n💾 Saving and syncing your updates...")
            git_push()
            print("👋 Thank you for using CLI Study Hub!")
            break
        else:
            print("❌ Invalid command.")
            pause()


if __name__ == "__main__":
    main()
