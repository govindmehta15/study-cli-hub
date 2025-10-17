#!/usr/bin/env python3
# ==========================================================
# Study CLI Hub
# A simple open-source CLI to read and manage study notes.
# Works on Windows, macOS, and Linux.
# Author: Govind Mehta
# ==========================================================

import os
import platform
import shutil
from datetime import datetime

BASE_DIR = os.path.join(os.path.dirname(__file__), "subjects")

# ----------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------

def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

def pause():
    input("\nPress Enter to continue...")

def list_subjects():
    subjects = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
    subjects.sort()
    return subjects

def list_files(subject):
    folder_path = os.path.join(BASE_DIR, subject)
    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    files.sort()
    return files

def read_file(subject, file_name):
    file_path = os.path.join(BASE_DIR, subject, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content

def edit_file(subject, file_name):
    file_path = os.path.join(BASE_DIR, subject, file_name)
    clear_screen()
    print(f"Editing: {subject}/{file_name}\n{'='*40}\n")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    print(content)
    print("\nEnter new content below (leave blank to cancel):")
    new_content = input("\n>>> ")

    if new_content.strip():
        reason = input("Enter reason for edit: ")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        backup_path = file_path + ".bak"
        shutil.copy(file_path, backup_path)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n# Edit ({timestamp})\nReason: {reason}\n{new_content}\n")
        print("\n✅ File updated successfully and backup saved.")
    else:
        print("\n❌ Edit cancelled.")
    pause()

def add_subject():
    clear_screen()
    subject_name = input("Enter new subject name: ").strip()
    description = input("Enter short subject description: ").strip()
    if not subject_name:
        print("❌ Subject name is required.")
        pause()
        return
    subject_path = os.path.join(BASE_DIR, subject_name)
    if not os.path.exists(subject_path):
        os.makedirs(subject_path)
        desc_file = os.path.join(subject_path, "description.txt")
        with open(desc_file, "w", encoding="utf-8") as f:
            f.write(f"Subject: {subject_name}\nDescription: {description}\nCreated: {datetime.now()}")
        print(f"\n✅ Subject '{subject_name}' created successfully!")
    else:
        print("\n⚠️ Subject already exists.")
    pause()

def add_note(subject):
    clear_screen()
    print(f"Add new note under: {subject}")
    title = input("Enter note title (file name): ").strip()
    if not title:
        print("❌ Title is required.")
        pause()
        return
    content = input("Enter note content:\n\n>>> ")
    if not content.strip():
        print("❌ Content cannot be empty.")
        pause()
        return
    file_name = title.replace(" ", "_").lower() + ".txt"
    file_path = os.path.join(BASE_DIR, subject, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{content}\n")
    print(f"\n✅ Note '{title}' added successfully!")
    pause()

# ----------------------------------------------------------
# CLI Navigation
# ----------------------------------------------------------

def subject_menu():
    while True:
        clear_screen()
        subjects = list_subjects()
        print("📘 All Subjects:\n")
        for i, s in enumerate(subjects, start=1):
            print(f"[{i}] {s}")
        print("\nCommands:")
        print(" open <id>  → open subject folder")
        print(" add        → add new subject")
        print(" exit       → quit program")

        cmd = input("\n> ").strip().split()

        if not cmd:
            continue

        if cmd[0] == "open":
            if len(cmd) < 2 or not cmd[1].isdigit() or int(cmd[1]) > len(subjects):
                print("❌ Invalid subject number.")
                pause()
                continue
            subject = subjects[int(cmd[1]) - 1]
            topic_menu(subject)

        elif cmd[0] == "add":
            add_subject()

        elif cmd[0] == "exit":
            clear_screen()
            print("👋 Exiting Study CLI Hub. Keep Learning!")
            break

        else:
            print("❌ Unknown command.")
            pause()

def topic_menu(subject):
    while True:
        clear_screen()
        files = list_files(subject)
        print(f"📂 Subject: {subject}\n")
        for i, f in enumerate(files, start=1):
            print(f"[{i}] {f}")
        print("\nCommands:")
        print(" read <id>  → read note file")
        print(" edit <id>  → edit file (with reason)")
        print(" add        → add new note")
        print(" back       → go back to subjects")

        cmd = input("\n> ").strip().split()
        if not cmd:
            continue

        if cmd[0] == "read":
            if len(cmd) < 2 or not cmd[1].isdigit() or int(cmd[1]) > len(files):
                print("❌ Invalid file number.")
                pause()
                continue
            file_name = files[int(cmd[1]) - 1]
            clear_screen()
            print(f"📖 {subject}/{file_name}\n{'='*40}\n")
            print(read_file(subject, file_name))
            pause()

        elif cmd[0] == "edit":
            if len(cmd) < 2 or not cmd[1].isdigit() or int(cmd[1]) > len(files):
                print("❌ Invalid file number.")
                pause()
                continue
            file_name = files[int(cmd[1]) - 1]
            edit_file(subject, file_name)

        elif cmd[0] == "add":
            add_note(subject)

        elif cmd[0] == "back":
            return

        else:
            print("❌ Unknown command.")
            pause()

# ----------------------------------------------------------
# Entry Point
# ----------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    subject_menu()
