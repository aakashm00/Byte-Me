from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import base64
import json
import sys
import os
import openai
import dotenv

# Add the ai-agent-service path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'service', 'ai-agent-service'))

from agent import AsyncOCRChatbot

# Load environment variables
dotenv.load_dotenv()

router = APIRouter()

# Initialize OCR chatbot once
ocr_chatbot = AsyncOCRChatbot()

class CameraCaptureRequest(BaseModel):
    """For camera capture (base64 image)"""
    image: str
    message: str = "What text is in this image?"

@router.get("/")
async def read_root():
    return {"message": "Welcome to the OCR FastAPI project!"}

@router.post("/ocr/camera")
async def process_camera_capture(request: CameraCaptureRequest):
    """
    Process image from camera capture (base64)
    """
    try:
        response = await ocr_chatbot.process_camera_scan(request.image, request.message)
        
        return {
            "type": "ocr_result",
            "response": response,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing camera capture: {str(e)}")

@router.post("/ocr/upload")
async def process_file_upload(
    file: UploadFile = File(...),
    message: str = "What text is in this image?"
):
    """
    Process uploaded image file
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file and convert to base64
        file_content = await file.read()
        base64_image = base64.b64encode(file_content).decode('utf-8')
        base64_with_prefix = f"data:{file.content_type};base64,{base64_image}"
        
        # Process with OCR
        response = await ocr_chatbot.process_camera_scan(base64_with_prefix, message)
        
        return {
            "type": "ocr_result", 
            "response": response,
            "status": "success",
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

@router.post("/chat")
async def chat_message(message: str):
    """
    Chat without image
    """
    try:
        response = await ocr_chatbot.chat(message)
        
        return {
            "type": "chat_response",
            "response": response, 
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

@router.post("/tts")
async def text_to_speech(text: str):
    """
    Convert text to speech using OpenAI TTS
    """
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        return StreamingResponse(
            iter([response.content]),
            media_type="audio/mpeg"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check"""
    return {"status": "OCR service running", "chatbot": "ready"}