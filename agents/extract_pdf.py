from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path, start_page, end_page):
    reader = PdfReader(file_path)
    pages = reader.pages[start_page-1:end_page]
    text = "\n\n".join(page.extract_text() or "" for page in pages)
    return text
