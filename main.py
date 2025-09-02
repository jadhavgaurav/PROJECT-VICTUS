# main.py - UPDATED

import os
import shutil
import uuid
import asyncio # NEW: For running blocking code in a thread
import traceback # NEW: For better error logging
from contextlib import asynccontextmanager # NEW: For modern startup/shutdown events

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request, BackgroundTasks # UPDATED
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import FileResponse, JSONResponse
from langchain_core.messages import HumanMessage, AIMessage

# Local Imports
import models
from database import engine, get_db
from agent import create_agent_executor
from tools import update_vector_store, FAISS_INDEX_PATH
from auth import is_authenticated

# Initialize Database
models.Base.metadata.create_all(bind=engine)

# Lifespan manager for loading models on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load all necessary models and the agent when the application starts.
    This is much more efficient than loading them on each request.
    """
    print("--- Application Startup ---")
    # Load Speech-to-Text Model
    from faster_whisper import WhisperModel
    print("Loading STT model (faster-whisper)...")
    app.state.stt_model = WhisperModel("base.en", device="cpu", compute_type="int8")
    print("STT model loaded.")

    # Load Text-to-Speech Model
    from piper import PiperVoice
    model_path = next((os.path.join("models", f) for f in os.listdir("models") if f.endswith(".onnx")), None)
    if not model_path:
        raise RuntimeError("Could not find a .onnx model file in the /models directory.")
    print(f"Loading TTS model ({model_path})...")
    app.state.tts_model = PiperVoice.load(model_path)
    print("TTS model loaded.")

    # Create a reusable Agent Executor
    # We will create a new one per request if RAG status changes, but can reuse this.
    print("Creating initial Agent Executor...")
    app.state.agent_executor = create_agent_executor(rag_enabled=False) # Start with RAG disabled
    print("Initial Agent Executor created.")
    print("--- Application Ready ---")
    
    yield # The application is now running

    # --- Shutdown logic can go here if needed ---
    print("--- Application Shutdown ---")


app = FastAPI(title="Project VICTUS", lifespan=lifespan) # UPDATED

# Mount static files (for frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Pydantic Models for requests
class ChatRequest(BaseModel):
    message: str
    session_id: str

class HistoryRequest(BaseModel):
    session_id: str

# API Endpoints
@app.get("/healthz")
async def health_check():
    """A simple endpoint to confirm the server is running."""
    return {"status": "ok"}

@app.post("/api/history")
async def get_history(request: HistoryRequest, db: Session = Depends(get_db)):
    history = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == request.session_id).order_by(models.ChatMessage.timestamp).all()
    if not history:
        welcome_message = {"message": "Hello! I'm VICTUS, your personal AI assistant. How can I help you today?", "sender": "ai"}
        return {"history": [welcome_message]}
    history_list = [{"message": msg.message, "sender": msg.sender} for msg in history]
    return {"history": history_list}

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.post("/api/chat")
async def chat_endpoint(request: Request, db: Session = Depends(get_db)): 
    chat_request: ChatRequest = await request.json()
    chat_request = ChatRequest.parse_obj(chat_request)

    # Re-create agent only if RAG status changes. More efficient.
    rag_enabled = os.path.exists(FAISS_INDEX_PATH) and bool(os.listdir(FAISS_INDEX_PATH))
    agent_executor = create_agent_executor(rag_enabled=rag_enabled)

    history = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == chat_request.session_id).order_by(models.ChatMessage.timestamp).all()
    chat_history_messages = [HumanMessage(content=msg.message) if msg.sender == "user" else AIMessage(content=msg.message) for msg in history]

    db_user_msg = models.ChatMessage(session_id=chat_request.session_id, message=chat_request.message, sender="user")
    db.add(db_user_msg)
    db.commit()

    try:
        response = await agent_executor.ainvoke({ # async invoke
            "input": chat_request.message,
            "chat_history": chat_history_messages
        })
        final_response = response.get("output", "I encountered an error processing your request.")
    except Exception as e:
        print("--- AGENT INVOCATION ERROR ---")
        traceback.print_exc()
        print("----------------------------")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

    db_ai_msg = models.ChatMessage(session_id=chat_request.session_id, message=final_response, sender="ai")
    db.add(db_ai_msg)
    db.commit()

    return {"response": final_response}

@app.post("/api/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)): # UPDATED
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF or DOCX.")
    
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # The server responds to the user immediately.
    background_tasks.add_task(update_vector_store, file_path)

    return {"status": "success", "filename": file.filename, "detail": "File received and is being processed in the background."}

@app.post("/api/transcribe")
async def transcribe_audio(request: Request, file: UploadFile = File(...)): # UPDATED
    try:
        stt_model = request.app.state.stt_model
        audio_bytes = await file.read()
        
        def run_transcription():
            segments, _ = stt_model.transcribe(audio_bytes, beam_size=5)
            return " ".join([segment.text for segment in segments])

        transcription = await asyncio.to_thread(run_transcription)
        return {"transcription": transcription}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {e}")

@app.post("/api/synthesize")
async def synthesize_speech(request: Request): # UPDATED
    try:
        body = await request.json()
        text = body.get('text')
        if not text:
            raise HTTPException(status_code=400, detail="No text provided for synthesis.")
        
        tts_model = request.app.state.tts_model
        output_dir = "static/audio"
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(output_dir, output_filename)

        # UPDATED: Run the blocking, CPU-bound synthesize function in a thread pool
        def run_synthesis():
            with open(output_path, "wb") as wav_file:
                tts_model.synthesize(text, wav_file)
        
        await asyncio.to_thread(run_synthesis)
        
        return {"audio_url": f"/static/audio/{output_filename}"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error synthesizing speech: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)