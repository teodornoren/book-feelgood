# book-feelgood

This Python script is designed to automate the booking process for activities on the FeelGood platform. It allows you to book or unbook activities with ease. Below, you'll find instructions on how to use this script effectively.

## Prerequisites

Before using this script, make sure you have the following prerequisites:

- Python 3.x installed on your system.
- Required Python packages installed. You can install them using `pip`:
  ```bash
  pip install requests
  ```

## Usage

You can run the script by executing the following command:

```bash
python booking_script.py -usr <your_username> -pw <your_password> -act <activities_file> -tst <test_mode> -t <time> -n <name> -d <day> -do <day_offset> -st <start_time>
```

### Command-Line Arguments

- `-usr` or `--username`: Your FeelGood username (required).
- `-pw` or `--password`: Your FeelGood password (required).
- `-act` or `--activities_file`: The name of the YAML file containing the list of activities to book (optional).
- `-tst` or `--test`: Run in test mode (optional). If specified, no actual booking will be made.
- `-t` or `--time`: An optional time to specify instead of using the configuration (optional).
- `-n` or `--name`: An optional name to specify instead of using the configuration (optional).
- `-d` or `--day`: An optional day to specify instead of using the configuration (optional).
- `-do` or `--day-offset`: An optional day offset to specify instead of using the configuration (optional).
- `-st` or `--start-time`: Optional start time for "Boka" activities (optional).

### Example Usage

Here are some example usages of the script:

1. Book activities using a specified activities file:

```bash
python booking_script.py -usr your_username -pw your_password -act activities_file
```

2. Book a specific activity manually:

```bash
python booking_script.py -usr your_username -pw your_password -n Yoga -t 18:30 -d Monday
```

3. Test the script without making actual bookings:

```bash
python booking_script.py -usr your_username -pw your_password -act activities_file -tst True
```

## Configuration

The script uses YAML configuration files for activities and settings. The configuration files are located in the `config` and `activities` directories. Ensure these files are correctly set up for your FeelGood account and activities.

## Important Notes
- The script may require periodic updates to match changes in the FeelGood platform's structure or authentication mechanisms.

Feel free to reach out if you have any questions or encounter any issues while using this script. Happy booking!

## yaml layout
```yaml
---
day_offset: <day_offset>
facility: <facility_uuid>
activities:
  - name: <activity_1>
    time: "<time>"
    day: <week_day>
  - name: <activity_2>
    time: "<time>"
    day: <week_day>
```
See the [activities](activities) directory for examples.

#### reminder to self:

##### Booking and unbooking 
base url for book/unbook:\
https://feelgood.wondr.se/w_booking\
how to unbook:\
    /activities/cancel/<activity_code>/1?force=1\
how to book:\
    /activities/participate/<activity_code>/?force=1\


