#!/usr/bin/env python3
"""
CLI Study Hub - Smart Startup Script
Automatically handles dependencies, GitHub sync, and provides a seamless experience
"""

import os
import sys
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    """Smart startup function"""
    console.print(Panel("[bold green]🚀 CLI Study Hub v4.0 - Smart Startup[/bold green]", expand=False))
    console.print()
    
    # Check if we're in the right directory
    if not os.path.exists("study.py"):
        console.print("[red]❌ study.py not found![/red]")
        console.print("[yellow]Make sure you're in the CLI Study Hub directory.[/yellow]")
        return False
    
    console.print("[green]✅ Starting CLI Study Hub with full automation...[/green]")
    console.print()
    console.print("[dim]Features enabled:[/dim]")
    console.print("  🔧 Auto-install missing dependencies")
    console.print("  📥 Auto-pull GitHub updates")
    console.print("  📤 Auto-push changes on exit")
    console.print("  🛡️ Universal file format support")
    console.print()
    
    try:
        # Start the main application
        result = subprocess.run([sys.executable, "study.py"], cwd=os.getcwd())
        return result.returncode == 0
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Error starting application: {e}[/red]")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
