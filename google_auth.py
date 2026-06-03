from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

import streamlit as st
import pickle
import os
import json

# ==================================================
# CONFIG
# ==================================================

CLIENT_SECRET_FILE = "client_secret.json"

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

REDIRECT_URI = "http://localhost:8501"

TOKEN_FILE = "token.pickle"
VERIFIER_FILE = "verifier.txt"
SESSION_FILE = "session.json"

# ==================================================
# GET AUTH URL
# ==================================================

def get_auth_url():

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    return auth_url


# ==================================================
# HANDLE CALLBACK
# ==================================================

def handle_callback():

    params = st.query_params

    if "code" not in params:
        return False

    code = params["code"]

    if isinstance(code, list):
        code = code[0]

    try:

        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

        flow.fetch_token(code=code)

        creds = flow.credentials

        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)

        st.session_state["google_connected"] = True

        try:
            st.query_params.clear()
        except:
            pass

        return True

    except Exception as e:
        st.error(f"Google Auth Error: {e}")
        return False


# ==================================================
# GOOGLE CALENDAR SERVICE
# ==================================================

def get_service():

    if not os.path.exists(TOKEN_FILE):
        return None

    try:

        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

        service = build(
            "calendar",
            "v3",
            credentials=creds
        )

        return service

    except Exception:
        return None


# ==================================================
# CHECK CONNECTION
# ==================================================

def is_google_connected():

    return os.path.exists(TOKEN_FILE)


# ==================================================
# LOGOUT GOOGLE
# ==================================================

def remove_google_connection():

    try:

        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)

        if os.path.exists(VERIFIER_FILE):
            os.remove(VERIFIER_FILE)

    except:
        pass