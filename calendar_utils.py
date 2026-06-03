from googleapiclient.discovery import build

def get_calendar_service(creds):
    return build("calendar", "v3", credentials=creds)


def create_event(service, summary, start_time, end_time):
    event = {
        "summary": summary,
        "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return created_event.get("htmlLink")
def get_calendar_service(user_id):
    return authenticate_google(user_id)