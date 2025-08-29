import logging
from doctr.io import DocumentFile
from dotenv import load_dotenv
from doctr.models import ocr_predictor
from pdf2image import convert_from_bytes
import numpy as np

load_dotenv()



logging.basicConfig(level=logging.INFO)
logging.info("Initializing OCR predictor...")
predictor = ocr_predictor(pretrained=True)
logging.info("OCR predictor initialized successfully.")

# function to extract text from documents
def extract_text_from_doc(doc_bytes: bytes, content_type: str) -> str:
    """
    Extracts text from a document (image or PDF) using doctr.
    For PDFs, it first converts each page to an image before OCR.
    """
    all_text = ""
    
    try:
        if content_type in ["image/jpeg", "image/png"]:
            logging.info("Processing as single image...")
            doc = DocumentFile.from_images(doc_bytes)
            result = predictor(doc)
            all_text = result.render()

        elif content_type == "application/pdf":
            logging.info("Processing as PDF...")
            images_pil = convert_from_bytes(doc_bytes, dpi=300)
            if not images_pil:
                logging.warning("PDF conversion resulted in no images.")
                return ""
            
            logging.info(f"Converted PDF to {len(images_pil)} image(s). Running OCR...")
            pages_np = [np.array(img) for img in images_pil]
            result = predictor(pages_np)
            all_text = result.render()

        else:
            logging.warning(f"Unsupported content type: {content_type}")
            return ""

        return all_text.strip()

    except Exception as e:
        logging.error(f"Error during OCR processing for content type {content_type}: {e}")
        if "PDFInfoNotInstalledError" in str(e):
            logging.error("Poppler is likely not installed.")
        return ""