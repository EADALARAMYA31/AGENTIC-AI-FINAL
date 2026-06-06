import os
import pickle
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# =========================
# CONFIG
# =========================
REDIRECT_URI = "https://agentic-ai-final.streamlit.app/"
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]
client_config = {
    "web": {
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris":[REDIRECT_URI]
    }
}

# =========================
# 1. GENERATE GOOGLE LOGIN URL
# =========================
def get_calendar_auth_url():
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true"
    )

    # store state for validation
    st.session_state["oauth_state"] = state

    return auth_url


# =========================
# 2. HANDLE CALLBACK
# =========================
def handle_oauth_callback(code):
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    # IMPORTANT: restore state
    flow.fetch_token(code=code)

    return flow.credentials

# =========================
# 3. LOAD SAVED CREDENTIALS
# =========================
def load_creds():
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)

    return creds


# =========================
# 4. GOOGLE CALENDAR SERVICE
# =========================
def get_calendar_service():
    creds = load_creds()
    if not creds:
        return None
    return build("calendar", "v3", credentials=creds)


# =========================
# 5. GOOGLE PROFILE NAME
# =========================
def get_google_profile_info(creds):
    service = build("oauth2", "v2", credentials=creds)
    return service.userinfo().get().execute()

