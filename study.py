# study.py
import os
import sys
import shutil
from colorama import init, Fore, Style
from file_viewer import view_file
from file_uploader import upload_file
from error_handler import handle_error

init(autoreset=True)

SUBJECTS_DIR = "subjects"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def list_subjects(user_folder=None):
    path = os.path.join(SUBJECTS_DIR, user_folder) if user_folder else SUBJECTS_DIR
    if not os.path.exists(path):
        os.makedirs(path)
    subjects = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return subjects

def list_notes(user_folder, subject):
    path = os.path.join(SUBJECTS_DIR, user_folder, subject) if user_folder else os.path.join(SUBJECTS_DIR, subject)
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files

def create_subject(user_folder):
    try:
        name = input(Fore.YELLOW + "Enter new subject name: ").strip()
        if not name:
            print(Fore.RED + "Subject name cannot be empty!")
            return
        path = os.path.join(SUBJECTS_DIR, user_folder, name) if user_folder else os.path.join(SUBJECTS_DIR, name)
        os.makedirs(path, exist_ok=True)
        desc_file = os.path.join(path, f"description_{name}.txt")
        with open(desc_file, "w") as f:
            f.write(input("Enter short description: "))
        print(Fore.GREEN + f"Subject '{name}' created successfully!")
    except Exception as e:
        handle_error(e)

def choose_subject(subjects):
    print(Fore.CYAN + "\nAvailable Subjects:")
    for i, s in enumerate(subjects, 1):
        print(f"{i}. {s}")
    print("Type 'create subject' to add a new one or 'switch user' to change user")
    choice = input(Fore.YELLOW + "Enter command or number: ").strip()
    return choice

def choose_note(notes):
    print(Fore.CYAN + "\nAvailable Notes:")
    for i, n in enumerate(notes, 1):
        print(f"{i}. {n}")
    print("Commands: 'read <filename>', 'view pdf <filename>', 'view doc <filename>', 'analyze csv <filename>', 'upload note', 'back'")
    cmd = input(Fore.YELLOW + "Enter command: ").strip()
    return cmd

def main():
    clear_screen()
    print(Fore.GREEN + Style.BRIGHT + "👋 Welcome to CLI Study Hub v3.0")
    user = input(Fore.YELLOW + "Enter your username (Enter for Global mode): ").strip()
    user_folder = user if user else None
    while True:
        try:
            subjects = list_subjects(user_folder)
            cmd = choose_subject(subjects)
            if cmd.lower() == 'exit':
                print(Fore.GREEN + "Exiting... Remember to git add, commit, push if needed!")
                break
            elif cmd.lower() == 'switch user':
                user = input("Enter new username: ").strip()
                user_folder = user if user else None
            elif cmd.lower() == 'create subject':
                create_subject(user_folder)
            elif cmd.isdigit() and 0 < int(cmd) <= len(subjects):
                subject = subjects[int(cmd)-1]
                while True:
                    notes = list_notes(user_folder, subject)
                    note_cmd = choose_note(notes)
                    if note_cmd.lower() == 'back':
                        break
                    elif note_cmd.startswith('read '):
                        filename = note_cmd[5:].strip()
                        view_file(user_folder, subject, filename)
                    elif note_cmd.startswith('view pdf '):
                        filename = note_cmd[9:].strip()
                        view_file(user_folder, subject, filename)
                    elif note_cmd.startswith('view doc '):
                        filename = note_cmd[9:].strip()
                        view_file(user_folder, subject, filename)
                    elif note_cmd.startswith('analyze csv '):
                        filename = note_cmd[12:].strip()
                        view_file(user_folder, subject, filename)
                    elif note_cmd.lower() == 'upload note':
                        upload_file(user_folder, subject)
                    else:
                        print(Fore.RED + "Invalid command.")
            else:
                print(Fore.RED + "Invalid choice.")
        except Exception as e:
            handle_error(e)

if __name__ == "__main__":
    main()
