import subprocess
import sys
import os
import datetime
import re
import logging
from logging.handlers import RotatingFileHandler
import pytz

def clear_log_file(log_file):
    """Clear the contents of a log file."""
    with open(log_file, 'w') as f:
        f.write('')  # Write an empty string to clear the file

def setup_logger(name, log_file, level=logging.INFO):
    """Set up a logger that writes to a file, clearing the file first."""
    clear_log_file(log_file)
    
    handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Setup loggers
dep_logger = setup_logger('dependencies', 'dependencies.log')
conv_logger = setup_logger('converter', 'converter.log')

def update_pip():
    dep_logger.info("Updating pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        dep_logger.info("pip updated successfully.")
        return True
    except subprocess.CalledProcessError as e:
        dep_logger.error(f"Failed to update pip. Error: {str(e)}")
        return False

def install_dependencies():
    if not update_pip():
        return False
    
    dep_logger.info("Starting dependency installation...")
    dependencies = ['icalendar', 'pytz']
    for dep in dependencies:
        try:
            dep_logger.info(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            dep_logger.info(f"{dep} installed successfully.")
        except subprocess.CalledProcessError as e:
            dep_logger.error(f"Failed to install {dep}. Error: {str(e)}")
            return False
    dep_logger.info("All dependencies installed successfully.")
    return True

def check_dependencies():
    dep_logger.info("Checking dependencies...")
    try:
        import icalendar
        import pytz
        dep_logger.info("All dependencies are installed.")
        return True
    except ImportError as e:
        dep_logger.error(f"Dependency check failed. Error: {str(e)}")
        return False

def parse_appointment(appointment_str):
    pattern = r'(.+), (\w+ \d{1,2}(?:st|nd|rd|th)?, \d{4}), (\d{1,2}:\d{2} [AP]M) - (\d{1,2}:\d{2} [AP]M)'
    match = re.match(pattern, appointment_str)
    if match:
        return {
            'summary': match.group(1),
            'date': match.group(2),
            'start': match.group(3),
            'end': match.group(4)
        }
    conv_logger.warning(f"Failed to parse appointment: {appointment_str}")
    return None

def parse_datetime(date_str, time_str, timezone='America/New_York'):
    try:
        # Remove ordinal suffixes from the date string if present
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        
        # Try parsing with different format strings
        for fmt in ["%B %d, %Y", "%B %d %Y"]:
            try:
                dt = datetime.datetime.strptime(f"{date_str} {time_str}", f"{fmt} %I:%M %p")
                local_tz = pytz.timezone(timezone)
                return local_tz.localize(dt)
            except ValueError:
                continue
        
        # If we get here, none of the formats worked
        raise ValueError(f"Could not parse date and time: {date_str} {time_str}")
    
    except Exception as e:
        conv_logger.error(f"Error parsing datetime: {date_str} {time_str}. Error: {str(e)}")
        return None

def print_ics_contents(ics_data):
    print("\nContents of the generated ICS file:")
    print(ics_data.decode('utf-8'))
    print("End of ICS file contents\n")

def text_to_ics(file_path, timezone='America/New_York'):
    from icalendar import Calendar, Event, vText

    cal = Calendar()
    cal.add('prodid', '-//Chronos ICS//example.com//')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')

    event_count = 0
    try:
        with open(file_path, 'r') as file:
            for line_num, line in enumerate(file, 1):
                conv_logger.debug(f"Processing line {line_num}: {line.strip()}")
                appt = parse_appointment(line.strip())
                if appt:
                    event = Event()
                    event.add('summary', vText(appt['summary']))
                    start_dt = parse_datetime(appt['date'], appt['start'], timezone)
                    end_dt = parse_datetime(appt['date'], appt['end'], timezone)
                    if start_dt and end_dt:
                        event.add('dtstart', start_dt)
                        event.add('dtend', end_dt)
                        event.add('dtstamp', datetime.datetime.now(pytz.UTC))
                        event['uid'] = f"{start_dt.strftime('%Y%m%dT%H%M%S')}-{event_count}@example.com"
                        cal.add_component(event)
                        event_count += 1
                        conv_logger.info(f"Added event: {appt['summary']} on {start_dt}")
                    else:
                        conv_logger.warning(f"Skipped event due to datetime parsing error: {appt}")
    except FileNotFoundError:
        conv_logger.error(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        conv_logger.error(f"An error occurred while reading the file: {str(e)}")
        return None

    if event_count == 0:
        conv_logger.warning("No events were parsed from the file. Check if the file is empty or if the format matches the expected pattern.")
        return None

    conv_logger.info(f"Total events added: {event_count}")
    return cal.to_ical()

def main():
    global conv_logger, dep_logger  # Ensure we're using the global loggers
    
    if not check_dependencies():
        print("Updating pip and installing dependencies...")
        if not install_dependencies():
            print("Failed to update pip or install dependencies. Please check dependencies.log for details.")
            return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'appts.txt')
    timezone = 'America/New_York'

    if not os.path.exists(file_path):
        print(f"Error: 'appts.txt' not found in the script directory.")
        conv_logger.error(f"'appts.txt' not found in the script directory: {script_dir}")
        return

    conv_logger.info(f"Attempting to read from file: {file_path}")
    ics_data = text_to_ics(file_path, timezone)

    if ics_data:
        output_file = os.path.join(script_dir, 'appointments.ics')
        try:
            with open(output_file, 'wb') as f:
                f.write(ics_data)
            print(f"ICS file has been created successfully: {output_file}")
            conv_logger.info(f"ICS file has been created successfully: {output_file}")
            print_ics_contents(ics_data)  # Print the contents of the ICS file
        except Exception as e:
            print(f"Error writing to ICS file: {str(e)}")
            conv_logger.error(f"Error writing to ICS file: {str(e)}")
    else:
        print("Failed to create ICS data. Check the converter.log file for details.")

    print("Script execution completed. Check converter.log for detailed information.")

if __name__ == "__main__":
    main()