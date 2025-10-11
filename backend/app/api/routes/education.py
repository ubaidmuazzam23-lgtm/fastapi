from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.education_service import EducationService
from app.services.sarvam_voice_service import SarvamVoiceService

router = APIRouter(prefix="/education", tags=["education"])

# Local dependency to extract clerk_user_id from authenticated user
async def get_clerk_user_id(current_user: User = Depends(get_current_user)) -> str:
    return current_user.clerk_user_id

class ChatMessage(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    language_code: Optional[str] = "en"  # Changed from "hi" to "en"

class VoiceChatRequest(BaseModel):
    audio_base64: str
    language_code: Optional[str] = "hi"
    conversation_history: Optional[List[Dict[str, str]]] = None

@router.post("/chat")
async def chat_with_education_bot(
    request: ChatMessage,
    clerk_user_id: str = Depends(get_clerk_user_id)
) -> Dict[str, Any]:
    """
    Text-based chat (with language support)
    """
    try:
        response = await EducationService.get_financial_education_response(
            user_question=request.message,
            clerk_user_id=clerk_user_id,
            conversation_history=request.conversation_history,
            language_code=request.language_code
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/voice-chat")
async def voice_chat_with_bot(
    request: VoiceChatRequest,
    clerk_user_id: str = Depends(get_clerk_user_id)
) -> Dict[str, Any]:
    """
    Voice-based chat with multilingual support
    """
    try:
        print(f"\n{'='*50}")
        print(f"🎙️ Voice Chat Request Received")
        print(f"Language: {request.language_code}")
        print(f"Audio data length: {len(request.audio_base64) if request.audio_base64 else 0}")
        print(f"{'='*50}\n")
        
        # Validate input
        if not request.audio_base64:
            raise HTTPException(status_code=400, detail="No audio data provided")
        
        # Step 1: Convert speech to text
        print("Step 1: Converting speech to text...")
        stt_result = await SarvamVoiceService.speech_to_text(
            request.audio_base64,
            request.language_code
        )
        
        if not stt_result.get("success"):
            error_msg = stt_result.get("error", "Unknown error")
            print(f"❌ STT Failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        user_text = stt_result.get("text", "")
        detected_language = stt_result.get("language", request.language_code)
        
        print(f"✅ STT Success: '{user_text}'")
        print(f"🌍 Detected language: {detected_language}")
        
        if not user_text or not user_text.strip():
            raise HTTPException(status_code=400, detail="Could not understand audio. Please try again.")
        
        # Step 2: Get text response IN THE SAME LANGUAGE
        print(f"Step 2: Getting AI response in {detected_language}...")
        text_response = await EducationService.get_financial_education_response(
            user_question=user_text,
            clerk_user_id=clerk_user_id,
            conversation_history=request.conversation_history,
            language_code=detected_language
        )
        
        if not text_response.get("success"):
            raise HTTPException(status_code=500, detail="Failed to get AI response")
        
        assistant_text = text_response.get("response", "")
        print(f"✅ Got AI response in {detected_language}: {assistant_text[:100]}...")
        
        # Step 3: Convert response to speech in same language
        print(f"Step 3: Converting response to speech in {detected_language}...")
        tts_result = await SarvamVoiceService.text_to_speech(
            text=assistant_text,
            language_code=detected_language
        )
        
        # Return response (with or without audio)
        response_data = {
            "success": True,
            "user_text": user_text,
            "response_text": assistant_text,
            "language": detected_language,
            "language_name": stt_result.get("language_name"),
            "audio_available": tts_result.get("success", False),
            "timestamp": text_response.get("timestamp"),
            "used_financial_data": text_response.get("used_financial_data", False),
            "is_loan_recommendation": text_response.get("is_loan_recommendation", False)
        }
        
        if tts_result.get("success"):
            response_data["response_audio_base64"] = tts_result.get("audio_base64")
            print(f"✅ TTS Success - Audio included in response in {detected_language}")
        else:
            response_data["tts_error"] = tts_result.get("error")
            print(f"⚠️ TTS Failed but continuing: {tts_result.get('error')}")
        
        if text_response.get("is_loan_recommendation"):
            response_data["loan_data"] = text_response.get("loan_data")
        
        print(f"\n{'='*50}")
        print(f"✅ Voice Chat Complete in {detected_language}")
        print(f"{'='*50}\n")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ Voice Chat Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Voice chat error: {str(e)}")

@router.post("/text-to-speech")
async def convert_text_to_speech(
    text: str,
    language_code: str = "hi"
) -> Dict[str, Any]:
    """Convert any text to speech"""
    try:
        result = await SarvamVoiceService.text_to_speech(text, language_code)
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

@router.get("/supported-languages")
async def get_supported_languages() -> Dict[str, Any]:
    """Get list of supported languages for voice"""
    return {
        "success": True,
        "languages": [
            {"code": "hi", "name": "Hindi", "native": "हिंदी"},
            {"code": "mr", "name": "Marathi", "native": "मराठी"},
            {"code": "ta", "name": "Tamil", "native": "தமிழ்"},
            {"code": "te", "name": "Telugu", "native": "తెలుగు"},
            {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ"},
            {"code": "gu", "name": "Gujarati", "native": "ગુજરાતી"},
            {"code": "bn", "name": "Bengali", "native": "বাংলা"},
            {"code": "ml", "name": "Malayalam", "native": "മലയാളം"},
            {"code": "pa", "name": "Punjabi", "native": "ਪੰਜਾਬੀ"},
            {"code": "en", "name": "English", "native": "English"},
            {"code": "od", "name": "Odia", "native": "ଓଡ଼ିଆ"}
        ]
    }

@router.get("/suggested-topics")
async def get_suggested_topics() -> Dict[str, Any]:
    """Existing endpoint - UNCHANGED"""
    try:
        topics = await EducationService.get_suggested_topics()
        return {"success": True, "topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/history")
async def get_chat_history(
    limit: int = 20,
    clerk_user_id: str = Depends(get_clerk_user_id)
) -> Dict[str, Any]:
    """Existing endpoint - UNCHANGED"""
    try:
        history = await EducationService.get_chat_history(clerk_user_id, limit)
        return {"success": True, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")