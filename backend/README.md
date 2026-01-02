# PROJECT-VICTUS Backend

The core intelligence engine of the PROJECT-VICTUS platform. Built with FastAPI, it orchestrates AI agent execution, manages system tools, handles RAG operations, and provides secure authentication.

## 🚀 Technologies

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **Dependency Management**: [Poetry](https://python-poetry.org/)
- **Database**:
  - **Relational**: SQLite (Dev) / PostgreSQL (Prod) via [SQLAlchemy](https://www.sqlalchemy.org/)
  - **Vector**: FAISS (for RAG)
- **AI Core**:
  - [LangChain](https://langchain.com/)
  - OpenAI GPT-4o
- **ASR/TTS**: Faster-Whisper, Piper TTS

## ✨ Key Capabilities

- **Agent Orchestrator**: Manages tool selection, planning, and execution loops.
- **RAG Engine**: Semantic search over uploaded documents using FAISS.
- **Security**: JWT Authentication, OAuth 2.0 (Google, Microsoft), and RBAC.
- **M365 Integration**: Deep integration with Outlook and Calendar via Graph API.
- **System Tools**: OS-level control (File system, Clipboard, Screenshots).
- **Observability**: Comprehensive tracing and logging system.

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.11+
- Poetry
- ffmpeg (for audio processing)

### Installation

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

### Configuration

Create a `.env` file in the `backend/` directory (see `.env.example` or root documentation for keys):

```env
DATABASE_URL=sqlite:///./victus.db
OPENAI_API_KEY=sk-...
SECRET_KEY=...
# ... other keys
```

### Database Setup

Initialize the database using Alembic:

```bash
poetry run alembic upgrade head
```

### Running the Server

Start the application with hot-reload enabled:

```bash
poetry run uvicorn src.main:app --reload --port 8000
```

Documentation will be available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📁 Project Structure

```
src/
├── api/              # API Route Handlers
├── auth/             # Authentication & Security
├── models/           # SQLAlchemy Database Models
├── services/         # Business Logic (RAG, Email, etc.)
├── tools/            # Agent Tools (Search, System, M365)
├── utils/            # Utilities (Logging, Metrics)
├── agent.py          # Legacy Agent Entry (moving to Orchestrator)
├── database.py       # Database Session Management
└── main.py           # Application Entry Point
```

## 🧪 Testing

Run tests with Pytest:

```bash
poetry run pytest
```

## 📦 Deployment

The application is container-ready. Use the `Dockerfile` in the root (or `backend/Dockerfile` if separated) to build the image.

```bash
docker build -t victus-backend .
```
