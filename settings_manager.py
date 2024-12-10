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
        - targetMatch (int or None): The number of target matches (if applicable).
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

    # Second question: Run availability check
    print("""
Would you like to run the product availability check?
1. Yes
2. No
""")
    availability_choice = input("Enter your choice (1/2): ").strip()
    run_availability_check = availability_choice == '1'

    # Third question: Choose targetMatch setting (only if not running availability check)
    targetMatch = None
    if not run_availability_check:
        print("""
Choose your targetMatch setting:
1. Quick Site Check (25)
2. All Products (99999)
3. Custom (enter your own value)
""")
        try:
            choice = input("Enter the number corresponding to your choice (1/2/3): ").strip()
            if choice == '1':
                targetMatch = 25
            elif choice == '2':
                targetMatch = 99999
            elif choice == '3':
                targetMatch = int(input("Enter your desired targetMatch value: ").strip())
            else:
                raise ValueError
        except ValueError:
            print("Invalid input. Defaulting TargetMatch to 25.")
            logging.warning("Invalid targetMatch input. Defaulting to 25.")
            targetMatch = 25

    return targetMatch, settings, run_availability_check

