# Project VICTUS

<div align="center">

**An advanced, voice-enabled, conversational AI personal assistant built for seamless productivity and system control.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
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

### ⚙️ User Settings

- **Profile Management**: View and manage account details
- **Memory Control**: View and delete stored facts/memories
- **Security**: Change passwords directly from the application

---

## Architecture

Project VICTUS follows a modular, layered architecture designed for maintainability, scalability, and testability.

### Visual Architecture Documentation

For a comprehensive, interactive visualization of the System Architecture, Database Schema, and Workflows, please view:

👉 **[System Architecture Diagrams](docs/architecture.html)**

### System Components

```
project_victus/
├── src/ (Backend)
│   ├── main.py                 # FastAPI application entry point
│   ├── agent.py                # AI agent executor configuration
│   ├── api/                    # API route handlers
│   ├── auth/                   # Authentication module
│   ├── tools/                  # Agent tools module (System, M365, RAG)
│   ├── utils/                  # Utility modules
│   └── database.py             # Database connection
│
├── frontend/ (React)
│   ├── src/
│   │   ├── components/         # UI Components
│   │   ├── state/              # Agent State Store
│   │   └── api/                # API Client
│   └── README.md
│
├── docs/                       # Documentation & Diagrams
├── pyproject.toml              # Backend Dependency Management
└── README.md                   # This file
```

---

## Tech Stack

### Backend

- **FastAPI**: Modern, high-performance web framework for building APIs
- **Poetry**: Dependency management and packaging
- **Pydantic**: Data validation and settings management
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Primary database for development
- **FAISS**: Vector database for RAG

### Frontend

- **React 18**: User Interface library
- **Vite**: Next Generation Frontend Tooling
- **TypeScript**: Static typing
- **Tailwind CSS**: Utility-first CSS framework
- **Zustand**: State management

### AI & Machine Learning

- **OpenAI GPT-4o**: LLM for reasoning
- **LangChain**: Agent framework
- **Faster-Whisper**: Speech-to-Text
- **Piper TTS**: Text-to-Speech

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Poetry**: [Install Poetry](https://python-poetry.org/docs/#installation)
- **FFmpeg**: Required for audio processing

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/jadhavgaurav/PROJECT-VICTUS.git
cd PROJECT-VICTUS
```

### 2. Backend Setup

```bash
cd backend
poetry install
poetry shell
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Configuration

Create a `.env` file in the `backend/` directory based on `.env.example`.

### 5. Initialize Database

```bash
# Inside backend/ (poetry shell)
poetry run alembic upgrade head
```

---

## Usage

### Starting the Backend

```bash
cd backend
poetry run uvicorn src.main:app --reload --port 8000
```

### Starting the Frontend

```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173` to access the application.

---

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Contributing

Contributions are welcome! Please check out the `docs/` folder for architectural guidance before making changes.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for productivity and innovation**

</div>
