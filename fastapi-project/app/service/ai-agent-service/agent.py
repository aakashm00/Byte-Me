# #!/usr/bin/env python3
# """Simple Async OCR Chatbot."""

# import cv2
# import numpy as np
# from connectonion import Agent
# import os
# import dotenv
# import base64
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from tool import SimpleOCR

# dotenv.load_dotenv()

# class AsyncOCRChatbot:
#     def __init__(self):
#         """Initialize async OCR chatbot."""
#         self.ocr = SimpleOCR()
#         self.executor = ThreadPoolExecutor(max_workers=2)
        
#         self.agent = Agent(
#             name="ocr-chatbot",
#             tools=[self.extract_text_from_image],
#             model=os.getenv("MODEL", "gpt-4o-mini"),
#             system_prompt="""You are a helpful OCR assistant that extracts and explains text from images.

# When processing images:
# 1. Use the extract_text_from_image tool to get the raw text
# 2. Analyze and summarize the content in a clear, well-formatted response
# 3. Use proper formatting with headings, bullet points, and structure
# 4. Highlight key information like dates, times, important details
# 5. Make the response easy to scan and understand

# Format your responses like this:
# ## Document Summary
# [Brief description of what this document is]

# ### Key Information
# • **Important Point 1:** Details
# • **Important Point 2:** Details
# • **Important Point 3:** Details

# ### Schedule/Timeline (if applicable)
# **Day/Time:** Event/Activity

# ### Contact Information (if applicable)
# • **Contact Type:** Details

# ### Additional Notes
# Any other relevant information

# Keep responses concise but informative. Focus on what matters most to the user."""
       

#         )
#         print("✅ Async OCR Chatbot ready!")
        
#         self._current_image = None
    
#     def extract_text_from_image(self, description: str = "the uploaded image") -> str:
#         """Tool: Extract text from uploaded image."""
#         if self._current_image is None:
#             return "No image uploaded yet."
        
#         result = self.ocr.extract_text_from_image(self._current_image)
        
#         if result['error']:
#             return f"Error reading image: {result['error']}"
        
#         if not result['text']:
#             return "No text found in image."
        
#         return f"Text found: {result['text']} (Confidence: {result['confidence']:.1f}%)"
    
#     async def process_camera_scan(self, base64_image: str, message: str = "What text is in this scan?") -> str:
#         """Process camera scan async."""
#         # Convert base64 to image
#         image = await self._base64_to_image_async(base64_image)
        
#         if image is None:
#             return "Could not process the scan. Please try again."
        
#         # Store image and process with agent async
#         self._current_image = image
        
#         # Run agent in thread pool to avoid blocking
#         loop = asyncio.get_event_loop()
#         response = await loop.run_in_executor(
#             self.executor, 
#             self.agent.input, 
#             message
#         )
        
#         self._current_image = None
        
#         return response
    
#     async def chat(self, message: str) -> str:
#         """Simple async chat without image."""
#         loop = asyncio.get_event_loop()
#         response = await loop.run_in_executor(
#             self.executor,
#             self.agent.input,
#             message
#         )
#         return response
    
#     async def _base64_to_image_async(self, base64_image: str) -> np.ndarray:
#         """Convert base64 to OpenCV image async."""
#         def _convert():
#             try:
#                 # Remove data URL prefix if present
#                 if base64_image.startswith('data:image'):
#                     image_data = base64_image.split(',')[1]
#                 else:
#                     image_data = base64_image
                
#                 # Decode to image
#                 image_bytes = base64.b64decode(image_data)
#                 nparr = np.frombuffer(image_bytes, np.uint8)
#                 image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
#                 return image
#             except:
#                 return None
        
#         # Run conversion in thread pool
#         loop = asyncio.get_event_loop()
#         return await loop.run_in_executor(self.executor, _convert)

# # For backward compatibility, create sync wrapper
# class OCRChatbot:
#     def __init__(self):
#         """Sync wrapper for async chatbot."""
#         self.async_chatbot = AsyncOCRChatbot()
    
#     def process_camera_scan(self, base64_image: str, message: str = "What text is in this scan?") -> str:
#         """Sync wrapper for camera scan."""
#         return asyncio.run(self.async_chatbot.process_camera_scan(base64_image, message))
    
#     def chat(self, message: str) -> str:
#         """Sync wrapper for chat."""
#         return asyncio.run(self.async_chatbot.chat(message))

# async def main():
#     """Test the async chatbot."""
#     chatbot = AsyncOCRChatbot()
    
