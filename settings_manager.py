import os
import logging

import os
import logging

# Default Settings
DEFAULT_RDS_SETTINGS = {
    "infoLocation": r'/home/ec2-user/projects/AWS-Militaria-Scraper/',
    "pgAdminCred": 'pgadminCredentials.json',
    "selectorJson": 'AWS_MILITARIA_SELECTORS.json'
}

DEFAULT_PC_SETTINGS = {
    "infoLocation": r'C:/Users/keena/Desktop/Cloud Militaria Scraper/Github Folder',
    "pgAdminCred": r'C:/Users/keena/Desktop/Cloud Militaria Scraper/pgadminCredentials.json',
    "selectorJson": r'C:/Users/keena/Desktop/Cloud Militaria Scraper/Github Folder/AWS_MILITARIA_SELECTORS.json'
}

def get_user_settings():
    """
    Prompt user to select settings for infoLocation, pgAdmin credentials, and selector JSON file.
    Returns:
        - targetMatch (int or None): The number of target matches.
        - sleeptime (int): The sleep time between cycles (in seconds).
        - settings (dict): A dictionary with keys 'infoLocation', 'pgAdminCred', 'selectorJson'.
        - run_availability_check (bool): Indicates whether the user wants to run the availability check.
    """
    # First question: Choose settings
    print("""
Choose your settings:
1. Amazon RDS Settings
2. Personal Computer Settings
3. Custom Settings
""")
    choice = input("Enter the number corresponding to your choice (1/2/3): ").strip()

    settings = {}
    if choice == '1':
        print("Using Amazon RDS Settings...")
        settings = DEFAULT_RDS_SETTINGS

    elif choice == '2':
        print("Using Personal Computer Settings...")
        settings = DEFAULT_PC_SETTINGS

    elif choice == '3':
        print("Custom settings selected.")
        # Prompt user for custom settings
        settings["infoLocation"] = input("Enter the directory path for configuration files (e.g., /path/to/config/): ").strip()
        settings["pgAdminCred"] = input("Enter the name of the pgAdmin credentials file (e.g., pgadminCredentials.json): ").strip()
        settings["selectorJson"] = input("Enter the name of the JSON selector file (e.g., AWS_MILITARIA_SELECTORS.json): ").strip()

        # Validate the directory exists
        if not os.path.exists(settings["infoLocation"]):
            print(f"Error: The directory {settings['infoLocation']} does not exist.")
            logging.error(f"Invalid directory entered: {settings['infoLocation']}")
            exit()

    else:
        print("Invalid choice. Exiting program.")
        exit()

    # Second question: Select check type
    print("""
Choose the type of inventory check:
1. New Inventory Check (targetMatch = 25, sleeptime = 15 minutes)
2. Whole Inventory Check (targetMatch = 99999, sleeptime = 0 seconds)
3. Custom Check (Enter your own targetMatch and sleeptime)
""")
    check_choice = input("Enter your choice (1/2/3): ").strip()

    try:
        if check_choice == '1':
            targetMatch = 25
            sleeptime = 15 * 60  # 15 minutes in seconds
        elif check_choice == '2':
            targetMatch = 99999
            sleeptime = 0
        elif check_choice == '3':
            targetMatch = int(input("Enter your desired targetMatch value: ").strip())
            sleeptime = int(input("Enter your desired sleeptime value (in seconds): ").strip())
        else:
            raise ValueError
    except ValueError:
        print("Invalid input. Defaulting to New Inventory Check.")
        logging.warning("Invalid input for inventory check. Defaulting to targetMatch=25, sleeptime=15 minutes.")
        targetMatch = 25
        sleeptime = 15 * 60

    return targetMatch, sleeptime, settings

