import os
import time
from io import StringIO
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import pytz

from calendar_utils import authenticate_google_calendar, create_calendar_event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

TIMEZONE = 'America/Los_Angeles'
LOCATION = '755 S Mathilda Ave, Sunnyvale, CA  94087, United States'

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get username and password from environment variables
username = os.getenv("LT_USERNAME")
password = os.getenv("LT_PASSWORD")

if not username or not password:
    logging.error("Please set LT_USERNAME and LT_PASSWORD environment variables.")
    exit(1)

def parse_datetime(reservation_date, reservation_time):
    """Parse date and time from the reservation string and convert to RFC3339 format."""
    try:
        # Example: "Sat, Oct 05, 2024" and "8:00 AM - 9:30 AM"
        start_time_str, end_time_str = reservation_time.split(' - ')
        
        # Parse the date and times
        start_time = datetime.strptime(f"{reservation_date} {start_time_str}", "%a, %b %d, %Y %I:%M %p")
        end_time = datetime.strptime(f"{reservation_date} {end_time_str}", "%a, %b %d, %Y %I:%M %p")
        
        # Convert to the correct timezone (America/Los_Angeles)
        tz = pytz.timezone(TIMEZONE)
        start_time = tz.localize(start_time).isoformat()
        end_time = tz.localize(end_time).isoformat()
        
        return start_time, end_time
    except Exception as e:
        logger.error(f"Error parsing date/time: {e}")
        raise

def get_booking_df() -> pd.DataFrame:
    # Configure the browser driver (Chrome in this example)
    chrome_options = Options()
    # Add headless mode if needed
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)  # Set explicit wait time

    try:
        # Open login page
        driver.get("https://lt.clubautomation.com/")
        logging.info("Opened login page.")

        # Wait for username and password input fields to load
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "login")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        logging.info("Located username and password fields.")

        # Enter username and password
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        logging.info("Entered username and password.")

        # Submit login form
        password_field.send_keys(Keys.RETURN)
        logging.info("Submitted login form.")

        # Wait for an element that confirms login was successful
        wait.until(EC.presence_of_element_located((By.ID, "initial-page")))
        logging.info("Login successful.")

        # Navigate to reservation page
        driver.get("https://lt.clubautomation.com/event/reserve-court-new")
        logging.info("Navigated to reservation page.")

        # Get reservation list table
        table_element = wait.until(EC.presence_of_element_located((By.ID, "table-reservation-list")))
        table_html = table_element.get_attribute('outerHTML')
        logging.info("Retrieved reservation list.")

        # Parse HTML table using pandas
        dfs = pd.read_html(StringIO(table_html))
        reservation_df = dfs[0]

        # Output reservation information
        return(reservation_df)

    except Exception as e:
        logging.info(f"An error occurred: {e}")
    finally:
        driver.quit()
        logging.info("Closed browser driver.")

def submit_events_from_dataframe(df):
    """Submit each row of the DataFrame as a calendar event."""
    service = authenticate_google_calendar()
    if not service:
        logger.error("Google Calendar service is not available.")
        return

    for index, row in df.iterrows():
        try:
            reservation_date = row['Your Reservations']
            reservation_time = row['Your Reservations.1']
            activity = row['Activity']

            # Parse date and time to RFC3339 format
            start_time, end_time = parse_datetime(reservation_date, reservation_time)

            # Create the event summary
            summary = activity
            location = LOCATION

            # Create the calendar event
            create_calendar_event(service, summary, start_time, end_time, location=LOCATION)

        except Exception as e:
            logger.error(f"Failed to process row {index}: {e}")

if __name__ == '__main__':
    # Call the function with the variables
    df = get_booking_df()
    submit_events_from_dataframe(df)
