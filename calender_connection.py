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
def handle_oauth_callback(code):
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    # IMPORTANT: load verifier safely
    verifier = st.session_state.get("code_verifier")

    if not verifier:
        raise Exception("Code verifier missing (Streamlit session reset issue)")

    flow.code_verifier = verifier

    try:
        flow.fetch_token(code=code)
    except Exception as e:
        print("TOKEN ERROR:", e)
        return None

    creds = flow.credentials

    # SAVE PER USER (IMPORTANT FIX)
    user_id = st.session_state.get("user_id", "default")
    token_file = f"token_{user_id}.pkl"

    with open(token_file, "wb") as f:
        pickle.dump(creds, f)

    return creds
# =========================
# LOAD CREDENTIALS
# =========================
def load_creds():
    user_id = st.session_state.get("user_id", "default")
    token_file = f"token_{user_id}.pkl"

    creds = None

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