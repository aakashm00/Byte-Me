#!/usr/bin/env python3
"""ASL detector using Roboflow API (pre-trained model)."""

import cv2
import numpy as np
import requests
import base64
import os
import dotenv

dotenv.load_dotenv()

class ASLDetector:
    def __init__(self):
        """Initialize with Roboflow API."""
        self.api_key = os.getenv("ROBOFLOW_API_KEY")
        # This uses the pre-trained model, not the dataset
        self.model_url = "https://detect.roboflow.com/american-sign-language-letters/6"
        
    def detect_letter(self, image: np.ndarray) -> dict:
        """Detect ASL letter using Roboflow API."""
        if not self.api_key:
            return {"error": "API key not found", "letter": None, "confidence": 0}
        
        try:
            # Encode image
            _, buffer = cv2.imencode('.jpg', image)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # API call to pre-trained model
            response = requests.post(
                f"{self.model_url}?api_key={self.api_key}&confidence=40&overlap=30",
                data=img_base64,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                predictions = result.get('predictions', [])
                
                if predictions:
                    best = max(predictions, key=lambda x: x['confidence'])
                    return {
                        "letter": best['class'],
                        "confidence": best['confidence'],
                        "error": None
                    }
                else:
                    return {"letter": None, "confidence": 0, "error": "No detection"}
            else:
                return {"letter": None, "confidence": 0, "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"letter": None, "confidence": 0, "error": str(e)}

def test_api_detector():
    """Test the API detector."""
    print("=== Testing Roboflow API ASL Detector ===")
    
    detector = ASLDetector()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    print("✅ Camera opened - Show ASL letters")
    print("Press SPACE to detect letter, Q to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        cv2.putText(frame, "ASL API Detector", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "SPACE: Detect | Q: Quit", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('ASL API Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            print("\n--- API Detection ---")
            result = detector.detect_letter(frame)
            
            if result["error"]:
                print(f"❌ Error: {result['error']}")
            elif result["letter"]:
                print(f"✅ Detected: {result['letter']} ({result['confidence']:.2f})")
            else:
                print("⚠️ No letter detected")
            print("------------------------\n")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_api_detector()