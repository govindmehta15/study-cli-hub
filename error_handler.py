# error_handler.py
import traceback
import os
from datetime import datetime

LOG_FILE = "logs/error.log"

def handle_error(e):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(f"[{datetime.now()}] {str(e)}\n")
        f.write(traceback.format_exc() + "\n\n")
    print(f"⚠️ An error occurred: {e}")
