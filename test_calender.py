from calender_connection import authenticate_google
from datetime import datetime, timedelta

service = authenticate_google()

now = datetime.utcnow().isoformat() + 'Z'

events_result = service.events().list(
    calendarId='primary',
    timeMin=now,
    maxResults=10,
    singleEvents=True,
    orderBy='startTime'
).execute()

events = events_result.get('items', [])

for event in events:
    print(event['summary'])
def create_event(service):
    event = {
        'summary': 'AI Project Study',
        'start': {
            'dateTime': '2026-03-01T10:00:00',
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': '2026-03-01T12:00:00',
            'timeZone': 'Asia/Kolkata',
        },
    }

    event = service.events().insert(
        calendarId='primary',
        body=event
    ).execute()

    print("Event created:", event.get('htmlLink'))

create_event(service)