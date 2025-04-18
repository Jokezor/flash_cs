import PyPDF2

def extract_text(pdf_file):
    text = ""
    with open(pdf_file, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

if __name__ == '__main__':
    # Quick test (ensure you have ostep.pdf in your working directory)
    text = extract_text("ostep.pdf")
    print(text[:1000]) 