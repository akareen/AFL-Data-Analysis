import os
from urllib.parse import urljoin
from scripts.scrape_players_by_range import scrape_player_page
from scripts.helper_functions import get_soup

# Scrape the AFL Tables website to find the stats for every player
def scrape_all_players_ever(start_url='https://afltables.com/afl/afl_index.html', directory='data/team_stats_players_all_time'):
    """
    Main function that performs the scraping
    It will scrape the stats for every player that has ever played in the VFL/AFL
    The function will store the player stats in a CSV file in the directory for each team
    they have played in
    :param start_url: URL to start scraping from
    :param directory: Directory to store the CSV files
    :return: None
    """
    BASE_LINK = "https://afltables.com/afl/"
    soup = get_soup(start_url)
    if not soup:
        return
    
    # Find all team links on the main page
    for a in soup.find_all('a', href=lambda x: x and 'teams/' in x):
        intermediate_team_url = urljoin(BASE_LINK, a['href'])
        
        # Follow the intermediate team link
        intermediate_team_soup = get_soup(intermediate_team_url)
        if not intermediate_team_soup:
            continue
        
        # Find the first link with 'stats/teams'
        stats_link = intermediate_team_soup.find('a', href=lambda x: x and 'stats/teams' in x)
        if not stats_link:
            continue
        
        # Construct the final team stats URL explicitly
        final_team_stats_url = BASE_LINK + stats_link['href'].replace('../', '')
        final_team_stats_soup = get_soup(final_team_stats_url)
        if not final_team_stats_soup:
            continue
        
        team_name = os.path.basename(final_team_stats_url).replace('.html', '')
        team_directory = os.path.join(directory, team_name)
        os.makedirs(team_directory, exist_ok=True)

        # Follow the final team stats URL and scrape every href starting with '../players'
        for player_link in final_team_stats_soup.find_all('a', href=lambda x: x and x.startswith('../players')):
            player_url = urljoin(final_team_stats_url, player_link['href'])
            scrape_player_page(player_url, team_directory)

