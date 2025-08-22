#tools.py

import os
import subprocess
import platform
import pyperclip #type:ignore
import requests #type:ignore
from typing import List
from pathlib import Path
from datetime import datetime, timedelta, timezone
import winreg
import dateparser #type:ignore

# LangChain Imports
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# Local Auth Import
from auth import get_access_token

# --- Configuration & ADVANCED Path Resolution ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FAISS_INDEX_PATH = "faiss_index"
UPLOAD_DIR = "uploads"
HOME_DIR = Path.home()

def get_windows_special_folder(folder_name):
    """
    Finds the correct path for special folders (like Desktop) from the Windows Registry.
    This correctly handles OneDrive-managed folders.
    """
    if platform.system() == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            path, _ = winreg.QueryValueEx(key, folder_name)
            return Path(path)
        except Exception:
            # Fallback if registry key is not found
            return HOME_DIR / folder_name
    else: # Fallback for non-Windows systems (macOS, Linux)
        return HOME_DIR / folder_name

# Using the robust function to define our shortcuts
PATH_SHORTCUTS = {
    "desktop": get_windows_special_folder("Desktop"),
    "documents": get_windows_special_folder("Documents"),
    "downloads": get_windows_special_folder("Downloads"),
    "pictures": get_windows_special_folder("Pictures"),
    "videos": get_windows_special_folder("Videos"),
    "home": HOME_DIR,
}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=GOOGLE_API_KEY)

def _resolve_path(path_str: str) -> Path:
    """Resolves common shortcuts into full file paths."""
    path_str = path_str.lower().strip()
    return PATH_SHORTCUTS.get(path_str, Path(path_str).expanduser().resolve())

# ==============================================================================
# 1. Web Search & RAG Tools
# ==============================================================================
web_search_tool = TavilySearchResults(k=3, tavily_api_key=TAVILY_API_KEY)

def update_vector_store(file_path: str):
    """Loads, splits, and indexes a single document file."""
    loader = PyPDFLoader(file_path) if file_path.endswith(".pdf") else Docx2txtLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    if os.path.exists(FAISS_INDEX_PATH) and os.listdir(FAISS_INDEX_PATH):
        db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        db.add_documents(docs)
    else:
        db = FAISS.from_documents(docs, embeddings)
    db.save_local(FAISS_INDEX_PATH)

@tool
def query_uploaded_documents(query: str) -> str:
    """Queries the content of all previously uploaded documents to answer a question."""
    if not os.path.exists(FAISS_INDEX_PATH) or not os.listdir(FAISS_INDEX_PATH):
        return "No documents have been uploaded yet. Please upload a document first."
    try:
        db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        context = "\n\n".join([doc.page_content for doc in retriever.invoke(query)])
        return f"Relevant information from documents:\n---\n{context}\n---"
    except Exception as e:
        return f"Error querying documents: {e}"

# ==============================================================================
# 2. Advanced System Tools
# ==============================================================================
@tool
def list_files(directory: str) -> str:
    """Lists files and directories in a specified location using shortcuts like 'desktop'."""
    path = _resolve_path(directory)
    if not path.is_dir():
        return f"Error: Directory '{path}' not found. Please ensure the shortcut or path is correct."
    try:
        files = [f.name for f in path.iterdir()]
        return "\n".join(files) if files else "The directory is empty."
    except Exception as e:
        return f"Error listing files: {e}"

