import fitz  # PyMuPDF

def extract_content(pdf_path):
    text_content = ""
    images = []

    # Open the PDF file
    with fitz.open(pdf_path) as pdf_document:
        # Extract text from each page
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text_content += page.get_text()

            # Extract images from the page
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                images.append(image_bytes)

    return text_content, images