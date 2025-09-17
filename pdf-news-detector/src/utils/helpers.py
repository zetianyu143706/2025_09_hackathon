def log_message(message):
    print(f"[LOG] {message}")

def handle_error(error):
    print(f"[ERROR] {error}")

def validate_pdf_path(pdf_path):
    if not pdf_path.endswith('.pdf'):
        raise ValueError("The provided path is not a valid PDF file.")
    return True

def format_report_data(image_score, text_score, pdf_name):
    return {
        "pdf_name": pdf_name,
        "image_score": image_score,
        "text_score": text_score
    }