@tool
def open_app(application_name: str) -> str:
    """
    Intelligently finds and opens an application, including standard programs and Microsoft Store apps.
    Handles aliases like 'vs code', 'chrome', 'whatsapp', 'spotify', etc.
    """
    if platform.system() != "Windows":
        return "This advanced open_app tool is configured for Windows only."

    app_name_lower = application_name.lower().strip()
    
    # --- 1. Microsoft Store App Launch (New) ---
    store_apps = {
        "whatsapp": "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
        "spotify": "SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify",
        # Add other store apps here by finding their AppUserModelID
    }
    if app_name_lower in store_apps:
        try:
            command = f'explorer.exe shell:appsfolder\\{store_apps[app_name_lower]}'
            subprocess.Popen(command, shell=True)
            return f"Successfully launched the {application_name} app."
        except Exception as e:
            return f"Failed to launch the {application_name} app: {e}"

    # --- 2. Traditional App Search (Registry, File System, PATH) ---
    aliases = {
        "vs code": "Code.exe", "visual studio code": "Code.exe",
        "chrome": "chrome.exe", "google chrome": "chrome.exe",
        "word": "WINWORD.EXE", "excel": "EXCEL.EXE", "powerpoint": "POWERPNT.EXE",
        "notepad": "notepad.exe", "calculator": "calc.exe",
        "edge": "msedge.exe", "firefox": "firefox.exe"
    }
    executable_name = aliases.get(app_name_lower, f"{application_name}.exe")

    try:
        key_path = fr"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{executable_name}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            executable_path, _ = winreg.QueryValue(key, None)
            subprocess.Popen(executable_path)
            return f"Successfully opened {application_name} via Registry."
    except FileNotFoundError:
        pass 
    except Exception as e:
        return f"Found {application_name} in Registry but failed to open: {e}"

    search_paths = [
        Path(os.environ.get("ProgramFiles", "C:/Program Files")),
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")),
        HOME_DIR / "AppData" / "Local" / "Programs",
        HOME_DIR / "AppData" / "Local",
    ]
    for path in search_paths:
        for root, _, files in os.walk(path):
            if executable_name.lower() in [f.lower() for f in files]:
                try:
                    subprocess.Popen(str(Path(root) / executable_name))
                    return f"Successfully found and opened {application_name}."
                except Exception as e:
                    return f"Found {application_name} but failed to launch: {e}"
    
    try:
        subprocess.Popen(executable_name, shell=True)
        return f"Successfully launched {application_name} from system PATH."
    except Exception:
        return f"Error: Could not find the application '{application_name}' after a thorough search."


@tool
def get_clipboard_content() -> str:
    """Reads and returns the current content of the system clipboard. Takes no arguments."""
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Could not get clipboard content: {e}"


@tool
def take_screenshot(path: str = "desktop") -> str:
    """
    Takes a screenshot of the entire screen and saves it to a specified path or shortcut location.
    Defaults to saving on the desktop if no path is given.
    """
    try:
        save_path = _resolve_path(path)
        if save_path.is_dir():
            # Generate a unique filename if a directory is provided
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            save_file = save_path / filename
        else:
            # Assume a full file path was given
            save_file = save_path

        pyautogui.screenshot(str(save_file))
        return f"Screenshot saved successfully to {save_file}"
    except Exception as e:
        return f"Failed to take screenshot: {e}"

@tool
def type_text(text: str) -> str:
    """
    Types the given text using the keyboard. Useful for automating typing into applications.
    Make sure the correct window is active before using.
    """
    try:
        pyautogui.write(text, interval=0.05)
        return "Text typed successfully."
    except Exception as e:
        return f"Failed to type text: {e}"

@tool
def get_active_window_title() -> str:
    """Gets the title of the currently active (focused) window on the screen."""
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            return f"The active window is: '{active_window.title}'"
        else:
            return "No active window found."
    except Exception as e:
        return f"Failed to get active window title: {e}"
    

# ==============================================================================
# 3. Microsoft 365 Tools
# ==============================================================================
BASE_URL = "https://graph.microsoft.com/v1.0"

@tool
def read_emails(max_emails: int = 5, folder: str = "inbox") -> str:
    """
    Reads emails from a specified folder in the user's Microsoft Outlook account.
    - Defaults to reading the 'inbox'.
    - Can also be used for other folders, such as 'sentitems'.
    Keywords: email, mail, inbox, outlook, sent.
    """
    token = get_access_token()
    if not token:
        return "Authentication failed. The login process must be completed in the terminal."

    # Use a dictionary to map simple names to the official Microsoft Graph API folder IDs
    folder_map = {
        "inbox": "inbox",
        "sent": "sentitems",
        "drafts": "drafts",
        "archive": "archive",
        "deleted": "deleteditems"
    }
    folder_id = folder_map.get(folder.lower().strip(), "inbox") # Default to inbox if not found

    headers = {"Authorization": f"Bearer {token}"}
    
    # This new endpoint is more specific and correctly targets the specified mail folder
    endpoint = f"{BASE_URL}/me/mailFolders/{folder_id}/messages?$select=subject,from,receivedDateTime&$orderby=receivedDateTime desc&$top={max_emails}"
    
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        emails = response.json().get("value", [])
        if not emails:
            return f"The '{folder_id}' folder is empty."
        summaries = [f"From: {e['from']['emailAddress']['name']}\nSubject: {e['subject']}" for e in emails]
        return "\n\n---\n\n".join(summaries)
    
    return f"Error reading emails from folder '{folder_id}': {response.text}"