#     # Test with base64 image
#     test_path = r"D:\code\hackathon-UNSW\fastapi-project\test"
    
#     if os.path.exists(test_path):
#         image_files = [f for f in os.listdir(test_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
#         if image_files:
#             # Convert test image to base64
#             with open(os.path.join(test_path, image_files[0]), 'rb') as f:
#                 image_bytes = f.read()
            
#             base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
#             # Test async camera scan
#             print("🔄 Processing image async...")
#             response = await chatbot.process_camera_scan(base64_image, "What text is in this image?")
#             print(f"🤖 {response}")

# if __name__ == "__main__":
#     asyncio.run(main())



#!/usr/bin/env python3
"""Simple Async OCR Chatbot with Memory."""

import cv2
import numpy as np
from connectonion import Agent
import os
import dotenv
import base64
import asyncio
from concurrent.futures import ThreadPoolExecutor
from tool import SimpleOCR

dotenv.load_dotenv()

class AsyncOCRChatbot:
    def __init__(self):
        """Initialize async OCR chatbot with conversation memory."""
        self.ocr = SimpleOCR()
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Simple conversation memory
        self.conversation_history = []
        self.last_ocr_result = ""
        
        self.agent = Agent(
            name="ocr-chatbot",
            tools=[self.extract_text_from_image],
            model=os.getenv("MODEL", "gpt-4o-mini"),
            system_prompt="""You are a helpful OCR assistant with conversation memory.

When processing images:
1. Extract and analyze text clearly
2. Use HTML formatting for better display
3. Remember the content for follow-up questions

For follow-up questions:
1. Reference previously extracted text
2. Answer based on conversation context
3. Be helpful and specific

Format responses with HTML:
<h2>Summary</h2>
<h3>Key Points</h3>
<ul><li><strong>Point:</strong> Detail</li></ul>"""
        )
        print("✅ OCR Chatbot with memory ready!")
        
        self._current_image = None
    
    def extract_text_from_image(self, description: str = "the uploaded image") -> str:
        """Extract text from image."""
        if self._current_image is None:
            return "No image uploaded yet."
        
        result = self.ocr.extract_text_from_image(self._current_image)
        
        if result['error']:
            return f"Error reading image: {result['error']}"
        
        if not result['text']:
            return "No text found in image."
        
        # Store for future reference
        self.last_ocr_result = result['text']
        return f"Extracted text: {result['text']}"
    
    def _build_context(self, message: str) -> str:
        """Build message with context."""
        context_parts = []
        
        # Add last OCR result
        if self.last_ocr_result:
            context_parts.append(f"PREVIOUSLY EXTRACTED: {self.last_ocr_result}")
        
        # Add recent chat history (last 3)
        if self.conversation_history:
            context_parts.append("RECENT CONVERSATION:")
            for exchange in self.conversation_history[-3:]:
                context_parts.append(f"User: {exchange['user']}")
                context_parts.append(f"Assistant: {exchange['assistant']}")
        
        context_parts.append(f"CURRENT: {message}")
        return "\n".join(context_parts)
    
    async def process_camera_scan(self, base64_image: str, message: str = "What text is in this scan?") -> str:
        """Process camera scan with memory."""
        image = await self._base64_to_image_async(base64_image)
        
        if image is None:
            return "Could not process the scan. Please try again."
        
        self._current_image = image
        context_message = self._build_context(message)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(self.executor, self.agent.input, context_message)
        
        # Store conversation
        self.conversation_history.append({"user": message, "assistant": response})
        
        self._current_image = None
        return response
    
    async def chat(self, message: str) -> str:
        """Chat with memory."""
        context_message = self._build_context(message)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(self.executor, self.agent.input, context_message)
        
        # Store conversation
        self.conversation_history.append({"user": message, "assistant": response})
        
        return response
    
    async def _base64_to_image_async(self, base64_image: str) -> np.ndarray:
        """Convert base64 to image."""
        def _convert():
            try:
                if base64_image.startswith('data:image'):
                    image_data = base64_image.split(',')[1]
                else:
                    image_data = base64_image
                
                image_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return image
            except:
                return None
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _convert)

# Sync wrapper (unchanged)
class OCRChatbot:
    def __init__(self):
        self.async_chatbot = AsyncOCRChatbot()
    
    def process_camera_scan(self, base64_image: str, message: str = "What text is in this scan?") -> str:
        return asyncio.run(self.async_chatbot.process_camera_scan(base64_image, message))
    
    def chat(self, message: str) -> str:
        return asyncio.run(self.async_chatbot.chat(message))