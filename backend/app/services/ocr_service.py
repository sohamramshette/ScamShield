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


class PaddleOCRProvider(OCRProvider):
    def __init__(self):
        try:
            from paddleocr import PaddleOCR
            # Use English, disable debug logging
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
        except ImportError:
            logger.warning("PaddleOCR not installed or failed to initialize.")
            self.ocr = None

    def extract_text(self, image_bytes: bytes) -> str:
        if not self.ocr:
            raise RuntimeError("PaddleOCR is not available")
            
        img = ImagePreprocessor.preprocess(image_bytes)
        result = self.ocr.ocr(img, cls=True)
        
        if not result or not result[0]:
            return ""
            
        extracted_text = []
        for line in result[0]:
            text, confidence = line[1]
            extracted_text.append(text)
            
        return "\n".join(extracted_text)


class EasyOCRProvider(OCRProvider):
    def __init__(self):
        try:
            import easyocr
            self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        except ImportError:
            logger.warning("EasyOCR not installed or failed to initialize.")
            self.reader = None

    def extract_text(self, image_bytes: bytes) -> str:
        if not self.reader:
            raise RuntimeError("EasyOCR is not available")
            
        img = ImagePreprocessor.preprocess(image_bytes)
        result = self.reader.readtext(img, detail=0, paragraph=True)
        return "\n".join(result)


class OCRService:
    def __init__(self):
        self.providers = []
        
        # Try paddle OCR first
        paddle = PaddleOCRProvider()
        if paddle.ocr:
            self.providers.append(paddle)
            
        # Try easy ocr second
        easy = EasyOCRProvider()
        if easy.reader:
            self.providers.append(easy)

    def extract_text(self, image_bytes: bytes) -> str:
        if not self.providers:
            # Fallback if neither is installed, maybe return mock or raise
            raise RuntimeError("No OCR providers available. Install paddleocr or easyocr.")
            
        for provider in self.providers:
            try:
                return provider.extract_text(image_bytes)
            except Exception as e:
                logger.error(f"OCR Provider {provider.__class__.__name__} failed: {e}")
                
        raise RuntimeError("All OCR providers failed to extract text.")

ocr_service = OCRService()
