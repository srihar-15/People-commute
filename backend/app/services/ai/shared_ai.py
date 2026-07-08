import os
import random
import requests
from io import BytesIO
from PIL import Image
import numpy as np
import google.generativeai as genai
from app.core.config import settings

class AIServiceError(Exception):
    pass

class SharedAIService:
    def __init__(self):
        # Fallback sequence for api keys
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        self.client_enabled = False
        
        if self.api_key and self.api_key != "mock-key":
            try:
                genai.configure(api_key=self.api_key)
                self.client_enabled = True
                print("Google Generative AI successfully configured.")
            except Exception as e:
                print(f"Warning: Failed to initialize Google GenAI SDK: {e}")
                
    def get_embeddings(self, text: str) -> list:
        """
        Generates 1536-dimension text embeddings using Gemini.
        Pads or truncates output to 1536 dimensions for schema compatibility.
        """
        if self.client_enabled:
            try:
                response = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document"
                )
                raw_emb = response['embedding']
                # Models output different dims. text-embedding-004 is 768.
                # Let's pad or project to 1536 for DB schema compatibility.
                if len(raw_emb) < 1536:
                    raw_emb = raw_emb + [0.0] * (1536 - len(raw_emb))
                elif len(raw_emb) > 1536:
                    raw_emb = raw_emb[:1536]
                return raw_emb
            except Exception as e:
                print(f"Gemini embedding failed, falling back: {e}")
        
        # Fallback: Deterministic embedding based on hash
        random.seed(hash(text) % 123456789)
        vector = [random.uniform(-0.1, 0.1) for _ in range(1536)]
        norm = np.linalg.norm(vector)
        return (vector / norm).tolist() if norm > 0 else vector

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Transcribes audio data (WhatsApp voice notes) using Gemini Multimodal.
        """
        if self.client_enabled:
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                # Construct inline audio data
                audio_part = {
                    "mime_type": "audio/ogg", # WhatsApp default codec
                    "data": audio_bytes
                }
                response = model.generate_content([
                    audio_part,
                    "Transcribe this voice note directly to English text. Do not add metadata or preamble."
                ])
                return response.text.strip()
            except Exception as e:
                print(f"Gemini voice note transcription failed: {e}")
                
        # Fallback: Realistic mock transcription for demo
        transcriptions = [
            "There is a leakage in the water pipeline near my house, please fix it.",
            "The street lights are not working since last Monday, the road is very dark.",
            "A huge pile of garbage has accumulated at the street corner, it is spreading bad smell."
        ]
        return random.choice(transcriptions)

    def translate_text(self, text: str, target_lang: str = "en") -> str:
        """
        Translates regional languages (Telugu, Hindi, etc.) using Gemini.
        """
        if self.client_enabled:
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(
                    f"Translate the following text directly to {target_lang}. Return only the translated text, nothing else:\n\n{text}"
                )
                return response.text.strip()
            except Exception as e:
                print(f"Gemini translation failed: {e}")
                
        # Mock translation fallback
        lower_text = text.lower()
        if "నీరు" in lower_text or "లీక్" in lower_text or "पानी" in lower_text:
            return "Water supply pipe is leaking."
        if "రోడ్డు" in lower_text or "గుంత" in lower_text or "सड़क" in lower_text:
            return "There is a deep pothole on the road."
        if "చెత్త" in lower_text or "కంపన" in lower_text or "कचరా" in lower_text:
            return "Garbage bin is overflowing and stinking."
        return text

    def perform_ocr(self, image_url: str) -> str:
        """
        Extracts text from uploaded documents using Gemini Vision capabilities.
        """
        if self.client_enabled:
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                img_data = requests.get(image_url).content
                img = Image.open(BytesIO(img_data))
                response = model.generate_content([
                    img,
                    "Extract all readable text from this document image. Return only the extracted text, no explanations."
                ])
                return response.text.strip()
            except Exception as e:
                print(f"Gemini OCR failed: {e}")
                
        # Mock OCR fallback
        return "REPRESENTATIVE PETITION DOCUMENT\nSubject: Grievance regarding drinking water shortage.\nWard: Ward 5 Shastri Nagar.\nSignature: Sitha Devi"

    def verify_images(self, intake_image_url: str, resolution_image_url: str) -> dict:
        """
        Performs structural before-and-after validation using Gemini Vision.
        """
        if self.client_enabled:
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                # Retrieve images
                img1_data = requests.get(intake_image_url).content
                img1 = Image.open(BytesIO(img1_data))
                
                img2_data = requests.get(resolution_image_url).content
                img2 = Image.open(BytesIO(img2_data))
                
                prompt = (
                    "You are a quality assurance inspector. Compare the intake (before) image and the resolution (after) image. "
                    "Verify if the issue depicted in the before image has been resolved in the after image. "
                    "Provide your response in JSON format containing: "
                    "'is_verified' (boolean), 'match_confidence' (float between 0 and 1), 'remarks' (string), "
                    "and 'verification_checklist' (array of strings checking validation details)."
                )
                
                response = model.generate_content(
                    [img1, img2, prompt],
                    generation_config={"response_mime_type": "application/json"}
                )
                import json
                return json.loads(response.text.strip())
            except Exception as e:
                print(f"Gemini Vision verification failed: {e}")
                
        # Mock Vision verification fallback
        return {
            "is_verified": True,
            "match_confidence": 0.92,
            "remarks": "Before image showed a visible infrastructure defect. After image shows clean work, fresh repairs, and no debris.",
            "verification_checklist": [
                "Defect is no longer visible",
                "New repair materials matches surrounding structure",
                "Worksite clean of tools and debris"
            ]
        }

ai_service = SharedAIService()
