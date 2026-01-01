# Project VICTUS

<div align="center">

**An advanced, voice-enabled, conversational AI personal assistant built for seamless productivity and system control.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Project VICTUS is a production-ready AI personal assistant that combines advanced language understanding with practical system integration capabilities. Built on modern Python frameworks and leveraging state-of-the-art AI models, VICTUS provides a seamless interface for managing tasks, documents, communications, and system operations through natural language interactions.

### Key Capabilities

- **Intelligent Conversation**: Powered by OpenAI's GPT-4o for natural, context-aware interactions
- **Voice Interface**: Real-time speech-to-text and text-to-speech for hands-free operation
- **Document Intelligence**: Upload and query documents using RAG (Retrieval Augmented Generation)
- **System Integration**: Direct control of applications, files, and system operations
- **Productivity Tools**: Email management, calendar scheduling, and task automation via Microsoft 365
- **Persistent Memory**: Maintains conversation history and user preferences across sessions
- **Enterprise Security**: Built-in authentication, rate limiting, and comprehensive security measures

---

## Features

### 🗣️ Voice Interface
- **Speech-to-Text**: Real-time audio transcription using Faster-Whisper
- **Text-to-Speech**: Natural voice synthesis with Piper TTS
- **Low Latency**: Optimized for real-time conversational interactions

### 🧠 Advanced AI Agent
- **Model**: OpenAI GPT-4o for superior reasoning and language understanding
- **Orchestration**: LangChain AgentExecutor for dynamic tool selection and execution
- **Context Awareness**: Maintains conversation context and user preferences
- **Multi-Tool Execution**: Seamlessly chains multiple tools for complex tasks

### 📄 Document Management
- **RAG System**: Upload PDF and DOCX files to a persistent FAISS vector store
- **Intelligent Querying**: Ask questions based on your documents with semantic search
- **Persistent Storage**: Documents remain available across sessions

### 💻 System Tools
- **Application Control**: Dynamically find and launch installed applications
- **File Management**: List, navigate, and manage files and directories
- **Clipboard Access**: Read and interact with clipboard content
- **Screenshot Capture**: Capture and analyze screen content
- **Window Management**: Get active window information and control

### 📧 Microsoft 365 Integration
- **Email Management**: Read, search, and send emails via Outlook
- **Calendar Operations**: Create, read, and manage calendar events
- **Secure Authentication**: OAuth 2.0 with Microsoft Graph API
- **Smart Scheduling**: Weather-aware event creation with intelligent suggestions

### 💾 Persistent Memory
- **Chat History**: Complete conversation history stored in SQLite database
- **User Facts**: Long-term memory for personal preferences and information
- **Session Management**: Maintains context across multiple sessions
- **User Isolation**: Secure, per-user data storage

### 🔒 Security & Authentication
- **JWT Authentication**: Secure token-based authentication
- **OAuth Integration**: Google and Microsoft OAuth support
- **Rate Limiting**: Protection against abuse and excessive requests
- **Input Validation**: Comprehensive sanitization and validation
- **CORS Protection**: Configurable cross-origin resource sharing

### 📊 Observability
- **Structured Logging**: Production-ready logging with file and console output
- **Prometheus Metrics**: HTTP request metrics and agent performance monitoring
- **Health Checks**: Detailed system status and model availability
- **Error Tracking**: Comprehensive error logging and reporting

---

## Architecture

Project VICTUS follows a modular, layered architecture designed for maintainability, scalability, and testability.

### System Architecture

