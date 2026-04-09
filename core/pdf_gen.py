from fpdf import FPDF
import io

def generate_pdf_bytes(content_text, title="Resume"):
    """
    Generates a PDF from the given text and returns it as a BytesIO stream.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header
    pdf.set_font("helvetica", style="B", size=16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(5)
    
    # Body
    pdf.set_font("helvetica", size=11)
    
    # Prevent encoding errors with standard latin-1 font
    safe_text = content_text.encode('latin-1', 'replace').decode('latin-1')
    
    # Multi cell for automatic text wrapping
    pdf.multi_cell(0, 6, safe_text)
    
    # Returns bytes payload
    pdf_bytes = pdf.output()
    return io.BytesIO(pdf_bytes)
