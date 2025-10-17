#!/usr/bin/env python3
# ==========================================================
# Study CLI Hub
# A simple open-source CLI to read and manage study notes.
# Works on Windows, macOS, and Linux.
# Author: Govind Mehta
# ==========================================================

import os
import sys
import platform
import subprocess
import curses

# ------------------------------------------------------------------
# Setup helper for Windows (install curses if needed)
# ------------------------------------------------------------------
if platform.system() == "Windows":
    try:
        import curses
    except ImportError:
        print("Installing windows-curses...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "windows-curses"])
        import curses

# ------------------------------------------------------------------
# Global paths
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBJECTS_DIR = os.path.join(BASE_DIR, "subjects")

# ------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------
def list_subjects():
    subjects = [f for f in os.listdir(SUBJECTS_DIR) if os.path.isdir(os.path.join(SUBJECTS_DIR, f))]
    return sorted(subjects)

def list_files(subject):
    path = os.path.join(SUBJECTS_DIR, subject)
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.startswith("description_")]

# ------------------------------------------------------------------
# Interactive Reader (Curses-based)
# ------------------------------------------------------------------
def read_file_interactive(file_path):
    def draw(stdscr):
        curses.curs_set(0)
        stdscr.keypad(True)

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_line = 0
        highlight_lines = set()
        height, width = stdscr.getmaxyx()

        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, f"📖 {os.path.basename(file_path)} | ↑↓ scroll | SPACE+↑↓ highlight | q to quit", curses.A_BOLD)

            for i in range(height - 2):
                line_index = current_line + i
                if line_index >= len(lines):
                    break
                line = lines[line_index].rstrip("\n")
                if line_index in highlight_lines:
                    stdscr.addstr(i + 1, 0, line[:width - 1], curses.A_REVERSE)
                else:
                    stdscr.addstr(i + 1, 0, line[:width - 1])

            key = stdscr.getch()
            if key == curses.KEY_UP and current_line > 0:
                current_line -= 1
            elif key == curses.KEY_DOWN and current_line < len(lines) - height + 2:
                current_line += 1
            elif key == ord(" "):  # highlight mode
                subkey = stdscr.getch()
                if subkey == curses.KEY_UP and current_line > 0:
                    highlight_lines.add(current_line - 1)
                    current_line -= 1
                elif subkey == curses.KEY_DOWN and current_line < len(lines) - 1:
                    highlight_lines.add(current_line + 1)
                    current_line += 1
            elif key == ord("q"):  # quit
                break

            stdscr.refresh()

    curses.wrapper(draw)

# ------------------------------------------------------------------
# Edit File (with reason)
# ------------------------------------------------------------------
def edit_file(file_path):
    reason = input("Enter reason for editing this file: ").strip()
    if not reason:
        print("❌ Edit reason is required.")
        return

    editor = os.environ.get("EDITOR", "nano" if platform.system() != "Windows" else "notepad")
    subprocess.call([editor, file_path])
    print(f"\n✅ Changes saved with reason: {reason}")

# ------------------------------------------------------------------
# Add New Subject
# ------------------------------------------------------------------
def add_subject():
    name = input("\nEnter new subject name: ").strip()
    if not name:
        print("❌ Subject name cannot be empty.")
        return

    subject_path = os.path.join(SUBJECTS_DIR, name)
    if os.path.exists(subject_path):
        print("⚠️ Subject already exists.")
        return

    os.makedirs(subject_path)
    description = input("Enter short description for this subject: ").strip()
    if not description:
        description = "No description provided."

    with open(os.path.join(subject_path, f"description_{name}.txt"), "w", encoding="utf-8") as f:
        f.write(description + "\n")

    print(f"✅ Subject '{name}' added successfully!")

# ------------------------------------------------------------------
# Add New Note
# ------------------------------------------------------------------
def add_note(subject):
    file_name = input("Enter note filename (without extension): ").strip()
    if not file_name:
        print("❌ File name cannot be empty.")
        return
    file_path = os.path.join(SUBJECTS_DIR, subject, f"{file_name}.txt")

    if os.path.exists(file_path):
        print("⚠️ A note with this name already exists.")
        return

    content = input("Enter brief starting content (optional, press Enter to skip): ")
    with open(file_path, "w", encoding="utf-8") as f:
        if content:
            f.write(content + "\n")

    print(f"✅ Note '{file_name}.txt' created successfully in '{subject}'.")
    choice = input("Do you want to edit it now? (y/n): ").strip().lower()
    if choice == "y":
        edit_file(file_path)

# ------------------------------------------------------------------
# CLI Navigation
# ------------------------------------------------------------------
def main_menu():
    while True:
        subjects = list_subjects()
        print("\n📚 Subjects Available:")
        for i, subject in enumerate(subjects, 1):
            print(f"{i}. {subject}")
        print("\na. ➕ Add new subject")
        print("0. Exit")

        choice = input("\nEnter choice: ").strip().lower()
        if choice == "0":
            print("👋 Exiting CLI Study Hub.")
            break
        elif choice == "a":
            add_subject()
        elif choice.isdigit() and 1 <= int(choice) <= len(subjects):
            subject_menu(subjects[int(choice) - 1])
        else:
            print("❌ Invalid choice, try again.")

def subject_menu(subject):
    while True:
        files = list_files(subject)
        print(f"\n📖 Notes in '{subject}':")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")
        print("\na. ➕ Add new note")
        print("b. 🔙 Back to subjects")

        choice = input("\nEnter file number or command: ").strip().lower()
        if choice == "b":
            break
        elif choice == "a":
            add_note(subject)
        elif choice.isdigit() and 1 <= int(choice) <= len(files):
            file_path = os.path.join(SUBJECTS_DIR, subject, files[int(choice) - 1])
            file_action_menu(file_path)
        else:
            print("❌ Invalid choice, try again.")

def file_action_menu(file_path):
    while True:
        print(f"\n📘 File: {os.path.basename(file_path)}")
        print("1. Read file")
        print("2. Edit file")
        print("b. Back to subject")
        choice = input("Enter choice: ").strip().lower()
        if choice == "1":
            read_file_interactive(file_path)
        elif choice == "2":
            edit_file(file_path)
        elif choice == "b":
            break
        else:
            print("❌ Invalid choice, try again.")

# ------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists(SUBJECTS_DIR):
        os.makedirs(SUBJECTS_DIR)
    print("📖 Welcome to CLI Study Hub (Open Source Notes Sharing)\n")
    main_menu()

