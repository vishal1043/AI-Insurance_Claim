import pytesseract
from PIL import Image
import pdfplumber
import logging
import re
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

logger = logging.getLogger(__name__)

def extract_text_from_image(image_path: str) -> str:
    """Extract text from image using pytesseract."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from image {image_path}: {str(e)}")
        return ""

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        return ""

def extract_text_from_file(file_path: str) -> str:
    """Extract text from file based on extension."""
    file_path_lower = file_path.lower()
    
    if file_path_lower.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        return extract_text_from_image(file_path)
    elif file_path_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    else:
        logger.warning(f"Unsupported file type: {file_path}")
        return ""

def find_dates_in_text(text: str) -> list:
    """Extract dates from text using regex patterns."""
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY or DD-MM-YYYY
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY/MM/DD or YYYY-MM-DD
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}',  # DD Month YYYY
    ]
    
    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)
    
    return dates

def find_amounts_in_text(text: str) -> list:
    """Extract monetary amounts from text."""
    # Pattern for amounts like Rs. 1000, ₹1000, 1000.00, etc.
    amount_pattern = r'(?:Rs\.?|₹)?\s*\d+(?:,\d{3})*(?:\.\d{2})?'
    amounts = re.findall(amount_pattern, text)
    return amounts
