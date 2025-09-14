#!/usr/bin/env python3
"""Simple OCR for agent tool."""

import cv2
import easyocr
import numpy as np

class SimpleOCR:
    def __init__(self):
        """Initialize EasyOCR reader."""
        print("🔄 Loading EasyOCR...")
        self.reader = easyocr.Reader(['en'], gpu=False)
        print("✅ EasyOCR ready!")
    
    def extract_text_from_image(self, image: np.ndarray) -> dict:
        """Extract text from image - main method for agent."""
        try:
            # Use EasyOCR to read text
            results = self.reader.readtext(image)
            
            if not results:
                return {
                    "text": "",
                    "confidence": 0,
                    "word_count": 0,
                    "error": "No text detected"
                }
            
            # Process results - only keep high confidence text
            extracted_texts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Only confident results
                    extracted_texts.append(text)
                    confidences.append(confidence)
            
            if not extracted_texts:
                return {
                    "text": "",
                    "confidence": 0,
                    "word_count": 0,
                    "error": "Low confidence text"
                }
            
            # Combine all text
            full_text = " ".join(extracted_texts)
            avg_confidence = sum(confidences) / len(confidences)
            
            return {
                "text": full_text,
                "confidence": avg_confidence * 100,
                "word_count": len(full_text.split()),
                "error": None
            }
            
        except Exception as e:
            return {
                "text": "",
                "confidence": 0,
                "word_count": 0,
                "error": str(e)
            }