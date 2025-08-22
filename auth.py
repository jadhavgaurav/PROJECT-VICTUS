import os
import msal
import atexit
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("MS_CLIENT_ID")
TENANT_ID = os.getenv("MS_TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read", "Mail.ReadWrite", "Mail.Send", "Calendars.ReadWrite"]

# Persist token cache
CACHE_FILE = ".msal_token_cache.json"

def save_cache(cache):
    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())

def load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache.deserialize(f.read())
    atexit.register(lambda: save_cache(cache))
    return cache

token_cache = load_cache()
app = msal.PublicClientApplication(
    CLIENT_ID, authority=AUTHORITY, token_cache=token_cache
)

def get_access_token():
    """
    Acquires an access token for Microsoft Graph API.
    Attempts to get it from the cache first, then falls back to device flow.
    """
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result:
            save_cache(token_cache)
            return result.get("access_token")

    # Fallback to device flow
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise ValueError("Failed to create device flow. Check your app registration.")

    print(f"MSAL: {flow['message']}", flush=True)
    # The user needs to follow the instructions in the terminal.
    # The server will block here until authentication is complete.
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        save_cache(token_cache)
        return result.get("access_token")
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))
        return None

def is_authenticated():
    """Check if we have a cached token without prompting for login."""
    return bool(app.get_accounts())