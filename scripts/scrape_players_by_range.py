import os
import csv
from tqdm import tqdm
from urllib.parse import urljoin
from scripts.helper_classes.helper_functions import get_soup
from scripts.helper_classes.scrape_player_helper import scrape_player_page

BASE_URL = "https://afltables.com/afl/stats/"


# The yearly page contains all player stats for every team, this function will recursively call the scrape_player_page function
def scrape_players_by_range(start_year, end_year, directory):
    """
    Scrapes the yearly pages to find the stats for every player for a range of years.
    :param start_year: Starting year for scraping.
    :param end_year: Ending year for scraping.
    :param directory: Directory to store the subdirectories for each team and their respective CSV files.
    :return: None
    """
    for year in tqdm(range(start_year, end_year + 1), desc="Processing", ncols=100):
        tqdm.write("Current Year Being Processed: {}".format(year))

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