import os
import shutil
import uuid
import soundfile as sf
import numpy as np
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import FileResponse, JSONResponse
from langchain_core.messages import HumanMessage, AIMessage


import models
from database import engine, get_db
from agent import create_agent_executor
from tools import update_vector_store, FAISS_INDEX_PATH
from auth import is_authenticated

# Initialize Database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project VICTUS")

# Mount static files (for frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Voice Model Loading (Lazy Load) ---
stt_model = None
tts_model = None

def get_stt_model():
    global stt_model
    if stt_model is None:
        from faster_whisper import WhisperModel
        # This will download the model on first use
        print("Loading STT model (faster-whisper)...")
        stt_model = WhisperModel("base.en", device="cpu", compute_type="int8")
        print("STT model loaded.")
    return stt_model

def get_tts_model():
    global tts_model
    if tts_model is None:
        from piper import PiperVoice
        # Find the .onnx file in the models directory
        model_path = None
        for file in os.listdir("models"):
            if file.endswith(".onnx"):
                model_path = os.path.join("models", file)
                break
        if not model_path:
            raise RuntimeError("Could not find a .onnx model file in the /models directory.")
        print(f"Loading TTS model ({model_path})...")
        tts_model = PiperVoice.load(model_path)
        print("TTS model loaded.")
    return tts_model


class ChatRequest(BaseModel):
    message: str
    session_id: str

# ==============================================================================
# === NEW HISTORY ENDPOINT ===
# ==============================================================================
class HistoryRequest(BaseModel):
    session_id: str

@app.get("/healthz")
async def health_check():
    """A simple endpoint to confirm the server is running."""
    return {"status": "ok"}


@app.post("/api/history")
async def get_history(request: HistoryRequest, db: Session = Depends(get_db)):
    history = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == request.session_id).order_by(models.ChatMessage.timestamp).all()
    
    if not history:
        # If there's no history, create and return the welcome message
        welcome_message = {"message": "Hello! I'm VICTUS, your personal AI assistant. How can I help you today?", "sender": "ai"}
        return {"history": [welcome_message]}
        
    # Otherwise, return the existing history
    history_list = [{"message": msg.message, "sender": msg.sender} for msg in history]
    return {"history": history_list}
# ==============================================================================



@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    rag_enabled = os.path.exists(FAISS_INDEX_PATH) and bool(os.listdir(FAISS_INDEX_PATH))

    # The flawed check is removed. The agent is now always created with all tools.
    agent_executor = create_agent_executor(rag_enabled=rag_enabled)

    # Load and translate chat history from the database
    history = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == request.session_id).order_by(models.ChatMessage.timestamp).all()
    chat_history_messages = []
    for msg in history:
        if msg.sender == "user":
            chat_history_messages.append(HumanMessage(content=msg.message))
        elif msg.sender == "ai":
            chat_history_messages.append(AIMessage(content=msg.message))

    # Save the new user message to the database
    db_user_msg = models.ChatMessage(session_id=request.session_id, message=request.message, sender="user")
    db.add(db_user_msg)
    db.commit()

    try:
        # Invoke the AgentExecutor with the correct dictionary input
        response = agent_executor.invoke({
            "input": request.message,
            "chat_history": chat_history_messages
        })
        # Extract the final output from the response dictionary
        final_response = response.get("output", "I encountered an error processing your request.")
    except Exception as e:
        print(f"Agent invocation error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

    # Save the AI's final response to the database
    db_ai_msg = models.ChatMessage(session_id=request.session_id, message=final_response, sender="ai")
    db.add(db_ai_msg)
    db.commit()

    return {"response": final_response}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF or DOCX.")
    
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process and index the document
        update_vector_store(file_path)

        return {"status": "success", "filename": file.filename, "detail": "File processed and indexed."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        stt = get_stt_model()
        # Read the audio file in memory
        audio_bytes = await file.read()
        segments, _ = stt.transcribe(audio_bytes, beam_size=5)
        transcription = " ".join([segment.text for segment in segments])
        return {"transcription": transcription}
    except Exception as e:
        print(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {e}")


@app.post("/api/synthesize")
async def synthesize_speech(request: Request):
    try:
        body = await request.json()
        text = body.get('text')
        if not text:
            raise HTTPException(status_code=400, detail="No text provided for synthesis.")
        
        tts = get_tts_model()
        output_dir = "static/audio"
        os.makedirs(output_dir, exist_ok=True)
        # Use a unique filename to avoid browser caching issues
        output_filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, "wb") as wav_file:
            tts.synthesize(text, wav_file)
        
        # Return the URL to the generated audio
        return {"audio_url": f"/static/audio/{output_filename}"}
    except Exception as e:
        print(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"Error synthesizing speech: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)