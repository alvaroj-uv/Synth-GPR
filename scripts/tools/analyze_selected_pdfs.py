
import sys
import os
from pypdf import PdfReader

# Force UTF-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

# List of specific PDF paths (hardcoded for this extraction task)
pdf_paths = [
    r"c:/Users/barba/Zotero/storage/44Y2UVFT/Bianchini Ciampoli et al. - 2019 - Railway ballast monitoring by GPR A test-site investigation.pdf",
    r"c:/Users/barba/Zotero/storage/3S6RDNE4/Liu et al. - 2024 - Deep Learning-Based Suppression of Strong Noise in GPR Data for Railway Subgrade Detection.pdf"
]

def extract_text(pdf_path, max_pages=3):
    print(f"\n{'='*80}")
    print(f"ANALYZING: {os.path.basename(pdf_path)}")
    print(f"{'='*80}")
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return

    try:
        reader = PdfReader(pdf_path)
        number_of_pages = len(reader.pages)
        print(f"Total Pages: {number_of_pages}")
        
        # Extract text from first few pages (Abstract + Intro) and maybe last page (Conclusions)
        pages_to_read = list(range(min(max_pages, number_of_pages)))
        
        for i in pages_to_read:
            page = reader.pages[i]
            text = page.extract_text()
            print(f"\n--- Page {i+1} ---")
            print(text[:1500]) # Limit characters per page for readability
            
    except Exception as e:
        print(f"Error reading PDF: {e}")


if __name__ == "__main__":
    for p in pdf_paths:
        extract_text(p)
