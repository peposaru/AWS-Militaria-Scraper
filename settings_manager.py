import os
import logging

# Default Settings
DEFAULT_RDS_SETTINGS = {
    "infoLocation"  : r'/home/ec2-user/projects/AWS-Militaria-Scraper/',
    "pgAdminCred"   : 'pgadminCredentials.json',
    "selectorJson"  : 'AWS_MILITARIA_SELECTORS.json',
    "s3Cred"        : 's3_credentials.json'
}

DEFAULT_PC_SETTINGS = {
    "infoLocation" : r'C:/Users/keena/Desktop/Cloud Militaria Scraper/Github Folder',
    "pgAdminCred"  : r'C:/Users/keena/Desktop/Cloud Militaria Scraper/pgadminCredentials.json',
    "selectorJson" : r'C:/Users/keena/Desktop/Cloud Militaria Scraper/Github Folder/AWS_MILITARIA_SELECTORS.json',
    "s3Cred"       : r'C:/Users/keena/Desktop/Cloud Militaria Scraper/s3_credentials.json'
}

# Which sites does the user want to process?
def site_choice(jsonData):
    print("Available sites:")
    for idx, site in enumerate(jsonData):
        print(f"{idx + 1}. {site['source']}")

    try:
        choice = input("Select sites to scrape (e.g., '1,3-5,7'): ")
        selected_indices = set()
        for part in choice.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                selected_indices.update(range(start - 1, end))
            else:
                selected_indices.add(int(part) - 1)

        selected_indices = sorted(selected_indices)
        if any(idx < 0 or idx >= len(jsonData) for idx in selected_indices):
            raise ValueError("One or more indices are out of range.")

        selected_sites = [jsonData[idx] for idx in selected_indices]
        return selected_sites
    except ValueError as e:
        logging.error(f"Invalid selection: {e}")
        return 

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
        settings["infoLocation"]  = input("Enter the directory path for configuration files (e.g., /path/to/config/): ").strip()
        settings["pgAdminCred"]   = input("Enter the name of the pgAdmin credentials file (e.g., pgadminCredentials.json): ").strip()
        settings["selectorJson"]  = input("Enter the name of the JSON selector file (e.g., AWS_MILITARIA_SELECTORS.json): ").strip()
        settings["s3Cred"]        = input("Enter the name of the s3 credentials file (e.g., s3_credentials.json): ").strip()

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
2. Run Availability Check (Check and update product availability)
3. Custom Check (Enter your own targetMatch and sleeptime)
""")
    check_choice = input("Enter your choice (1/2/3): ").strip()

    run_availability_check = False
    try:
        if check_choice == '1':
            targetMatch = 25
            sleeptime = 15 * 60  # 15 minutes in seconds
        elif check_choice == '2':
            targetMatch = None
            sleeptime = None
            run_availability_check = True
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

    return targetMatch, sleeptime, settings, run_availability_check


