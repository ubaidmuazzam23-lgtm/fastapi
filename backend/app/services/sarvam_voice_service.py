"""
Sarvam AI Voice Service for multilingual voice input/output
"""
import httpx
import base64
import io
from typing import Optional, Dict, Any
from app.config.settings import settings

class SarvamVoiceService:
    """Service to handle Sarvam AI voice operations"""
    
    BASE_URL = "https://api.sarvam.ai"
    
    # Language codes supported by Sarvam
    SUPPORTED_LANGUAGES = {
        'hi-IN': 'hindi',
        'mr-IN': 'marathi',
        'ta-IN': 'tamil',
        'te-IN': 'telugu',
        'kn-IN': 'kannada',
        'gu-IN': 'gujarati',
        'bn-IN': 'bengali',
        'ml-IN': 'malayalam',
        'pa-IN': 'punjabi',
        'en-IN': 'english',
        'od-IN': 'odia',
        # Backward compatibility
        'hi': 'hindi',
        'mr': 'marathi',
        'ta': 'tamil',
        'te': 'telugu',
        'kn': 'kannada',
        'gu': 'gujarati',
        'bn': 'bengali',
        'ml': 'malayalam',
        'pa': 'punjabi',
        'en': 'english',
        'od': 'odia'
    }
    
    @staticmethod
    def _normalize_language_code(language_code: str) -> str:
        """
        Normalize language code to Sarvam API format (xx-IN)
        
        Args:
            language_code: Language code (hi or hi-IN)
            
        Returns:
            Normalized code (hi-IN)
        """
        if '-IN' in language_code:
            return language_code
        
        lang_map = {
            'hi': 'hi-IN',
            'mr': 'mr-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'kn': 'kn-IN',
            'gu': 'gu-IN',
            'bn': 'bn-IN',
            'ml': 'ml-IN',
            'pa': 'pa-IN',
            'en': 'en-IN',
            'od': 'od-IN'
        }
        
        return lang_map.get(language_code, 'en-IN')  # Default to English
    
    @staticmethod
    def _check_api_key():
        """Check if Sarvam API key is configured"""
        if not settings.SARVAM_API_KEY:
            raise ValueError("Sarvam API key not configured. Please add SARVAM_API_KEY to your .env file")
    
    @staticmethod
    async def speech_to_text(
        audio_base64: str,
        language_code: str = 'en'
    ) -> Dict[str, Any]:
        """
        Convert speech to text using Sarvam AI
        
        Args:
            audio_base64: Base64 encoded audio file (webm format from browser)
            language_code: Language code selected by user (en, hi, mr, etc.)
            
        Returns:
            Dict with transcribed text and language
        """
        try:
            SarvamVoiceService._check_api_key()
            
            # Normalize language code
            normalized_lang = SarvamVoiceService._normalize_language_code(language_code)
            
            if not audio_base64:
                return {
                    "success": False,
                    "error": "No audio data provided"
                }
            
            print(f"🎤 Sarvam STT: Converting audio to text in {normalized_lang}...")
            print(f"🔑 API Key present: {bool(settings.SARVAM_API_KEY)}")
            print(f"📦 Audio data length: {len(audio_base64)}")
            
            try:
                audio_bytes = base64.b64decode(audio_base64)
                print(f"✅ Audio decoded, size: {len(audio_bytes)} bytes")
            except Exception as e:
                print(f"❌ Failed to decode audio: {str(e)}")
                return {
                    "success": False,
                    "error": f"Invalid audio data: {str(e)}"
                }
            
            audio_file = io.BytesIO(audio_bytes)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {
                    'file': ('audio.webm', audio_file, 'audio/webm')
                }
                data = {
                    'language_code': normalized_lang,
                    'model': 'saarika:v2'
                }
                headers = {
                    'api-subscription-key': settings.SARVAM_API_KEY
                }
                
                response = await client.post(
                    f"{SarvamVoiceService.BASE_URL}/speech-to-text",
                    headers=headers,
                    files=files,
                    data=data
                )
                
                print(f"📡 Sarvam STT Response: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    transcript = data.get("transcript", "")
                    
                    print(f"✅ Transcription successful: {transcript[:50]}...")
                    print(f"🌐 Language used: {normalized_lang}")
                    
                    return {
                        "success": True,
                        "text": transcript,
                        "language": normalized_lang,
                        "language_name": SarvamVoiceService.SUPPORTED_LANGUAGES.get(normalized_lang, "english")
                    }
                else:
                    error_text = response.text
                    print(f"❌ Sarvam STT Error: {response.status_code} - {error_text}")
                    return {
                        "success": False,
                        "error": f"Speech recognition failed: {error_text}"
                    }
                    
        except ValueError as ve:
            print(f"⚠️  Configuration Error: {str(ve)}")
            return {
                "success": False,
                "error": str(ve)
            }
        except httpx.TimeoutException:
            print(f"⏱️  Sarvam STT Timeout")
            return {
                "success": False,
                "error": "Speech recognition timed out. Please try again."
            }
        except Exception as e:
            print(f"❌ Sarvam STT Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Speech recognition error: {str(e)}"
            }
    
    @staticmethod
    async def text_to_speech(
        text: str,
        language_code: str = 'en',
        speaker: str = "meera"
    ) -> Dict[str, Any]:
        """
        Convert text to speech using Sarvam AI
        
        Args:
            text: Text to convert to speech
            language_code: Language code (en, hi, mr, etc.)
            speaker: Voice speaker name
            
        Returns:
            Dict with base64 encoded audio
        """
        try:
            SarvamVoiceService._check_api_key()
            
            # Normalize language code
            normalized_lang = SarvamVoiceService._normalize_language_code(language_code)
            
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "No text provided"
                }
            
            print(f"🔊 Sarvam TTS: Converting text to speech in {normalized_lang}...")
            print(f"📝 Text length: {len(text)} chars")
            print(f"📝 Text preview: {text[:100]}...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{SarvamVoiceService.BASE_URL}/text-to-speech",
                    headers={
                        "api-subscription-key": settings.SARVAM_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "inputs": [text],
                        "target_language_code": normalized_lang,
                        "speaker": speaker,
                        "model": "bulbul:v1",
                        "enable_preprocessing": True
                    }
                )
                
                print(f"📡 Sarvam TTS Response: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    audio_data = data.get("audios", [""])[0] if data.get("audios") else ""
                    
                    if not audio_data:
                        print(f"⚠️  TTS returned empty audio")
                        return {
                            "success": False,
                            "error": "Text to speech returned empty audio"
                        }
                    
                    print(f"✅ TTS successful, audio length: {len(audio_data)} chars")
                    
                    return {
                        "success": True,
                        "audio_base64": audio_data,
                        "language": normalized_lang
                    }
                else:
                    error_text = response.text
                    print(f"❌ Sarvam TTS Error: {response.status_code} - {error_text}")
                    return {
                        "success": False,
                        "error": f"Text to speech failed: {error_text}"
                    }
                    
        except ValueError as ve:
            print(f"⚠️  Configuration Error: {str(ve)}")
            return {
                "success": False,
                "error": str(ve)
            }
        except httpx.TimeoutException:
            print(f"⏱️  Sarvam TTS Timeout")
            return {
                "success": False,
                "error": "Text to speech timed out. Please try again."
            }
        except Exception as e:
            print(f"❌ Sarvam TTS Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Text to speech error: {str(e)}"
            }
    
    @staticmethod
    async def detect_language(audio_base64: str) -> Optional[str]:
        """
        Detect language from audio (not used - manual selection preferred)
        """
        result = await SarvamVoiceService.speech_to_text(audio_base64, "en")
        if result.get("success"):
            return result.get("language")
        return None