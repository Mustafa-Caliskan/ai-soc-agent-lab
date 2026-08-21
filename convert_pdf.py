import os
import sys

# DLL path workaround for pywin32 on Windows
def apply_win32_dll_workaround():
    try:
        import site
        sp_dirs = site.getsitepackages()
    except Exception:
        sp_dirs = []
        
    # Standard paths to search for pywin32_system32
    potential_dirs = []
    # Add paths from sys.path
    for p in sys.path:
        if "site-packages" in p:
            potential_dirs.append(p)
            potential_dirs.append(os.path.join(p, "pywin32_system32"))
    # Add standard site-packages
    for sd in sp_dirs:
        potential_dirs.append(os.path.join(sd, "pywin32_system32"))
        
    for d in potential_dirs:
        if d.endswith("pywin32_system32") and os.path.exists(d):
            print(f"[INFO] Found pywin32 DLL directory: {d}")
            if hasattr(os, 'add_dll_directory'):
                try:
                    os.add_dll_directory(d)
                except Exception as e:
                    print(f"[WARN] Failed os.add_dll_directory: {e}")
            os.environ["PATH"] = d + os.pathsep + os.environ["PATH"]
            break

def convert_docx_to_pdf(docx_path, pdf_path):
    print(f"Starting conversion: {docx_path} -> {pdf_path}")
    
    apply_win32_dll_workaround()
    
    # Try importing win32com
    try:
        import win32com.client
    except ImportError:
        print("[INFO] win32com not found. Installing pywin32...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
        apply_win32_dll_workaround()
        import win32com.client
        
    try:
        # Initialize Word application
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        # Open document
        doc = word.Documents.Open(os.path.abspath(docx_path))
        
        # Save as PDF (FileFormat=17 represents PDF in Word)
        doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)
        
        # Close document and application
        doc.Close()
        word.Quit()
        print("[OK] PDF conversion successful!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed converting via MS Word: {e}")
        return False

if __name__ == "__main__":
    docx = "CyberTech_IMRAD_Raporu.docx"
    pdf = "CyberTech_IMRAD_Raporu.pdf"
    if os.path.exists(docx):
        convert_docx_to_pdf(docx, pdf)
    else:
        print(f"[ERROR] {docx} not found!")
