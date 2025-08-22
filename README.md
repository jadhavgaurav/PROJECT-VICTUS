# Project VICTUS - Advanced AI Personal Assistant

Project VICTUS is a voice-enabled, conversational AI personal assistant built with a modern, production-grade technology stack. It is context-aware, capable of performing complex tasks through dynamic tool use, and deeply integrated with both local system and cloud productivity services.

## Features

-   **Voice Interface**: Real-time Speech-to-Text (Faster-Whisper) and Text-to-Speech (Piper).
-   **Advanced Agentic Brain**: Powered by Google Gemini 1.5 Flash and orchestrated with LangGraph.
-   **Persistent Document Q&A**: Upload PDF/DOCX files for the agent to query against, using a persistent FAISS vector store.
-   **Dynamic Tooling**:
    -   **Web Search**: Real-time internet access via Tavily.
    -   **System Tools**: Navigate the file system, manage applications, and access system info.
    -   **Microsoft 365**: Read/send Outlook emails and manage Outlook calendar events.
-   **Persistent Memory**: Full chat history is saved in a SQLite database.
-   **Web Frontend**: A clean, modern interface built with HTML, CSS, and Vanilla JavaScript.

## Tech Stack

-   **Backend**: FastAPI
-   **AI Agent**: LangChain + LangGraph + Google Gemini 1.5 Flash
-   **Frontend**: HTML, CSS, Vanilla JavaScript
-   **Voice I/O**: Faster-Whisper (STT), Piper TTS (TTS)
-   **Vector Store**: FAISS
-   **Web Search**: Tavily Search API
-   **M365 Auth**: MSAL (Microsoft Authentication Library)
-   **Dependencies**: Poetry
-   **Deployment**: Docker

---

## 🚀 Step 1: Initial Setup

### 1.1. Prerequisites

-   [Python 3.10+](https://www.python.org/)
-   [Poetry](https://python-poetry.org/docs/#installation) for dependency management.
-   [Docker](https://www.docker.com/products/docker-desktop/) for containerization.
-   System dependency for Piper TTS:
    ```bash
    # On Debian/Ubuntu
    sudo apt-get update && sudo apt-get install -y espeak-ng

    # On MacOS
    brew install espeak
    ```

### 1.2. Clone the Project

Create a new directory for your project and save all the provided files into the structure outlined below.

### 1.3. API Keys and Environment Variables

You need to get API keys from the following services:

-   **Google AI Studio**: for the `GOOGLE_API_KEY`.
-   **Tavily AI**: for the `TAVILY_API_KEY`.
-   **Microsoft Azure**: This is the most involved.
    1.  Go to the [Azure Portal](https://portal.azure.com/) and navigate to **Azure Active Directory**.
    2.  Go to **App registrations** > **New registration**.
    3.  Name it "ProjectVictus" or similar. Select "Accounts in any organizational directory (Any Azure AD directory - Multitenant) and personal Microsoft accounts (e.g. Skype, Xbox)".
    4.  You don't need a Redirect URI for the device code flow.
    5.  After creation, copy the **Application (client) ID** and **Directory (tenant) ID**. These are your `MS_CLIENT_ID` and `MS_TENANT_ID`.
    6.  Go to **API permissions** > **Add a permission** > **Microsoft Graph**.
    7.  Select **Delegated permissions**. Add the following permissions:
        -   `offline_access`
        -   `User.Read`
        -   `Mail.ReadWrite`
        -   `Mail.Send`
        -   `Calendars.ReadWrite`
    8.  Go to **Authentication** in the side panel. Scroll down and enable **Allow public client flows**. Click **Save**.

Now, create a file named `.env` in the root of your project and populate it with your keys:

```env
# .env file
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
TAVILY_API_KEY="YOUR_TAVILY_API_KEY"
MS_CLIENT_ID="YOUR_AZURE_APP_CLIENT_ID"
MS_TENANT_ID="YOUR_AZURE_APP_TENANT_ID"
```

---

## 🎶 Step 2: Voice Model Setup (Piper TTS)

The text-to-speech model requires a voice file.

1.  Create a directory named `models` in your project root.
2.  Download a voice model from [Piper Voices](https://huggingface.co/rhasspy/piper-voices/tree/main). We recommend starting with a high-quality medium voice, like `en_US-lessac-medium.onnx` and its corresponding `.json` file.
3.  Place both the `.onnx` and `.onnx.json` files inside the `models` directory.
4.  Your project should now have a `models/en_US-lessac-medium.onnx` file (or similar).

---

## 📦 Step 3: Install Dependencies

Open your terminal in the project root and install all Python dependencies using Poetry.

```bash
poetry install
```

This will create a virtual environment and install everything listed in `pyproject.toml`.

---

## ▶️ Step 4: Running the Application

There are two ways to run Project VICTUS:

### 4.1. Local Development (with Uvicorn)

This is best for testing and development.

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser and navigate to `http://localhost:8000`.

### 4.2. Production (with Docker)

This is the recommended way to run the application for stable use.

1.  **Build the Docker image:**
    ```bash
    docker build -t project-victus .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -d -p 8000:8000 --name victus-container --env-file .env -v $(pwd)/faiss_index:/app/faiss_index -v $(pwd)/uploads:/app/uploads -v $(pwd)/.msal_token_cache.json:/app/.msal_token_cache.json project-victus
    ```
    *This command maps the port, mounts the persistent FAISS index, uploads folder, and MSAL token cache to your host machine.*

Open your browser and navigate to `http://localhost:8000`.

---

## 📝 How to Use

1.  **Chat**: Simply type your message and press Enter.
2.  **Use Tools**:
    -   "What's the latest news on AI?" (Web Search)
    -   "List files on my desktop." (System Tool)
    -   "Open VS Code." (System Tool)
    -   "Summarize my last 3 emails." (M365 - requires login)
    -   "Create a calendar event for tomorrow at 10 AM titled 'Project sync'." (M365 - requires login)
3.  **Microsoft 365 Login**:
    -   The first time you ask for an email or calendar action, the agent will respond that you need to log in.
    -   Check the **terminal** where the server is running. It will display a message like: `To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code XXXXXXX to authenticate.`
    -   Follow the instructions. Once you log in, your token is cached, and you won't need to do this again until it expires.
4.  **Upload Documents for Q&A**:
    -   Use the "Upload Document" button to select a `.pdf` or `.docx` file.
    -   Once uploaded, you can ask questions about its content, e.g., "What does the document say about machine learning?"
5.  **Voice Interaction**:
    -   **Input**: Click the microphone icon to start recording. Click it again to stop. Your speech will be transcribed and sent.
    -   **Output**: Click the speaker icon next to any agent message to have it read aloud.