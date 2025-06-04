import os
from transformers import MarianMTModel, MarianTokenizer
import torch
from dotenv import load_dotenv
from typing import Optional
import logging

logging.basicConfig(
    filename="translation_accuracy.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


load_dotenv()

class KalenjinTranslator:
    def __init__(self, model_name: str = "tketer/kalenjin-translator", hf_token: Optional[str] = None):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.hf_token = hf_token or self._get_hf_token()
        self._load_model()

    def _get_hf_token(self) -> str:
        """Retrieve and validate Hugging Face token from environment"""
        token = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError(
                "Hugging Face token not found. "
                "Set HF_TOKEN in .env or pass directly to constructor"
            )
        if not token.startswith("hf_"):
            raise ValueError("Invalid token format - must start with 'hf_'")
        return token

    def _load_model(self):
        """Initialize model with error handling"""
        try:
            self.model = MarianMTModel.from_pretrained(
                self.model_name,
                token=self.hf_token
            ).to(self.device)
            self.tokenizer = MarianTokenizer.from_pretrained(
                self.model_name,
                token=self.hf_token
            )
        except Exception as e:
            raise RuntimeError(f"Model loading failed: {str(e)}")

    def translate(self, text: str, expected_translation: str = None) -> str:
        """Translate text and log accuracy if expected translation is provided"""

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input must be a non-empty string")

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        outputs = self.model.generate(**inputs)
        translated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Log translation accuracy if expected output is provided
        if expected_translation:
            is_correct = translated_text.strip().lower() == expected_translation.strip().lower()
            logger.info(f"Source: {text} | Translated: {translated_text} | Expected: {expected_translation} | Correct: {is_correct}")

        return translated_text


    def translate_batch(self, texts: list[str], expected_translations: list[str] = None) -> list[str]:
        """Batch translation with accuracy logging"""

        inputs = self.tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512).to(self.device)
        outputs = self.model.generate(**inputs)
        translated_texts = [self.tokenizer.decode(out, skip_special_tokens=True) for out in outputs]

        # Log translation accuracy if expected outputs are provided
        if expected_translations:
            for src, translated, expected in zip(texts, translated_texts, expected_translations):
                is_correct = translated.strip().lower() == expected.strip().lower()
                logger.info(f"Source: {src} | Translated: {translated} | Expected: {expected} | Correct: {is_correct}")

        return translated_texts


# Initialize with fallback
try:
    translator = KalenjinTranslator()
except Exception as e:
    print(f"Warning: {str(e)}")
    translator = KalenjinTranslator(hf_token="your_fallback_token_here")
