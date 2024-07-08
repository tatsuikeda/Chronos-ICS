# Chronos ICS

Chronos ICS is a Python script that converts plain text appointments into ICS (iCalendar) format. This tool helps you manage your schedule by easily converting text-based appointment lists into a format that can be imported into most calendar applications.

## Features

- Converts text-based appointments to ICS format
- Automatic update of pip and installation of dependencies
- Reads appointments from a file named 'appts.txt' in the same directory as the script
- Detailed logging for both dependency management and conversion process
- Supports appointments with custom descriptions and flexible date formats
- Handles dates both with and without ordinal suffixes (e.g., "July 11th, 2024" and "July 11, 2024")

## Requirements

- Python 3.6 or higher

## Installation

1. Clone this repository or download the `chronos_ics.py` script.
2. Place the script in a directory of your choice.

## Usage

1. Create a text file named `appts.txt` in the same directory as the `chronos_ics.py` script.

2. In `appts.txt`, list your appointments, with each appointment on a new line following this format:
   ```
   Event Description, Month Day, Year, Start Time - End Time
   ```
   Examples:
   ```
   Shopping errand, July 11th, 2024, 3:00 PM - 4:00 PM
   Doctor's appointment, August 15, 2024, 10:30 AM - 11:30 AM
   ```
   Note: Both date formats (with or without ordinal suffixes) are supported.

3. Run the script:
   ```
   python chronos_ics.py
   ```

4. The script will automatically update pip, install required dependencies, read from `appts.txt`, and create an `appointments.ics` file in the same directory.

## Logging

The script creates two log files:
- `dependencies.log`: Contains information about the pip update and dependency installation process.
- `converter.log`: Contains detailed information about the conversion process, including any errors or warnings.

## Troubleshooting

If you encounter any issues, please check the log files for more detailed information. The most common problems are:
- `appts.txt` file missing from the script directory
- Appointments not formatted correctly in the input file
- Timezone issues (the script uses 'America/New_York' by default)
- Pip update or dependency installation failures

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/yourusername/chronos-ics/issues) if you want to contribute.

## License

[MIT](https://choosealicense.com/licenses/mit/)