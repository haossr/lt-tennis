import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)

# Global variables
reservation_date = "10/04/2024"  # Target date in MM/DD/YYYY format
start_time_text = "8:00am"       # Start time, e.g., '8:00am'
max_attempts = 100               # Maximum number of attempts

# Get username and password from environment variables
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

if not username or not password:
    logging.error("Please set USERNAME and PASSWORD environment variables.")
    exit(1)

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
    wait.until(EC.presence_of_element_located((By.ID, "main-menu")))
    logging.info("Login successful.")

    # Navigate to reservation page
    driver.get("https://lt.clubautomation.com/event/reserve-court-new")
    logging.info("Navigated to reservation page.")

    # Wait until date input field is clickable and enter date
    date_field = wait.until(EC.element_to_be_clickable((By.ID, "date")))
    date_field.clear()
    date_field.send_keys(reservation_date)
    logging.info(f"Entered reservation date: {reservation_date}.")

    # Select duration
    duration_radio = wait.until(EC.element_to_be_clickable((By.ID, "interval-120")))
    # Click parent element to ensure interaction is successful
    duration_parent = duration_radio.find_element(By.XPATH, "./..")
    duration_parent.click()
    logging.info("Selected duration.")

    # Click search button
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "reserve-court-search")))
    search_button.click()
    logging.info("Clicked search button.")

    # Check if start time appears, try up to max_attempts times, wait 5 seconds between attempts
    attempt = 0
    found_start_time = False

    while attempt < max_attempts:
        try:
            # Wait for start time link to appear (short wait time)
            start_time_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{start_time_text}')]"))
            )
            found_start_time = True
            logging.info(f"Found start time {start_time_text} on attempt {attempt + 1}.")
            break  # Found start time, exit loop
        except:
            attempt += 1
            logging.info(f"Attempt {attempt}: Start time {start_time_text} not found, retrying in 5 seconds...")
            time.sleep(5)
            # Optionally refresh page or click search button again
            # driver.refresh()
            # search_button.click()

    if not found_start_time:
        logging.error(f"After {max_attempts} attempts, start time {start_time_text} was not found.")
        exit(1)

    # Found start time, click link
    start_time_link.click()
    logging.info("Clicked on start time link.")

    # Confirm reservation
    confirm_button = wait.until(EC.element_to_be_clickable((By.ID, "confirm")))
    confirm_button.click()
    logging.info("Confirmed reservation.")

    # Complete reservation
    ok_button = wait.until(EC.element_to_be_clickable((By.ID, "button-ok")))
    ok_button.click()
    logging.info("Completed reservation.")

    # Get reservation list table
    table_element = wait.until(EC.presence_of_element_located((By.ID, "table-reservation-list")))
    table_html = table_element.get_attribute('outerHTML')
    logging.info("Retrieved reservation list.")

    # Parse HTML table using pandas
    dfs = pd.read_html(table_html)
    reservation_df = dfs[0]

    # Output reservation information
    print(reservation_df)

except Exception as e:
    logging.error(f"An error occurred: {e}")
finally:
    driver.quit()
    logging.info("Closed browser driver.")