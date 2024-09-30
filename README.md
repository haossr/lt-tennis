# LT-Tennis

LT-Tennis is an automation tool designed to simplify tennis court reservations. It uses Selenium to automate the booking process on the LT Club Automation platform.

## Features

- Automates the reservation process for tennis courts.
- Supports multiple start times for flexibility.
- Configurable for retries if the preferred time slots are not available.
- Customizable court durations for different types of bookings.

## Prerequisites

- Python 3.x
- [Selenium](https://www.selenium.dev/) WebDriver
- ChromeDriver or another WebDriver compatible with Selenium

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/haossr/lt-tennis.git
   cd lt-tennis
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Download and install the appropriate WebDriver (e.g., ChromeDriver):

   - [Download ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)

   Ensure the WebDriver is accessible from your system's `PATH`.

## Usage

1. Set the environment variables for your LT Club credentials:

   ```bash
   export LT_USERNAME="your_username"
   export LT_PASSWORD="your_password"
   ```

2. Run the script with the desired options:

   ```bash
   python booking.py --reservation_date 10/06/2024 --start_time_text 8:30am 8:00am 9:00am --max_attempts 3 --interval_duration 90
   ```

   Options:
   - `--reservation_date`: The date for the reservation in `MM/DD/YYYY` format.
   - `--start_time_text`: A list of preferred start times for the reservation.
   - `--max_attempts`: Maximum number of attempts to retry finding an available slot.
   - `--interval_duration`: Duration of the reservation in minutes (e.g., 90).

3. (Optional) Set up a scheduled cron job to automate the reservation process at specific times (e.g., daily or weekly).

## Example

To automate a booking for the next Saturday:

```bash
reservation_date=$(date -d "next saturday" +"%m/%d/%Y")
python booking.py --reservation_date "$reservation_date" --start_time_text 8:30am 8:00am 9:00am --max_attempts 3 --interval_duration 90
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```