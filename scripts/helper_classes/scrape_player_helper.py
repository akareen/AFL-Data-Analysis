import csv, os
from datetime import datetime, timedelta

from scripts.helper_classes.helper_functions import get_soup
from scripts.helper_objects.row_titles import PLAYER_COL_TITLES

# This scrapes the individual player page to extract their performance for each round
def scrape_player_page(player_url, team_directory):
    """
    The player page contains a large number of numerical summaries.
    This code disregards the summaries as they can be created from the raw data.
    Thus it will focus on extracting the performance of the player for every round.
    :param player_url: URL of the player page
    :param team_directory: Directory to store the CSV file
    :return: None
    """
    soup = get_soup(player_url)
    if not soup:
        return

    personal_details = player_personal_details(soup)
    first_name = personal_details["first_name"]
    last_name = personal_details["last_name"]

    tables = soup.find_all('table')
    stats_file_name = f"{last_name.upper()}_{first_name.upper()}_STATS.csv"
    personal_file_name = f"{last_name.upper()}_{first_name.upper()}_PERSONAL.csv"
    stats_csv_file_path = os.path.join(team_directory, stats_file_name) # Create the CSV file path
    personal_csv_file_path = os.path.join(team_directory, personal_file_name) # Create the CSV file path
    
    # check if the file already exists
    if os.path.exists(stats_csv_file_path):
        i = 1
        while os.path.exists(stats_csv_file_path):
            stats_file_name = f"{last_name.upper()}_{first_name.upper()}_{i}__STATS.csv"
            stats_csv_file_path = os.path.join(team_directory, stats_file_name)
            personal_file_name = f"{last_name.upper()}_{first_name.upper()}_{i}_PERSONAL.csv"
            personal_csv_file_path = os.path.join(team_directory, personal_file_name)
            i += 1

    with open(stats_csv_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header_written = False  # flag to ensure header is written only once
        
        for table in tables: # iterate through all tables
            th_colspan_28 = table.find('th', colspan="28")
            if not th_colspan_28:
                continue

            team, year = th_colspan_28.text.strip().split(' - ')
            if not header_written:  # write header only if not already written
                header = ['team', 'year'] + PLAYER_COL_TITLES
                writer.writerow(header)
                header_written = True

            for row in table.tbody.find_all('tr'):
                # The arrow flags are used to show if they are interchanged but it is irrelevant for our purposes
                data = [team, year] + [td.text.strip().replace('↑', '').replace('↓', '') for td in row.find_all('td')]
                writer.writerow(data)

    with open(personal_csv_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header = ['first_name', 'last_name', 'born_date', 'debut_date', 'height', 'weight']
        writer.writerow(header)
        data = [personal_details["first_name"], personal_details["last_name"], personal_details["born_date"], personal_details["debut_date"], personal_details["height"], personal_details["weight"]]
        writer.writerow(data)


def scrape_player_page_for_all_players(player_url, directory):
    """
    This code differs from scrape_player_page() as it will use a unique identifier for the player.
    This is because it is being saved into a folder that contains all players ever.
    The way that the website and scraping is structured is that the player page has their performance for all time.
    However, the only way to access it is by year, to prevent duplication of data the unique identifier will mean that
    all the data is only scraped once for each visit and will prevent just a simple first and last name as there is duplicates.
    """
    soup = get_soup(player_url)
    if not soup:
        return
    
    personal_details = player_personal_details(soup)
    first_name = personal_details["first_name"]
    last_name = personal_details["last_name"]
    dob = personal_details["born_date"]

    stats_file_name = f"{last_name.upper()}_{first_name.upper()}_{dob}_STATS.csv"
    personal_file_name = f"{last_name.upper()}_{first_name.upper()}_{dob}_PERSONAL.csv"
    stats_csv_file_path = os.path.join(directory, stats_file_name) # Create the CSV file path
    personal_csv_file_path = os.path.join(directory, personal_file_name) # Create the CSV file path
    
    # check if the file already exists
    if os.path.exists(stats_csv_file_path):
        return

    tables = soup.find_all('table')
    with open(stats_csv_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header_written = False  # flag to ensure header is written only once
        
        for table in tables: # iterate through all tables
            th_colspan_28 = table.find('th', colspan="28")
            if not th_colspan_28:
                continue

            team, year = th_colspan_28.text.strip().split(' - ')
            if not header_written:  # write header only if not already written
                header = ['team', 'year'] + PLAYER_COL_TITLES
                writer.writerow(header)
                header_written = True

            for row in table.tbody.find_all('tr'):
                # The arrow flags are used to show if they are interchanged but it is irrelevant for our purposes
                data = [team, year] + [td.text.strip().replace('↑', '').replace('↓', '') for td in row.find_all('td')]
                writer.writerow(data)

    with open(personal_csv_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header = ['first_name', 'last_name', 'born_date', 'debut_date', 'height', 'weight']
        writer.writerow(header)
        data = [personal_details["first_name"], personal_details["last_name"], personal_details["born_date"], personal_details["debut_date"], personal_details["height"], personal_details["weight"]]
        writer.writerow(data)


# This extracts personal details of the player
def player_personal_details(soup):
    """
    Scrapes the player page to use the personal details when creating the player object
    returns a dictionary of: first_name, last_name, born_date, debut_date, height, weight
    """
    # Extract player's full name
    h1_tag = soup.find('h1')
    full_name = h1_tag.text.split()
    first_name = full_name[0]
    last_name = full_name[-1]

    # Extract the born date, debut age in years and days
    born_tag = soup.find('b', string='Born:')
    born_date_str = born_tag.next_sibling.strip().rstrip(' (')
    born_date = datetime.strptime(born_date_str, "%d-%b-%Y")
    

    debut_age_str = born_tag.find_next('b', string='Debut:').next_sibling.strip()
    debut_age_ls = debut_age_str.split()

    debut_years = int(debut_age_ls[0][:-1])
    debut_days = int(debut_age_ls[1][:-1]) if len(debut_age_ls) > 1 else 0

    # Calculate the debut date
    debut_date = born_date + timedelta(days=(debut_years * 365 + debut_days))
    debut_date = debut_date.strftime('%d-%m-%Y')
    born_date = born_date.strftime('%d-%m-%Y')

    # Extract height and weight details
    height_obj = soup.find('b', string='Height:')
    weight_obj = soup.find('b', string='Weight:')
    height_str = height_obj.next_sibling.strip() if height_obj else None
    weight_str = weight_obj.next_sibling.strip() if weight_obj else None
    
    height = int(height_str.split()[0]) if height_str else -1
    weight = int(weight_str.split()[0]) if weight_str else -1

    return {
        "first_name": first_name,
        "last_name": last_name,
        "born_date": born_date,
        "debut_date": debut_date,
        "height": height,
        "weight": weight
    }