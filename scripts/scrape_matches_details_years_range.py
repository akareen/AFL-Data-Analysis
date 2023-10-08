import csv, os
from datetime import datetime
from tqdm import tqdm
from urllib.parse import urljoin

from scripts.helper_classes.helper_functions import get_soup
from scripts.helper_classes.match_extraction_helper import extract_match_info

from scripts.helper_objects.translation import AFL_TEAM_CODES
from scripts.helper_objects.row_titles import MATCH_COL_TITLES
from scripts.helper_objects.row_titles import PLAYER_COL_TITLES


# Peforms the web scraping integrating all the functions stores the data in a CSV file for each year
def scrape_matches_page_directory(start_year=1897, end_year=datetime.now().year, directory='data/match_details'):
    """
    It will scrape all the match details from the start year to the end year
    The match details include the game stats and team stats for each team
    :param start_year: start year
    :param end_year: end year
    :param directory: directory to store the CSV files
    :return: None
    """

    MATCH_URL_TEMPLATE = 'https://afltables.com/afl/seas/{}.html'
    os.makedirs(directory, exist_ok=True) # Ensure the directory exists

    for year in tqdm(range(start_year, end_year + 1), desc="Processing", ncols=100):
        
        # Update the description to include the current year being processed
        tqdm.write("Current Year Being Processed: {}".format(year))
        
        url = MATCH_URL_TEMPLATE.format(year)
        year_directory = os.path.join(directory, str(year))
        game_stats_directory = os.path.join(year_directory, 'gamestats')
        team_stats_directory = os.path.join(year_directory, 'teamstats')
        
        os.makedirs(year_directory, exist_ok=True)
        os.makedirs(game_stats_directory, exist_ok=True)
        os.makedirs(team_stats_directory, exist_ok=True)
        
        soup = get_soup(url)
        curr_round = 1

        # Iterating through sections and games
        for section in soup.find_all('td', {'width': '85%', 'valign': 'top'}):
            round_name = section.find_previous('a', {'name': True}).get('name')
            i = 1
            for game in section.find_all('table', recursive=False):
                rows = game.find_all('tr', recursive=False)
                process_rows(rows, game_stats_directory, team_stats_directory, round_name, str(year))
                i += 1
            curr_round += 1

        # Process final round section
        final_round_section = soup.find('a', {'name': 'fin'}).find_next_sibling('table').find_next_sibling('table')
        process_final_round_section(final_round_section, game_stats_directory, team_stats_directory, year)


# Extract data from rows and write to CSV
def process_rows(rows, game_stats_directory, team_stats_directory, round_name, year='2023'):
    """
    Extracts all relevant data from rows and writes it to the CSV
    :param rows: rows from the table
        rows begins in the format [<tr><td><a>Home Team</a></td><td width="20%">3.2 4.3 5.4 6.5</td><td>Extra Info</td></tr>,
                                   <tr><td><a>Away Team</a></td><td width="20%">3.2 4.3 5.4 6.5</td><td>Extra Info</td></tr>]
    :param writer: csv writer
    :param round_name: name of the round
    :param year: year of the round
    :return: None
    """

    match_info = extract_match_info(rows)
    if match_info is None:
        return

    match_stats_link = match_info['match_stats_link']
    del match_info['match_stats_link']

    home_code = AFL_TEAM_CODES[match_info['home_team'].lower()]
    away_code = AFL_TEAM_CODES[match_info['away_team'].lower()]
    game_stats_file_name = f"{year}_{round_name}_{home_code}_{away_code}_GAMESTATS.csv"
    home_stats_file_name = f"{year}_{round_name}_{home_code}_{away_code}_TEAMSTATS_{home_code}.csv"
    away_stats_file_name = f"{year}_{round_name}_{home_code}_{away_code}_TEAMSTATS_{away_code}.csv"

    file_path = os.path.join(game_stats_directory, game_stats_file_name)

    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Writing header
        writer.writerow(MATCH_COL_TITLES)
        keys_in_order = [
            "venue", "date", "attendance", "home_team", "away_team",
            "home_goals", "home_behinds", "away_goals", "away_behinds",
            "sum_home_goals", "sum_home_behinds", "home_total_score",
            "sum_away_goals", "sum_away_behinds", "away_total_score",
            "winning_team", "margin"
        ]

        values_in_order = []
        for key in keys_in_order:
            if key in ["home_goals", "away_goals", "home_behinds", "away_behinds"]:
                values_in_order.extend(match_info[key])  # Unpack the list
            else:
                values_in_order.append(match_info[key])
        values_in_order = [year, round_name, *values_in_order]
        writer.writerow(values_in_order)

    if match_stats_link != "empty":
        base_url = 'https://afltables.com/afl'
        if match_stats_link.startswith('../'):
            match_stats_link = '/afl' + match_stats_link[2:]

        full_url = urljoin(base_url, match_stats_link)
        process_match_details(full_url, match_info['home_team'], match_info['away_team'], team_stats_directory, year, round_name, home_stats_file_name, away_stats_file_name)


# Processes the match details page
def process_match_details(match_stats_link, home_team, away_team, team_stats_directory, year, round_name, home_file_path, away_file_path):
    """
    This function is used to extract the details that have occured in the game such as all player stats for each team
    :param match_stats_link: link to the match stats page
    :param home_team: home team name
    :param away_team: away team name
    :param team_stats_directory: directory to store the CSV files
    :param year: year of the round
    :param round_name: name of the round
    :param home_file_path: file path for home team stats
    :param away_file_path: file path for away team stats
    :return: None
    """
    match_details_soup = get_soup(match_stats_link)
    if not match_details_soup:
        return
    team_tables = match_details_soup.find_all(class_='sortable', limit=2)
    data = [[team_tables[0], home_team], [team_tables[1], away_team]]
    i = 0
    for team in data:
        table = team[0]
        team_name = team[1]
        opposition_name = home_team if team_name == away_team else away_team
        file_path = home_file_path if i == 0 else away_file_path

        csv_file_path = os.path.join(team_stats_directory, file_path)

        th_elements = table.find('thead').find('th', string='#').find_all_next('th')
        headers = ['#']
        headers.extend([th.get_text() for th in th_elements])
        header = ["year", "round_name", "team_name", "opposition_name", "jersey_num", "player_name", *PLAYER_COL_TITLES[5:]]

        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)

            for row in table.find('tbody').find_all('tr'):
                data = [td.get_text() for td in row.find_all('td')]
                writer.writerow([year, round_name, team_name, opposition_name, *data[:25]])
        i += 1


# Process the final round section
def process_final_round_section(final_round_section, game_stats_directory, team_stats_directory, year):
    """
    Processes the final round section which differs from the main sections
    :param final_round_section: final round section
        final_round_section begins in the format <table><tr><td><b>Final Round</b></td></tr></table>
        It contains the final round name and the game table
    :param writer: csv writer
    :param year: year of the round
    :return: None
    """
    while final_round_section:
        final_round_name = final_round_section.find('b')
        if final_round_name:
            final_round_name = ''.join([c for c in final_round_name.text if c.isupper()])
            game_table = final_round_section.find_next_sibling('table')
            if game_table:
                rows = game_table.find_all('tr', recursive=False)
                process_rows(rows, game_stats_directory, team_stats_directory, final_round_name, str(year))
                final_round_section = game_table.find_next_sibling('table') if game_table else None
            else:
                final_round_section = None
        else:
            final_round_section = final_round_section.find_next_sibling('table')