@tool
def send_email(to: str, subject: str, content: str = "") -> str:
    """
    Sends an email from the user's Microsoft Outlook account to a recipient. Keywords: email, mail, send, outlook.
    This will automatically trigger a login prompt in the terminal if the user is not authenticated.
    """
    token = get_access_token()
    if not token:
        return "Authentication failed. The login process must be completed in the terminal."

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    email_data = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": content},
            "toRecipients": [{"emailAddress": {"address": to}}]
        },
        "saveToSentItems": "true"
    }
    response = requests.post(f"{BASE_URL}/me/sendMail", headers=headers, json=email_data)
    return "Email sent successfully." if response.status_code == 202 else f"Error sending email: {response.text}"

@tool
def get_calendar_events(days: int = 7, specific_date: str = None) -> str:
    """
    Gets events from the user's Microsoft Outlook calendar.
    - If a 'specific_date' (YYYY-MM-DD) is provided, it will get events for that day.
    - Otherwise, it gets events for a specified number of 'days' from today.
    Keywords: calendar, event, appointment, meeting, schedule.
    """
    token = get_access_token()
    if not token:
        return "Authentication failed. The login process must be completed in the terminal."

    headers = {"Authorization": f"Bearer {token}"}
    
    if specific_date:
        try:
            start_dt = datetime.strptime(specific_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=1)
            start_time = start_dt.isoformat() + "Z"
            end_time = end_dt.isoformat() + "Z"
        except ValueError:
            return "Error: Please provide the specific_date in YYYY-MM-DD format."
    else:
        start_time = datetime.utcnow().isoformat() + "Z"
        end_time = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"

    params = {'startDateTime': start_time, 'endDateTime': end_time, '$select': 'subject,start,end', '$orderby': 'start/dateTime'}
    response = requests.get(f"{BASE_URL}/me/calendarview", headers=headers, params=params)
    
    if response.status_code == 200:
        events = response.json().get("value", [])
        if not events:
            return f"No events found for the specified period."
        details = [f"- {e['subject']} starting at {e['start']['dateTime']}" for e in events]
        return "Here are the matching events:\n" + "\n".join(details)
    return f"Error getting calendar events: {response.text}"



@tool
def create_calendar_event(subject: str, start_time_str: str, end_time_str: str, location: str = None, body: str = None) -> str:
    """
    Creates a new event in the user's Outlook calendar.
    - Requires a 'subject'.
    - Requires a 'start_time_str' and 'end_time_str' in a natural language format (e.g., "today at 5pm", "tomorrow at 9am").
    - The tool will intelligently handle date and timezone conversions.
    """
    token = get_access_token()
    if not token:
        return "Authentication failed. The login process must be completed in the terminal."

    try:
        # Use dateparser to intelligently convert natural language to datetime objects
        # It assumes the user's local timezone if not specified.
        start_dt = dateparser.parse(start_time_str)
        end_dt = dateparser.parse(end_time_str)

        if not start_dt or not end_dt:
            return "Error: Could not understand the start or end time. Please be more specific (e.g., 'today at 5pm', 'August 23 2025 at 10am')."

        # Convert the parsed local time to UTC for the API
        start_utc = start_dt.astimezone(timezone.utc)
        end_utc = end_dt.astimezone(timezone.utc)

    except Exception as e:
        return f"Error parsing date/time: {e}. Please use a clearer format."

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    event_data = {
        "subject": subject,
        "start": {
            "dateTime": start_utc.isoformat(),
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": end_utc.isoformat(),
            "timeZone": "UTC"
        }
    }
    if location:
        event_data["location"] = {"displayName": location}
    if body:
        event_data["body"] = {"contentType": "Text", "content": body}

    response = requests.post(f"{BASE_URL}/me/events", headers=headers, json=event_data)

    if response.status_code == 201:
        return f"Successfully created calendar event: '{subject}'."
    
    return f"Error creating calendar event: {response.status_code} - {response.text}"



# ==============================================================================
# 4. Tool Assembler Function
# ==============================================================================
def get_all_tools(rag_enabled: bool) -> List:
    """Dynamically assembles the list of available tools."""
    all_tools = [
        web_search_tool,
        list_files,
        open_app,
        get_clipboard_content,
        take_screenshot,
        type_text,
        get_active_window_title
    ]
    if rag_enabled:
        all_tools.append(query_uploaded_documents)
    
    # Always include the M365 tools. They handle their own auth.
    all_tools.extend([
        read_emails,
        send_email,
        get_calendar_events,
        create_calendar_event
    ])
    return all_tools