# TimeWatch URLs
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
CANT_FIND_CONFIGURATION_TEXT = "Could not find configuration file, initilizing ..."
CONFIGURATION_INITILIZED_TEXT = (
    "Configuration file initilized and saved to {path}/config.ini"
)
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
    ("start_time", "Time you start working (Default is 0900): ", "0900"),
    (
        "auto_end_time",
        "Automatically set end time (Reccomended, default is 'True')",
        "True",
    ),
    ("end_time", "Time you finish working (Default is 1800): ", "1800"),
]
