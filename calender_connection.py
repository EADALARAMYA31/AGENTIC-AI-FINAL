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
def get_calendar_auth_url():
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    st.session_state["oauth_state"] = state

    # Save verifier globally
    with open("oauth_verifier.txt", "w") as f:
        f.write(flow.code_verifier)

    return auth_url


# =====================
# STEP 2: CALLBACK
# =====================
def handle_oauth_callback(code):
    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

        verifier = st.session_state.get("code_verifier")

        st.write("VERIFIER =", verifier)

        flow.code_verifier = verifier

        flow.fetch_token(code=code)

        return flow.credentials

    except Exception as e:
        import traceback

        st.error(str(e))
        st.code(traceback.format_exc())

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