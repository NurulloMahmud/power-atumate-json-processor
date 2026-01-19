import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import msal
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["Files.ReadWrite.All"]

TOKEN_CACHE_FILE = "token_cache.json"


def get_msal_app():
    """Create an MSAL application instance with token cache."""
    
    # Load existing token cache if it exists
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, "r") as f:
            cache.deserialize(f.read())
    
    app = msal.ConfidentialClientApplication(
        client_id=os.getenv("CLIENT_ID"),
        client_credential=os.getenv("CLIENT_SECRET"),
        authority="https://login.microsoftonline.com/consumers",
        token_cache=cache,
    )
    
    return app, cache


def save_cache(cache):
    """Save token cache to file."""
    if cache.has_state_changed:
        with open(TOKEN_CACHE_FILE, "w") as f:
            f.write(cache.serialize())


def get_access_token():
    """
    Get a valid access token for Microsoft Graph API.
    Uses cached token if available, otherwise initiates browser login.
    """
    app, cache = get_msal_app()
    
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            print("Using cached token")
            save_cache(cache)
            return result["access_token"]
    
    # No cached token - need interactive login
    print("No cached token found. Opening browser for login...")
    result = interactive_login(app)
    
    if "access_token" in result:
        save_cache(cache)
        return result["access_token"]
    else:
        raise Exception(f"Authentication failed: {result.get('error_description', 'Unknown error')}")


def interactive_login(app):
    """
    Perform interactive login via browser.
    Opens browser for user to login, then captures the authorization code.
    """
    
    auth_code = {"code": None}
    
    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = parse_qs(urlparse(self.path).query)
            if "code" in query:
                auth_code["code"] = query["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Login successful!</h1><p>You can close this window.</p></body></html>")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Authentication failed")
        
        def log_message(self, format, *args):
            pass
    
    server = HTTPServer(("localhost", 8000), CallbackHandler)
    
    auth_url = app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/callback",
    )
    
    print(f"Opening browser for login...")
    webbrowser.open(auth_url)
    
    server.handle_request()
    server.server_close()
    
    if not auth_code["code"]:
        raise Exception("Failed to receive authorization code")
    
    result = app.acquire_token_by_authorization_code(
        code=auth_code["code"],
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/callback",
    )
    
    return result


if __name__ == "__main__":
    token = get_access_token()
    print(f"Got token: {token[:50]}...")