```
project_victus/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── agent.py                # AI agent executor configuration
│   ├── config.py               # Application configuration management
│   ├── database.py             # Database connection and session management
│   ├── models.py               # SQLAlchemy ORM models
│   ├── m365_auth.py            # Microsoft 365 authentication handler
│   │
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic request/response models
│   │   ├── health.py           # Health check and metrics endpoints
│   │   ├── chat.py             # Chat and history endpoints
│   │   ├── documents.py        # Document upload endpoints
│   │   ├── voice.py            # Voice transcription and synthesis
│   │   └── pages.py            # Frontend page serving
│   │
│   ├── auth/                   # Authentication module
│   │   ├── __init__.py
│   │   ├── routes.py           # Authentication endpoints
│   │   ├── dependencies.py    # FastAPI authentication dependencies
│   │   ├── jwt.py              # JWT token management
│   │   └── oauth.py            # OAuth provider integrations
│   │
│   ├── tools/                  # Agent tools module
│   │   ├── __init__.py
│   │   ├── assembler.py        # Tool collection and assembly
│   │   ├── config.py           # Tool configuration and shared resources
│   │   ├── web_search.py       # Web search capabilities
│   │   ├── rag_tools.py        # Document querying and RAG
│   │   ├── system_tools.py     # System operation tools
│   │   ├── m365_tools.py       # Microsoft 365 integration tools
│   │   ├── weather_tool.py     # Weather information retrieval
│   │   └── memory_tools.py     # Long-term memory management
│   │
│   └── utils/                  # Utility modules
│       ├── __init__.py
│       ├── logging.py          # Logging configuration
│       ├── security.py          # Security utilities (CORS, rate limiting)
│       ├── metrics.py           # Prometheus metrics collection
│       └── context.py           # Request context management
│
├── static/                     # Frontend static files
│   ├── index.html              # Main application interface
│   ├── login.html              # Authentication page
│   ├── signup.html             # User registration page
│   ├── style.css               # Application styles
│   ├── auth.css                # Authentication page styles
│   ├── script.js               # Main application logic
│   ├── auth.js                 # Authentication logic
│   └── audio/                  # Generated audio files
│
├── tests/                       # Test suite
│   ├── test_api.py             # API endpoint tests
│   ├── test_agent.py           # Agent functionality tests
│   ├── test_memory_tools.py    # Memory tools tests
│   └── test_metrics.py         # Metrics tests
│
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   └── env.py                  # Alembic environment
│
├── uploads/                     # User-uploaded documents
├── faiss_index/                 # FAISS vector store
├── models/                      # TTS voice models
├── logs/                        # Application logs
│
├── pyproject.toml              # Poetry dependency management
├── alembic.ini                  # Alembic configuration
├── Dockerfile                   # Docker container definition
└── README.md                    # This file
```

### Component Interaction

```
┌─────────────┐
│   Frontend   │
│  (Browser)   │
└──────┬───────┘
       │ HTTP/SSE
       ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌──────────────────────────────┐  │
│  │      API Routes (src/api/)    │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │   Authentication (src/auth/)  │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │   Agent Executor (agent.py)   │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │      Tools (src/tools/)        │  │
│  │  ┌──────────────────────────┐ │  │
│  │  │ System │ M365 │ RAG │ ... │ │  │
│  │  └──────────────────────────┘ │  │
│  └─────────────────────────────────┘  │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   External Services & Databases      │
│  ┌──────────┬──────────┬──────────┐ │
│  │ OpenAI   │ SQLite   │ Microsoft│ │
│  │ Graph    │          │ Graph    │ │
│  └──────────┴──────────┴──────────┘ │
└─────────────────────────────────────┘
```

---

## Tech Stack

### Backend Framework
- **FastAPI**: Modern, high-performance web framework for building APIs
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and settings management

### AI & Machine Learning
- **OpenAI GPT-4o**: Large language model for natural language understanding
- **LangChain**: Framework for building LLM-powered applications
- **FAISS**: Vector similarity search for RAG functionality
- **Faster-Whisper**: Efficient speech-to-text transcription
- **Piper TTS**: Text-to-speech synthesis

### Data & Storage
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Lightweight database for development
- **Alembic**: Database migration management
- **FAISS**: Vector database for document embeddings

### Authentication & Security
- **JWT**: JSON Web Tokens for authentication
- **OAuth 2.0**: Google and Microsoft authentication
- **MSAL**: Microsoft Authentication Library
- **bcrypt**: Password hashing
- **SlowAPI**: Rate limiting middleware

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Structured Logging**: Production-ready logging system

### Development Tools
- **Poetry**: Dependency management and packaging
- **Pytest**: Testing framework
- **Alembic**: Database migrations

### Deployment
- **Docker**: Containerization
- **AWS App Runner**: Cloud deployment platform

---

## Prerequisites

Before installing Project VICTUS, ensure you have the following:

