"""
Voice processing endpoints (transcription and synthesis)
"""

import os
import uuid
import asyncio
import traceback
from fastapi import APIRouter, Request, UploadFile, File, HTTPException, status
from ..utils.logging import get_logger
from ..utils.security import validate_input

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Voice"])


@router.post("/transcribe")
async def transcribe_audio(request: Request, file: UploadFile = File(...)):
    """Transcribe audio to text using Whisper."""
    if not hasattr(request.app.state, 'stt_model') or request.app.state.stt_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech-to-text model not available"
        )
    
    try:
        stt_model = request.app.state.stt_model
        audio_bytes = await file.read()
        
        def run_transcription():
            segments, _ = stt_model.transcribe(audio_bytes, beam_size=5)
            return " ".join([segment.text for segment in segments])

        transcription = await asyncio.to_thread(run_transcription)
        return {"transcription": transcription}
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transcribing audio: {e}"
        )


@router.post("/synthesize")
async def synthesize_speech(request: Request):
    """Synthesize text to speech using Piper."""
    if not hasattr(request.app.state, 'tts_model') or request.app.state.tts_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Text-to-speech model not available"
        )
    
    try:
        body = await request.json()
        text = body.get('text')
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text provided for synthesis."
            )
        
        # Validate input
        text = validate_input(text, max_length=5000)
        
        tts_model = request.app.state.tts_model
        output_dir = "static/audio"
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(output_dir, output_filename)

        def run_synthesis():
            with open(output_path, "wb") as wav_file:
                tts_model.synthesize(text, wav_file)
        
        await asyncio.to_thread(run_synthesis)
        
        return {"audio_url": f"/static/audio/{output_filename}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error synthesizing speech: {e}"
        )

