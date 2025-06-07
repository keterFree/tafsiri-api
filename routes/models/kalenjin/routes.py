from fastapi import APIRouter, HTTPException
from models import TranslationRequest, TranslationResponse
from routes.models.kalenjin.translator import KalenjinTranslator


router = APIRouter()
translator = KalenjinTranslator()

@router.post("/kalenjintranslate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Input text cannot be empty")

        translated_text = translator.translate(request.text)
        return TranslationResponse(
            translated_text=translated_text,
            source_lang="English",
            target_lang="Kalenjin"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Translation error: {str(e)}"
        )