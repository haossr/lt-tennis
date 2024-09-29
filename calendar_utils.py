import os
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# The scope of access required
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Path to the Service Account JSON key file
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_PATH")
CALENDAR_ID = os.getenv("CALENDAR_ID")

def authenticate_google_calendar():
    """Authenticate and return the Google Calendar service instance using a service account."""
    try:
        # Load service account credentials from the JSON file
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # Create the Google Calendar API service using the credentials
        service = build('calendar', 'v3', credentials=credentials)
        logger.info("Service account authenticated successfully.")
        return service
    except Exception as e:
        logger.error(f"Failed to authenticate service account: {e}")
        return None

def check_duplicate_event(service, calendar_id, summary, start_time, end_time):
    """
    Check if a similar event already exists on the calendar.
    
    Args:
        service: The Google Calendar API service instance.
        calendar_id: The ID of the calendar where to check for duplicates.
        summary: The event title to check for duplicates.
        start_time: The start time of the event (RFC3339 timestamp format).
        end_time: The end time of the event (RFC3339 timestamp format).
    
    Returns:
        bool: True if a duplicate event exists, False otherwise.
    """
    try:
        # Query for events during the specified time range
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # Check if any events match the summary and time range
        for event in events:
            if event['summary'] == summary:
                logger.info(f"Duplicate event found: {event['htmlLink']}")
                return True

        return False
    except Exception as e:
        logger.error(f"Error checking for duplicate event: {e}")
        return False

def create_calendar_event(service, summary, start_time, end_time, location="", description="", calendar_id=CALENDAR_ID, timezone='America/Los_Angeles'):
    """
    Create a calendar event using the service account, with duplicate check.
    
    Args:
        service: The Google Calendar API service instance.
        summary: The event title.
        location: The event location.
        description: A brief description of the event.
        start_time: The start time of the event (RFC3339 timestamp format).
        end_time: The end time of the event (RFC3339 timestamp format).
        calendar_id: The ID of the calendar where the event will be created.
        timezone: The timezone for the event (default is 'America/Los_Angeles').
    
    Returns:
        The created event or None if a duplicate event exists.
    """
    logger.info("Checking for duplicate events before creating the event.")
    
    # Check if a duplicate event already exists
    if check_duplicate_event(service, calendar_id, summary, start_time, end_time):
        logger.info("Event creation aborted: Duplicate event already exists.")
        return None
    
    logger.info("No duplicate event found. Proceeding to create the event.")
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time,
            'timeZone': timezone,
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    try:
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        logger.info(f"Event created successfully: {event.get('htmlLink')}")
    except Exception as e:
        logger.error(f"Failed to create event: {e}")
        raise
    return event

# Example usage
if __name__ == '__main__':
    try:
        service = authenticate_google_calendar()
        if service:
            # Parameters for the event
            summary = "Service Account Meeting"
            location = "Virtual"
            description = "Discussing service account integration with Google Calendar API"
            start_time = '2024-10-01T09:00:00-07:00'  # Make sure the time is in RFC3339 format with timezone
            end_time = '2024-10-01T10:00:00-07:00'
            timezone = 'America/Los_Angeles'  # Default to San Francisco timezone

            create_calendar_event(service, summary, location, description, start_time, end_time, calendar_id, timezone)
        else:
            logger.error("Failed to authenticate with Google Calendar API using service account.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")