import os
import logging
import argparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get username and password from environment variables
username = os.getenv("LT_USERNAME")
password = os.getenv("LT_PASSWORD")

if not username or not password:
    logging.error("Please set LT_USERNAME and LT_PASSWORD environment variables.")
    exit(1)

def make_reservation(reservation_date, start_time_text_list, max_attempts, interval_duration):
    global username, password  # Use global variables for username and password

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

        # Wait until date input field is clickable and enter date
        date_field = wait.until(EC.element_to_be_clickable((By.ID, "date")))
        date_field.clear()
        date_field.send_keys(reservation_date)
        logging.info(f"Entered reservation date: {reservation_date}.")

        # Select duration (use interval_duration argument)
        duration_radio = driver.find_element(By.ID, f"interval-{interval_duration}")
        duration_parent = duration_radio.find_element(By.XPATH, "./..")
        duration_parent.click()
        logging.info(f"Selected duration: {interval_duration} minutes.")

        # Click search button
        search_button = wait.until(EC.element_to_be_clickable((By.ID, "reserve-court-search")))
        search_button.click()
        logging.info("Clicked search button.")
      
        # Check if any of the start times in start_time_text_list appears, try up to max_attempts times
        attempt = 0
        found_start_time = False

        while attempt < max_attempts:
            try:
                for start_time_text in start_time_text_list:
                    try:
                        # Wait for a matching start time link to appear (short wait time)
                        logging.info(f"Looking for start time {start_time_text}...")
                        start_time_link = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{start_time_text}')]"))
                        )
                        found_start_time = True
                        logging.info(f"Found start time {start_time_text} on attempt {attempt + 1}.")
                        start_time_link.click()
                        break  # Exit inner loop if a start time is found

                    except Exception as e:
                        continue  # Continue to the next start time in the list
                attempt += 1
                logging.info(f"Attempt {attempt}: Start time not found, retrying in 5 seconds...")
            except Exception as e:
                logging.warning(f"An error occurred: {e}")
                attempt += 1
                logging.info(f"Attempt {attempt}: Start time not found, retrying in 5 seconds...")
                search_button = wait.until(EC.element_to_be_clickable((By.ID, "reserve-court-search")))
                search_button.click()

        if not found_start_time:
            logging.info(f"After {max_attempts} attempts, none of the start times were found: {start_time_text_list}.")
            exit(0)

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

if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Reserve tennis court via Selenium automation.")
    parser.add_argument('--reservation_date', required=True, help="Target reservation date in MM/DD/YYYY format.")
    parser.add_argument('--start_time_text', nargs='+', required=True, help="List of start times to check, e.g., '8:00am 8:30am'.")
    parser.add_argument('--max_attempts', type=int, required=True, help="Maximum number of attempts to find the start time.")
    parser.add_argument('--interval_duration', type=int, required=True, help="Duration of the reservation in minutes, e.g., '90'.")

    # Parse arguments
    args = parser.parse_args()

    # Call the function with the parsed arguments
    make_reservation(args.reservation_date, args.start_time_text, args.max_attempts, args.interval_duration)