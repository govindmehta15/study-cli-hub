# dependency_checker.py
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def check_dependency(package_name, import_name=None):
    """Check if a package is installed and return status"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True, "✅ Installed"
    except ImportError:
        return False, "❌ Missing"

def install_dependency(package_name):
    """Install a package using pip"""
    try:
        console.print(f"[yellow]Installing {package_name}...[/yellow]")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return True, "✅ Installed successfully"
        else:
            return False, f"❌ Installation failed: {result.stderr}"
    except Exception as e:
        return False, f"❌ Installation error: {e}"

def install_missing_dependencies():
    """Install all missing dependencies automatically"""
    dependencies = [
        ("rich", "rich", "Beautiful CLI interface"),
        ("PyPDF2", "PyPDF2", "PDF file reading"),
        ("python-docx", "docx", "Word document reading"),
        ("getch", "getch", "Cross-platform key input"),
        ("lxml", "lxml", "XML processing for Word docs")
    ]
    
    missing_packages = []
    
    # Check which packages are missing
    for package, import_name, description in dependencies:
        is_installed, status = check_dependency(package, import_name)
        if not is_installed:
            missing_packages.append(package)
    
    if not missing_packages:
        return True
    
    console.print(f"[yellow]Installing {len(missing_packages)} missing packages...[/yellow]")
    
    # Install missing packages
    for package in missing_packages:
        success, message = install_dependency(package)
        if not success:
            console.print(f"[red]{package}: {message}[/red]")
            return False
        else:
            console.print(f"[green]{package}: {message}[/green]")
    
    return True

def check_all_dependencies():
    """Check all required dependencies"""
    dependencies = [
        ("rich", "rich", "Beautiful CLI interface"),
        ("PyPDF2", "PyPDF2", "PDF file reading"),
        ("python-docx", "docx", "Word document reading"),
        ("getch", "getch", "Cross-platform key input"),
        ("lxml", "lxml", "XML processing for Word docs")
    ]
    
    console.print(Panel("[bold cyan]🔍 Checking Dependencies[/bold cyan]", expand=False))
    
    table = Table(title="Dependency Status", show_header=True, header_style="bold magenta")
    table.add_column("Package", width=15)
    table.add_column("Status", width=20)
    table.add_column("Description", width=30)
    
    missing_packages = []
    
    for package, import_name, description in dependencies:
        is_installed, status = check_dependency(package, import_name)
        table.add_row(package, status, description)
        if not is_installed:
            missing_packages.append(package)
    
    console.print(table)
    console.print()
    
    if missing_packages:
        console.print(Panel("[bold red]⚠️ Missing Dependencies Detected[/bold red]", expand=False))
        console.print(f"[yellow]Missing packages: {', '.join(missing_packages)}[/yellow]")
        console.print()
        
        # Offer to install missing packages
        install_choice = console.input("[yellow]Would you like to install missing packages automatically? (y/n): [/yellow]").strip().lower()
        
        if install_choice in ['y', 'yes']:
            console.print()
            for package in missing_packages:
                success, message = install_dependency(package)
                console.print(f"{package}: {message}")
            
            console.print()
            console.print("[green]✅ Dependency installation complete![/green]")
            console.print("[yellow]Please restart the application.[/yellow]")
            return False
        else:
            console.print()
            console.print("[yellow]Manual installation required:[/yellow]")
            console.print(f"[cyan]pip install {' '.join(missing_packages)}[/cyan]")
            console.print()
            console.print("[yellow]Or install all dependencies:[/yellow]")
            console.print("[cyan]pip install -r requirements.txt[/cyan]")
            return False
    else:
        console.print(Panel("[bold green]✅ All Dependencies Installed[/bold green]", expand=False))
        return True

def show_installation_guide():
    """Show comprehensive installation guide"""
    console.print(Panel("[bold cyan]📋 Installation Guide[/bold cyan]", expand=False))
    console.print()
    console.print("[green]Option 1: Install all dependencies at once[/green]")
    console.print("[cyan]pip install -r requirements.txt[/cyan]")
    console.print()
    console.print("[green]Option 2: Install dependencies individually[/green]")
    console.print("[cyan]pip install rich PyPDF2 python-docx getch lxml[/cyan]")
    console.print()
    console.print("[green]Option 3: Use conda (if available)[/green]")
    console.print("[cyan]conda install -c conda-forge rich PyPDF2 python-docx lxml[/cyan]")
    console.print("[cyan]pip install getch[/cyan]")
    console.print()
    console.print("[yellow]Note: Some packages may require additional system dependencies:[/yellow]")
    console.print("• [cyan]lxml[/cyan] may need libxml2 and libxslt development headers")
    console.print("• [cyan]PyPDF2[/cyan] works best with Python 3.6+")
    console.print("• [cyan]python-docx[/cyan] requires lxml for full functionality")

if __name__ == "__main__":
    if not check_all_dependencies():
        console.print()
        show_installation_guide()
        sys.exit(1)
    else:
        console.print("[green]🚀 Ready to start CLI Study Hub![/green]")
