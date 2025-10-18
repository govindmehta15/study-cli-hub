#!/usr/bin/env python3
"""
CLI Study Hub - Complete Setup Script
Installs ALL dependencies and prepares the application for first use
"""

import os
import sys
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

def install_package_with_progress(package_name, description):
    """Install a package with progress indication"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold blue]Installing {package_name}..."),
            console=console,
        ) as progress:
            task = progress.add_task(f"Installing {package_name}", total=None)
            
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package_name
            ], capture_output=True, text=True)
            
            progress.update(task, completed=True)
            
            if result.returncode == 0:
                return True, f"✅ {package_name} installed successfully"
            else:
                return False, f"❌ Failed to install {package_name}: {result.stderr}"
                
    except Exception as e:
        return False, f"❌ Error installing {package_name}: {e}"

def setup_cli_study_hub():
    """Complete setup for CLI Study Hub"""
    console.print(Panel("[bold green]🚀 CLI Study Hub - Complete Setup[/bold green]", expand=False))
    console.print()
    
    # Check Python version
    if sys.version_info < (3, 6):
        console.print("[red]❌ Python 3.6 or higher is required![/red]")
        console.print(f"Current version: {sys.version}")
        return False
    
    console.print(f"[green]✅ Python version: {sys.version.split()[0]}[/green]")
    console.print()
    
    # Define all dependencies
    dependencies = [
        ("rich", "Beautiful CLI interface with colors and tables"),
        ("PyPDF2", "PDF file reading and text extraction"),
        ("python-docx", "Word document reading and processing"),
        ("getch", "Cross-platform key input for interactive features"),
        ("lxml", "XML processing required for Word documents")
    ]
    
    console.print(Panel("[bold cyan]📦 Installing All Dependencies[/bold cyan]", expand=False))
    console.print("[dim]This ensures support for ALL file formats without errors[/dim]")
    console.print()
    
    # Install each dependency
    results = []
    for package, description in dependencies:
        success, message = install_package_with_progress(package, description)
        results.append((package, success, message))
        console.print(f"  {message}")
    
    console.print()
    
    # Show installation summary
    table = Table(title="Installation Summary", show_header=True, header_style="bold magenta")
    table.add_column("Package", width=15)
    table.add_column("Status", width=20)
    table.add_column("Description", width=40)
    
    all_success = True
    for package, success, message in results:
        status = "✅ Installed" if success else "❌ Failed"
        description = next(desc for pkg, desc in dependencies if pkg == package)
        table.add_row(package, status, description)
        if not success:
            all_success = False
    
    console.print(table)
    console.print()
    
    if all_success:
        console.print(Panel("[bold green]🎉 Setup Complete![/bold green]", expand=False))
        console.print()
        console.print("[green]✅ All dependencies installed successfully[/green]")
        console.print("[green]✅ CLI Study Hub is ready to use[/green]")
        console.print()
        console.print("[yellow]🚀 Next steps:[/yellow]")
        console.print("1. Run: [cyan]python3 study.py[/cyan]")
        console.print("2. Enter your username or press Enter for global mode")
        console.print("3. Start studying with any file format!")
        console.print()
        console.print("[dim]All file types are now supported:[/dim]")
        console.print("  📄 Text files (txt, md, py, json, etc.)")
        console.print("  📋 Documents (pdf, docx, csv)")
        console.print("  🖼️ Images (jpg, png, gif, etc.)")
        console.print("  📦 Archives (zip, rar, 7z, etc.)")
        console.print("  🎵 Media files (mp3, mp4, etc.)")
        console.print("  ⚙️ Executables and binary files")
        
    else:
        console.print(Panel("[bold red]⚠️ Setup Incomplete[/bold red]", expand=False))
        console.print()
        console.print("[yellow]Some dependencies failed to install.[/yellow]")
        console.print("[yellow]The application will still work, but some file types may not be supported.[/yellow]")
        console.print()
        console.print("[cyan]Try running:[/cyan]")
        console.print("[cyan]pip install -r requirements.txt[/cyan]")
    
    return all_success

def main():
    """Main setup function"""
    try:
        success = setup_cli_study_hub()
        return success
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]Setup error: {e}[/red]")
        return False

if __name__ == "__main__":
    success = main()
    console.print()
    input("Press Enter to continue...")
    sys.exit(0 if success else 1)
