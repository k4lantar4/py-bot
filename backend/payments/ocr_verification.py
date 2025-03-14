import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import re
import logging
from django.conf import settings
from .models import CardPayment

logger = logging.getLogger(__name__)

class ReceiptOCRProcessor:
    """Process payment receipts using OCR to extract and verify payment information"""
    
    def __init__(self):
        # Configure Tesseract path from settings if provided
        tesseract_cmd = getattr(settings, 'TESSERACT_CMD_PATH', 'tesseract')
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Regex patterns for extracting information
        self.amount_pattern = r'مبلغ[:\s]*([\d,]+)'
        self.card_pattern = r'کارت[:\s]*(\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})'
        self.ref_pattern = r'پیگیری[:\s]*(\d+)'
        self.date_pattern = r'\d{4}/\d{2}/\d{2}'
        self.time_pattern = r'\d{2}:\d{2}:\d{2}'
    
    def preprocess_image(self, image_data):
        """Preprocess image for better OCR results"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Noise removal
            kernel = np.ones((1, 1), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            return thresh
        except Exception as e:
            logger.error(f"Image preprocessing error: {str(e)}")
            return None
    
    def extract_text(self, image):
        """Extract text from image using Tesseract"""
        try:
            # Configure Tesseract to use Persian
            custom_config = r'--oem 3 --psm 6 -l fas+eng'
            text = pytesseract.image_to_string(image, config=custom_config)
            return text
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            return None
    
    def extract_payment_info(self, text):
        """Extract payment information from OCR text"""
        try:
            info = {
                'amount': None,
                'card_number': None,
                'reference': None,
                'date': None,
                'time': None,
                'raw_text': text
            }
            
            # Extract amount
            amount_match = re.search(self.amount_pattern, text)
            if amount_match:
                amount_str = amount_match.group(1).replace(',', '')
                info['amount'] = int(amount_str)
            
            # Extract card number
            card_match = re.search(self.card_pattern, text)
            if card_match:
                card_number = card_match.group(1).replace('-', '').replace(' ', '')
                info['card_number'] = card_number
            
            # Extract reference number
            ref_match = re.search(self.ref_pattern, text)
            if ref_match:
                info['reference'] = ref_match.group(1)
            
            # Extract date and time
            date_match = re.search(self.date_pattern, text)
            time_match = re.search(self.time_pattern, text)
            if date_match:
                info['date'] = date_match.group(0)
            if time_match:
                info['time'] = time_match.group(0)
            
            return info
        except Exception as e:
            logger.error(f"Payment info extraction error: {str(e)}")
            return None
    
    def verify_payment(self, payment_id, receipt_image):
        """Verify a payment using OCR on the receipt image"""
        try:
            # Get payment instance
            payment = CardPayment.objects.get(id=payment_id)
            
            # Process image
            processed_image = self.preprocess_image(receipt_image.read())
            if not processed_image:
                return False, "Image processing failed"
            
            # Extract text
            text = self.extract_text(processed_image)
            if not text:
                return False, "Text extraction failed"
            
            # Extract payment information
            info = self.extract_payment_info(text)
            if not info:
                return False, "Payment information extraction failed"
            
            # Verify payment details
            verified = payment.verify_with_ocr(info)
            
            if verified:
                logger.info(f"Payment {payment_id} verified successfully via OCR")
                return True, "Payment verified successfully"
            else:
                logger.warning(f"Payment {payment_id} OCR verification failed")
                return False, "Payment details do not match"
                
        except CardPayment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return False, "Payment not found"
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return False, str(e) 