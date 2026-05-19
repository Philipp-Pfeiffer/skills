#!/usr/bin/env python3
"""Basic HTML to PDF fallback using available Python libraries."""

import sys
import os


def try_weasyprint(html_path, pdf_path):
    try:
        from weasyprint import HTML
        HTML(html_path).write_pdf(pdf_path)
        return True
    except ImportError:
        return False


def try_fpdf(html_path, pdf_path):
    """Very basic fallback - strips HTML tags and outputs as text PDF."""
    try:
        from fpdf import FPDF
        import re
        
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Strip HTML tags
        text = re.sub(r'<[^>]+>', '', content)
        # Decode HTML entities
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        for line in text.split('\n'):
            if line.strip():
                pdf.cell(0, 10, txt=line.strip(), ln=True)
        
        pdf.output(pdf_path)
        return True
    except Exception:
        return False


def main():
    if len(sys.argv) != 3:
        print("Usage: html_to_pdf.py <input.html> <output.pdf>")
        sys.exit(1)
    
    html_path = sys.argv[1]
    pdf_path = sys.argv[2]
    
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found")
        sys.exit(1)
    
    # Try backends in order
    backends = [
        ("weasyprint", try_weasyprint),
        ("fpdf fallback", try_fpdf),
    ]
    
    for name, func in backends:
        print(f"Trying {name}...")
        if func(html_path, pdf_path):
            print(f"Success: {pdf_path}")
            sys.exit(0)
    
    print("Error: No PDF backend available")
    sys.exit(1)


if __name__ == "__main__":
    main()
