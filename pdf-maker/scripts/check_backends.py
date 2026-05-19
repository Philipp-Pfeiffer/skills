#!/usr/bin/env python3
"""Check which PDF backends are available on the system."""

import shutil
import subprocess
import sys


def check_command(cmd):
    """Check if a command is available and get its version."""
    path = shutil.which(cmd)
    if not path:
        return None
    try:
        result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
        version = result.stdout.strip().split('\n')[0] if result.stdout else "unknown"
        return {"path": path, "version": version}
    except Exception:
        return {"path": path, "version": "unknown"}


def check_python_lib(name):
    """Check if a Python library is available."""
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def main():
    print("=== PDF Backend Check ===\n")
    
    backends = {
        "weasyprint": check_command("weasyprint"),
        "wkhtmltopdf": check_command("wkhtmltopdf"),
        "pandoc": check_command("pandoc"),
    }
    
    python_libs = {
        "weasyprint": check_python_lib("weasyprint"),
        "reportlab": check_python_lib("reportlab"),
        "fpdf": check_python_lib("fpdf") or check_python_lib("fpdf2"),
    }
    
    available = []
    
    for name, info in backends.items():
        if info:
            print(f"✓ {name}: {info['path']}")
            print(f"  Version: {info['version']}")
            available.append(name)
        else:
            print(f"✗ {name}: not found")
    
    print()
    for name, available_flag in python_libs.items():
        if available_flag:
            print(f"✓ Python lib '{name}': available")
            if name not in available:
                available.append(name)
        else:
            print(f"✗ Python lib '{name}': not found")
    
    print(f"\n=== Best backend: {available[0] if available else 'NONE'} ===")
    return 0 if available else 1


if __name__ == "__main__":
    sys.exit(main())
