import cv2
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class OCRProvider(ABC):
    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> str:
        pass

class ImagePreprocessor:
    @staticmethod
    def preprocess(image_bytes: bytes) -> np.ndarray:
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image")
            
        # 1. Resize (to improve OCR accuracy on small text)
        img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        
        # 2. Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 3. Contrast Enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast = clahe.apply(gray)
        
        # 4. Noise Removal
        denoised = cv2.fastNlMeansDenoising(contrast, None, h=10, searchWindowSize=21, templateWindowSize=7)
        
        # 5. Deskew (Basic implementation)
        coords = np.column_stack(np.where(denoised > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        if abs(angle) > 0.5:
            (h, w) = denoised.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            deskewed = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        else:
            deskewed = denoised
            
        return deskewed


class TesseractOCRProvider(OCRProvider):
    def __init__(self):
        try:
            import pytesseract
            self.pytesseract = pytesseract
        except ImportError:
            logger.warning("Pytesseract not installed.")
            self.pytesseract = None

    def extract_text(self, image_bytes: bytes) -> str:
        if not self.pytesseract:
            raise RuntimeError("Pytesseract is not available")
            
        img = ImagePreprocessor.preprocess(image_bytes)
        result = self.pytesseract.image_to_string(img)
        return result


class OCRService:
    def __init__(self):
        self.providers = []
        
        tesseract = TesseractOCRProvider()
        if tesseract.pytesseract:
            self.providers.append(tesseract)

    def extract_text(self, image_bytes: bytes) -> str:
        if not self.providers:
            raise RuntimeError("No OCR providers available. Install pytesseract and tesseract-ocr.")
            
        for provider in self.providers:
            try:
                return provider.extract_text(image_bytes)
            except Exception as e:
                logger.error(f"OCR Provider {provider.__class__.__name__} failed: {e}")
                
        raise RuntimeError("All OCR providers failed to extract text.")

ocr_service = OCRService()
