import os
import pickle
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

REDIRECT_URI = "https://agentic-ai-final.streamlit.app/"

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

client_config = {
    "web": {
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [REDIRECT_URI]
    }
}
# =====================
# STEP 1: LOGIN URL
# ====================
def get_calendar_auth_url():
    import urllib.parse

    params = {
        "client_id": client_config["web"]["client_id"],
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    }

    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

    return url


# =====================
# STEP 2: CALLBACK
# =====================
import requests

def handle_oauth_callback(code):
    try:
        data = {
            "code": code,
            "client_id": client_config["web"]["client_id"],
            "client_secret": client_config["web"]["client_secret"],
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }

        token_url = "https://oauth2.googleapis.com/token"
        r = requests.post(token_url, data=data)
        token_data = r.json()

        if "access_token" not in token_data:
            st.error(token_data)
            return None

        from google.oauth2.credentials import Credentials

        creds = Credentials(
            token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_url,
            client_id=client_config["web"]["client_id"],
            client_secret=client_config["web"]["client_secret"],
        )
        token_file = f"token_{user_id}.pkl"
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)

        return creds

    except Exception as e:
        st.error(f"OAuth Error: {e}")
        return None
# =========================
# LOAD CREDENTIALS
# =========================
def load_creds(user_id):
    creds = None
    token_file = f"token_{user_id}.pkl"

    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    return creds

# =========================
# GOOGLE CALENDAR SERVICE
# =========================
def get_calendar_service(user_id):
    creds = load_creds(user_id)
    if not creds:
        return None
    return build("calendar", "v3", credentials=creds)

# =========================
# PROFILE INFO
# =========================
def get_google_profile_info(creds):
    service = build("oauth2", "v2", credentials=creds)
    return service.userinfo().get().execute()