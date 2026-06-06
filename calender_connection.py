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
# =====================
def get_flow():
    return Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

def get_calendar_auth_url():
    flow = get_flow()

    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes=True
    )

    st.session_state["oauth_state"] = state
    st.session_state["oauth_flow"] = flow   # 🔥 REQUIRED

    return auth_url


# =====================
# STEP 2: CALLBACK FIX
# =====================
def handle_oauth_callback():
    code = st.query_params.get("code")

    if not code:
        return None

    flow = st.session_state.get("oauth_flow")

    if not flow:
        st.error("OAuth session lost. Please login again.")
        return None

    try:
        flow.fetch_token(code=code)
        creds = flow.credentials

        return creds

    except Exception as e:
        st.error(f"OAuth failed: {e}")
        return None

# =========================
# LOAD CREDENTIALS
# =========================
def load_creds():
    creds = None

    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)

    return creds

# =========================
# GOOGLE CALENDAR SERVICE
# =========================
def get_calendar_service():
    creds = load_creds()
    if not creds:
        return None
    return build("calendar", "v3", credentials=creds)

# =========================
# PROFILE INFO
# =========================
def get_google_profile_info(creds):
    service = build("oauth2", "v2", credentials=creds)
    return service.userinfo().get().execute()