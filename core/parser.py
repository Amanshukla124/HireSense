import io
import PyPDF2

def extract_text_from_pdf(file_stream):
    """
    Extracts plain text from a PDF file stream.
    Returns the concatenated text of all pages.
    """
    try:
        reader = PyPDF2.PdfReader(file_stream)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n".join(pages_text).strip()
    except Exception as e:
        return None
