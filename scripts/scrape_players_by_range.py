import os
import csv
from urllib.parse import urljoin
from scripts.helper_functions import get_soup

BASE_URL = "https://afltables.com/afl/stats/"

# This scrapes the individual player page to extract their performance for each round
def scrape_player_page(player_url, team_directory):
    """
    The player page contains a large number of nnumerical summaries.
    This code disregards the summaries as they can be created from the raw data.
    Thus it will focus on extracting the performance of the player for every round.
    :param player_url: URL of the player page
    :param team_directory: Directory to store the CSV file
    :return: None
    """
    soup = get_soup(player_url)
    if not soup:
        return

    tables = soup.find_all('table')
    player_name = player_url.split('/')[-1].replace('.html', '') # Extract the player name from the URL
    csv_file_path = os.path.join(team_directory, f"{player_name}.csv") # Create the CSV file path

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header_written = False  # flag to ensure header is written only once
        
        for table in tables: # iterate through all tables
            th_colspan_28 = table.find('th', colspan="28")
            if not th_colspan_28:
                continue

            team, year = th_colspan_28.text.strip().split(' - ')
            if not header_written:  # write header only if not already written
                header = ['Team', 'Year'] + [th.text.strip() for th in table.find_all('tr')[1].find_all('th')]
                writer.writerow(header)
                header_written = True

            for row in table.tbody.find_all('tr'):
                # The arrow flags are used to show if they are interchanged but it is irrelevant for our purposes
                data = [team, year] + [td.text.strip().replace('↑', '').replace('↓', '') for td in row.find_all('td')]
                writer.writerow(data)


# The yearly page contains all player stats for every team, this function will recursively call the scrape_player_page function
def scrape_players_by_range(start_year, end_year, directory):
    """
    Scrapes the yearly pages to find the stats for every player for a range of years.
    :param start_year: Starting year for scraping.
    :param end_year: Ending year for scraping.
    :param directory: Directory to store the subdirectories for each team and their respective CSV files.
    :return: None
    """
    for year in range(start_year, end_year + 1):
        URL = f"{BASE_URL}{year}.html"
        soup = get_soup(URL)
        if not soup:
            continue

        year_directory = os.path.join(directory, str(year))
        for table in soup.find_all('table', class_='sortable'):
            team_link = table.find('a', href=lambda x: x and x.startswith('../teams/'))
            if not team_link:
                continue

            team_name = team_link.text.strip()
            team_directory = os.path.join(year_directory, team_name)
            os.makedirs(team_directory, exist_ok=True)

            for row in table.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) > 1:
                    player_link = cols[1].find('a', href=lambda x: x and x.startswith('players/'))
                    if player_link:
                        player_url = urljoin(BASE_URL, player_link['href'])
                        scrape_player_page(player_url, team_directory)