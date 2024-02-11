# TimeWatch URLs
TIMEWATCH_BASE_URL = "https://c.timewatch.co.il"
TIMEWATCH_USER_VALIDATION_URL = "https://c.timewatch.co.il/user/validate_user.php"
TIMEWATCH_DATE_TABLE_URL = "https://c.timewatch.co.il/punch/editwh.php"
TIMEWATCH_HOUR_UPDATE_URL = "https://c.timewatch.co.il/punch/editwh3.php"
# Strings
UPDATE_HOURS_LINK_TEXT = "עדכון נתוני נוכחות"
HOURS_UPDATE_REQUIRED_TEXT = "חסרה כניסה/יציאה"
LOGGING_IN_TEXT = "Logging into TimeWatch..."
START_FILL_HOURS_TEXT = "Found {num_dates} missing dates! Filling..."
FULLY_FILLED_TEXT = "Time card is fully filled!"
TIMEWATCH_SET_TIME_ISSUE_TEXT = "limited punch"
MAX_RETIRES_TEXT = "Tried filling date 5 times and still failing, please check manually"
MISSING_DATES_RETRY_TEXT = "You still have missing dates, trying again ..."
SUBMITTING_HOURS_TEXT = (
    "Submitting hours, date={date}, start_time={start_time}, end_time={end_time}"
)
UNABLE_TO_FILL_TEXT = (
    "Unable to fill date. Probably a bug on TimeWatch, please verify manually"
)
CANT_FIND_CONFIGURATION_TEXT = "Could not find configuration file, initializing ..."
CONFIGURATION_INITIALIZED_TEXT = (
    "Configuration file initialized and saved to {path}/config.ini"
)
LAUNCHD_INITIALIZED_TEXT = "Created new launchd file at {path}"
# Configurations
CONFIG_FILE_PATH = "~/Library/Preferences/TimeWatcher"
AUTHENTICATION = "authentication"
PREFERENCES = "preferences"
AUTHENTICATION_VALUES = [
    (
        "company_number",
        "Enter Company Number (Press enter for Rapid7 - 4630): ",
        "4630",
    ),
    ("employee_number", "[MANDATORY] Enter Employee Number: ", None),
    ("employee_password", "[MANDATORY] Enter Employee Password (Your ID): ", None),
]
PREFERENCES_VALUES = [
    (
        "auto_execute",
        "Do you want to run this program automatically for you? (Default is 'True'): ",
        "True",
    ),
    (
        "day_to_execute",
        "If you chose to run automatically, which day do you want to execute on? Insert only digits. (Default is 12th of each month): ",
        "12",
    ),
    (
        "hour_to_execute",
        "If you chose to run automatically, which hour in the day you want to exeucte on?? Insert only digits. (Default is 11 (11 A.M)): ",
        "11",
    ),
    ("start_time", "Time you start working (Default is 0900): ", "0900"),
    (
        "auto_end_time",
        "Automatically set end time (Reccomended, default is 'True')",
        "True",
    ),
    ("end_time", "Time you finish working (Default is 1800): ", "1800"),
]
LAUNCH_AGENT_FILE_NAME = "com.birkagal.timewatcher.plist"
LAUNCH_AGENT_FILE_PATH = f"~/Library/LaunchAgents/{LAUNCH_AGENT_FILE_NAME}"
LAUNCH_AGENT_FILE_CONTENT = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.birkagal.timewatcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>mkdir</string>
        <string>-p</string>
        <string>~/Library/Logs/TimeWatcher</string>
        <string>&amp;&amp;</string>
        <string>timewatcher</string>
        <string>>></string>
        <string>~/Library/Logs/TimeWatcher/logs</string>
        <string>2&gt;&amp;1</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Day</key>
        <integer>{day_to_execute}</integer>
        <key>Hour</key>
        <integer>{hour_to_execute}</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
"""