### Required
- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **Poetry**: [Install Poetry](https://python-poetry.org/docs/#installation)

### Optional
- **Docker**: For containerized deployment
- **Conda**: For managing Python environments (recommended for PyTorch)

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Storage**: 2GB free space for models and dependencies
- **Network**: Internet connection for API calls

**Note**: Advanced system tools (`open_app`, `list_files`) are optimized for Windows. Other operating systems may have limited functionality for these features.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/jadhavgaurav/PROJECT-VICTUS.git
cd PROJECT-VICTUS
```

### 2. Set Up Python Environment

#### Using Poetry (Recommended)

```bash
# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

#### Using Conda (Alternative)

```bash
# Create conda environment
conda create -n victus python=3.11
conda activate victus

# Install PyTorch (if needed for voice models)
conda install pytorch torchvision torchaudio cpuonly -c pytorch

# Install dependencies
poetry install
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration (see [Configuration](#configuration) section).

### 4. Set Up Voice Models

1. Create a `models` directory:
   ```bash
   mkdir models
   ```

2. Download a Piper TTS voice model from [Piper Voices](https://huggingface.co/rhasspy/piper-voices/tree/main)
   - Recommended: `en_US-lessac-medium`

3. Place both `.onnx` and `.onnx.json` files in the `models` directory

### 5. Initialize Database

```bash
# Run database migrations
poetry run alembic upgrade head
```

---

## Configuration

Configuration is managed through environment variables in the `.env` file.

### Required Configuration

```env
# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=sqlite:///./chat_history.db

# JWT Authentication
SECRET_KEY=your_secret_key_min_32_characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

### Optional Configuration

```env
# Web Search (Tavily AI)
TAVILY_API_KEY=your_tavily_api_key

# Weather Service (OpenWeatherMap)
OPENWEATHER_API_KEY=your_openweather_api_key

# Microsoft 365 Integration
MS_CLIENT_ID=your_azure_app_client_id
MS_TENANT_ID=your_azure_app_tenant_id
MS_CLIENT_SECRET=your_azure_app_client_secret

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Microsoft OAuth
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/auth/microsoft/callback

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/victus.log

# Security
RATE_LIMIT_ENABLED=true
CORS_ORIGINS=http://localhost:8000,http://localhost:3000
```

### Getting API Keys

#### OpenAI
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new secret key

#### Tavily AI (Web Search)
1. Visit [Tavily AI](https://tavily.com/)
2. Sign up for an account
3. Generate an API key from the dashboard

#### OpenWeatherMap (Weather)
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key

#### Microsoft Azure (M365 Integration)
1. Navigate to [Azure Portal](https://portal.azure.com/)
2. Go to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Configure:
   - Name: Your app name
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: `http://localhost:8000/api/auth/microsoft/callback`
5. After creation:
   - Copy **Application (client) ID** → `MS_CLIENT_ID`
   - Copy **Directory (tenant) ID** → `MS_TENANT_ID`
6. Go to **Certificates & secrets** > **New client secret**
   - Copy the secret value → `MS_CLIENT_SECRET`
7. Go to **API permissions** > **Add a permission** > **Microsoft Graph** > **Delegated permissions**
   - Add: `User.Read`, `Mail.ReadWrite`, `Mail.Send`, `Calendars.ReadWrite`
8. Click **Grant admin consent** (if required)

---

## Usage

### Starting the Application

#### Development Mode

```bash
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

#### Production Mode

```bash
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using the Web Interface

1. **Access the Application**: Open `http://localhost:8000` in your browser
2. **Authentication**: 
   - Sign up for a new account, or
   - Log in with existing credentials, or
   - Use OAuth (Google/Microsoft) for quick access
3. **Chat Interface**:
   - Type messages in the input field and press Enter
   - Click the microphone icon for voice input
   - Click the speaker icon to hear responses
4. **Document Upload**: Use the upload button to add PDF or DOCX files
5. **Microsoft 365**: First-time use will prompt for authentication

### Example Interactions

```
User: "What's the weather in Mumbai tomorrow?"
VICTUS: [Checks weather] "Tomorrow in Mumbai, expect partly cloudy skies with a high of 32°C..."

User: "Schedule a meeting with John at 3 PM tomorrow"
VICTUS: [Checks weather, creates calendar event] "I've scheduled a meeting with John for tomorrow at 3 PM..."

User: "Read my latest emails"
VICTUS: [Fetches emails] "You have 3 new emails. The most recent is from..."

User: "Remember that my favorite programming language is Python"
VICTUS: [Stores fact] "I've saved that your favorite programming language is Python."

User: "What's my favorite programming language?"
VICTUS: [Recalls fact] "Your favorite programming language is Python."
```

---

## API Documentation

### Interactive API Docs

Once the application is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user information
- `POST /api/auth/logout` - User logout
- `GET /api/auth/google/login` - Initiate Google OAuth
- `GET /api/auth/microsoft/login` - Initiate Microsoft OAuth

#### Chat
- `POST /api/chat` - Send chat message (Server-Sent Events stream)
- `POST /api/history` - Get chat history for a session

#### Documents
- `POST /api/upload` - Upload document for RAG processing

#### Voice
- `POST /api/transcribe` - Transcribe audio to text
- `POST /api/synthesize` - Synthesize text to speech

#### System
- `GET /healthz` - Health check endpoint
- `GET /metrics` - Prometheus metrics

### Authentication

Most endpoints support optional authentication. Include the JWT token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/chat
```

---

## Development

### Project Structure

The codebase follows a modular architecture:

- **`src/api/`**: API route handlers organized by domain
- **`src/auth/`**: Authentication and authorization logic
- **`src/tools/`**: Agent tools for various capabilities
- **`src/utils/`**: Shared utilities and helpers
- **`static/`**: Frontend static files

### Code Style

- Follow PEP 8 Python style guide
- Use type hints for all function signatures
- Include docstrings for all public functions and classes
- Keep functions focused and single-purpose

### Adding New Features

1. **New API Endpoint**: Add to appropriate file in `src/api/`
2. **New Tool**: Create in `src/tools/` and register in `assembler.py`
3. **New Authentication Provider**: Extend `src/auth/oauth.py`
4. **New Database Model**: Add to `src/models.py` and create migration

### Database Migrations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

---

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/test_api.py

# Run with verbose output
poetry run pytest -v
```

### Test Structure

- **`tests/test_api.py`**: API endpoint tests
- **`tests/test_agent.py`**: Agent functionality tests
- **`tests/test_memory_tools.py`**: Memory tools tests
- **`tests/test_metrics.py`**: Metrics collection tests

---

## Deployment

### Docker Deployment

#### Build Image

```bash
docker build -t project-victus .
```

#### Run Container

```bash
docker run -d \
  --name victus-container \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/faiss_index:/app/faiss_index \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/chat_history.db:/app/chat_history.db \
  project-victus
```

### Cloud Deployment

#### AWS App Runner

1. **Build and Push Docker Image**:
   ```bash
   # Tag and push to ECR or Docker Hub
   docker tag project-victus:latest your-registry/project-victus:latest
   docker push your-registry/project-victus:latest
   ```

2. **Create App Runner Service**:
   - Navigate to AWS App Runner console
   - Create new service
   - Configure:
     - Source: Container registry
     - Port: 8000
     - Environment variables: Add all required `.env` variables

3. **Access**: App Runner provides a secure HTTPS URL

#### Environment Variables for Production

Ensure all required environment variables are set in your deployment platform:
- `OPENAI_API_KEY`
- `SECRET_KEY` (use a strong, randomly generated key)
- `DATABASE_URL` (use PostgreSQL for production)
- Other service API keys as needed

### Production Considerations

- Use a production-grade database (PostgreSQL) instead of SQLite
- Set up proper logging aggregation (CloudWatch, Datadog, etc.)
- Configure HTTPS with proper SSL certificates
- Set up monitoring and alerting
- Implement backup strategies for database and vector store
- Use environment-specific configuration management

---

## Security

### Security Features

- **Authentication**: JWT-based token authentication
- **Authorization**: Role-based access control (where applicable)
- **Rate Limiting**: Protection against abuse and DDoS
- **Input Validation**: Comprehensive sanitization of user inputs
- **CORS**: Configurable cross-origin resource sharing
- **Password Hashing**: bcrypt for secure password storage
- **OAuth 2.0**: Secure third-party authentication

### Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong `SECRET_KEY`** values (minimum 32 characters, randomly generated)
3. **Enable HTTPS** in production
4. **Regularly update dependencies** to patch security vulnerabilities
5. **Monitor logs** for suspicious activity
6. **Limit CORS origins** to trusted domains
7. **Use environment-specific secrets** management

### Reporting Security Issues

If you discover a security vulnerability, please report it responsibly. Do not open public issues for security vulnerabilities.

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow code style and include tests
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**: Provide a clear description of changes

### Contribution Guidelines

- Write clear, concise commit messages
- Include tests for new features
- Update documentation as needed
- Follow existing code style and patterns
- Ensure all tests pass before submitting

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **OpenAI** for the GPT-4o model
- **LangChain** for the agent framework
- **FastAPI** for the excellent web framework
- **Faster-Whisper** and **Piper TTS** for voice capabilities
- All open-source contributors and libraries

---

## Support

For questions, issues, or feature requests, please open an issue on the GitHub repository.

---

<div align="center">

**Built with ❤️ for productivity and innovation**

</div>
