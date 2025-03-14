import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import re
import logging
from django.conf import settings
from .models import CardPayment
import traceback

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
        
        # OCR configuration
        self.ocr_config = r'--oem 3 --psm 6 -l fas+eng'
        
        # Image preprocessing parameters
        self.kernel_size = getattr(settings, 'OCR_KERNEL_SIZE', (1, 1))
        self.threshold_block_size = getattr(settings, 'OCR_THRESHOLD_BLOCK_SIZE', 11)
        self.threshold_c = getattr(settings, 'OCR_THRESHOLD_C', 2)
    
    def preprocess_image(self, image_data):
        """Preprocess image for better OCR results"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                logger.error("Failed to decode image data")
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                self.threshold_block_size,
                self.threshold_c
            )
            
            # Noise removal
            kernel = np.ones(self.kernel_size, np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # Additional preprocessing for Persian text
            thresh = cv2.bitwise_not(thresh)
            
            return thresh
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {str(e)}\n{traceback.format_exc()}")
            return None
    
    def extract_text(self, image):
        """Extract text from image using Tesseract"""
        try:
            # Configure Tesseract to use Persian
            text = pytesseract.image_to_string(image, config=self.ocr_config)
            
            if not text.strip():
                logger.warning("No text extracted from image")
                return None
                
            return text
            
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}\n{traceback.format_exc()}")
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
                'raw_text': text,
                'confidence': 0
            }
            
            # Extract amount
            amount_match = re.search(self.amount_pattern, text)
            if amount_match:
                amount_str = amount_match.group(1).replace(',', '')
                info['amount'] = int(amount_str)
                info['confidence'] += 1
            
            # Extract card number
            card_match = re.search(self.card_pattern, text)
            if card_match:
                card_number = card_match.group(1).replace('-', '').replace(' ', '')
                info['card_number'] = card_number
                info['confidence'] += 1
            
            # Extract reference number
            ref_match = re.search(self.ref_pattern, text)
            if ref_match:
                info['reference'] = ref_match.group(1)
                info['confidence'] += 1
            
            # Extract date and time
            date_match = re.search(self.date_pattern, text)
            time_match = re.search(self.time_pattern, text)
            if date_match:
                info['date'] = date_match.group(0)
                info['confidence'] += 0.5
            if time_match:
                info['time'] = time_match.group(0)
                info['confidence'] += 0.5
            
            # Calculate confidence percentage
            info['confidence'] = (info['confidence'] / 4) * 100
            
            if info['confidence'] < 50:
                logger.warning(f"Low confidence OCR result: {info['confidence']}%")
            
            return info
            
        except Exception as e:
            logger.error(f"Payment info extraction error: {str(e)}\n{traceback.format_exc()}")
            return None
    
    def verify_payment(self, payment_id, receipt_image):
        """Verify a payment using OCR on the receipt image"""
        try:
            # Get payment instance
            payment = CardPayment.objects.get(id=payment_id)
            
            # Process image
            processed_image = self.preprocess_image(receipt_image.read())
            if not processed_image:
                return False, "خطا در پردازش تصویر"
            
            # Extract text
            text = self.extract_text(processed_image)
            if not text:
                return False, "خطا در استخراج متن از تصویر"
            
            # Extract payment information
            info = self.extract_payment_info(text)
            if not info:
                return False, "خطا در استخراج اطلاعات پرداخت"
            
            # Log OCR results for debugging
            logger.info(f"OCR Results for payment {payment_id}:")
            logger.info(f"Amount: {info['amount']}")
            logger.info(f"Card: {info['card_number']}")
            logger.info(f"Reference: {info['reference']}")
            logger.info(f"Confidence: {info['confidence']}%")
            
            # Verify payment details
            verified = payment.verify_with_ocr(info)
            
            if verified:
                logger.info(f"Payment {payment_id} verified successfully via OCR")
                return True, "پرداخت با موفقیت تایید شد"
            else:
                logger.warning(f"Payment {payment_id} OCR verification failed")
                return False, "اطلاعات پرداخت مطابقت ندارد"
                
        except CardPayment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return False, "پرداخت یافت نشد"
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}\n{traceback.format_exc()}")
            return False, str(e) 