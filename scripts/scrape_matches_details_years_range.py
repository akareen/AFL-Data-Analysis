from datetime import datetime
import csv
import os
from scripts.helper_functions import get_soup
from scripts.scrape_matches_years_range import determine_winner, unpack_team_scores, extract_extra_info, extract_data
from urllib.parse import urljoin

COLUMN_TITLES = ['Year', 'Round', 'Home Team', 'Away Team',
                'H Goals 1st', 'H Goals 2nd', 'H Goals 3rd', 'H Goals 4th',
                'H Behind 1st', 'H Behind 2nd', 'H Behind 3rd', 'H Behind 4th',
                'H Total Goals', 'H Total Behind', 'H Total Score',
                'A Goals 1st', 'A Goals 2nd', 'A Goals 3rd', 'A Goals 4th',
                'A Behind 1st', 'A Behind 2nd', 'A Behind 3rd', 'A Behind 4th',
                'A Total Goals', 'A Total Behind', 'A Total Score',
                'Winning Team', 'Margin', 'Date', 'Attendance', 'Venue']


# Peforms the web scraping integrating all the functions stores the data in a CSV file for each year
def scrape_matches_page_directory(start_year=1897, end_year=datetime.now().year, directory='data/match_details'):
    """
    Main function that performs the scraping
    :return: None
    """

    MATCH_URL_TEMPLATE = 'https://afltables.com/afl/seas/{}.html'

    os.makedirs(directory, exist_ok=True) # Ensure the directory exists
    for year in range(start_year, end_year + 1):
        url = MATCH_URL_TEMPLATE.format(year)

        year_directory = os.path.join(directory, str(year))
        soup = get_soup(url)
        
        
        curr_round = 1
        # Iterating through sections and games
        for section in soup.find_all('td', {'width': '85%', 'valign': 'top'}):
            round_name = section.find_previous('a', {'name': True}).get('name')
            i = 1
            for game in section.find_all('table', recursive=False):
                game_directory = os.path.join(year_directory, f'round_{round_name}_game_{i}')
                os.makedirs(game_directory, exist_ok=True)
                rows = game.find_all('tr', recursive=False)
                process_rows(rows, game_directory, round_name, str(year))
                i += 1
            curr_round += 1
        
        # Process final round section
        final_round_section = soup.find('a', {'name': 'fin'}).find_next_sibling('table').find_next_sibling('table')
        process_final_round_section(final_round_section, year_directory, curr_round, year)
            

# Extract data from rows and write to CSV
def process_rows(rows, game_directory, round_name, year='2023'):
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

    match_stats_link = None

    # Process home and away rows
    for row_type in ["home", "away"]:
        row = rows[0] if row_type == "home" else rows[1]
        if row.find('td', {'width': '20%'}) is None:
            return
        team, scores, extra_info = extract_data(row)
        
        goals, behinds = unpack_team_scores(scores[:4])
        total_goals, total_behinds = sum(goals), sum(behinds)
        total_score = total_goals * 6 + total_behinds
        
        if row_type == "home":
            home_team, home_total_score = team, total_score
            home_goals, home_behinds = goals, behinds
            date, attendance, venue = extract_extra_info(extra_info)
        else:
            away_team, away_total_score = team, total_score
            away_goals, away_behinds = goals, behinds

        if row_type == "away":
            a_tag = row.find('a', href=lambda href: href and href.startswith('../stats/games'))
            if a_tag:
                match_stats_link = a_tag['href']
            
    winning_team = determine_winner(home_team, home_total_score, away_team, away_total_score)
    margin = abs(home_total_score - away_total_score)
    
    display_name_home = '_'.join(word.lower() for word in home_team.split())
    display_name_away = '_'.join(word.lower() for word in away_team.split())
    file_name = os.path.join(game_directory, f'{display_name_home}_{display_name_away}_game_stats.csv')
    os.makedirs(game_directory, exist_ok=True)
    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Writing header
        writer.writerow(COLUMN_TITLES)
        writer.writerow([year, round_name, home_team, away_team,
                        *home_goals, *home_behinds, sum(home_goals), sum(home_behinds), home_total_score,
                        *away_goals, *away_behinds, sum(away_goals), sum(away_behinds), away_total_score,
                        winning_team, margin, date, attendance, venue])

    if match_stats_link is not None:
        base_url = 'https://afltables.com/afl'
        if match_stats_link.startswith('../'):
            match_stats_link = '/afl' + match_stats_link[2:]

        full_url = urljoin(base_url, match_stats_link)
        process_match_details(full_url, home_team, away_team, game_directory, year, round_name)


def process_match_details(match_stats_link, home_team, away_team, game_directory, year, round_name):
    match_details_soup = get_soup(match_stats_link)
    if not match_details_soup:
        return
    team_tables = match_details_soup.find_all(class_='sortable', limit=2)
    data = [[team_tables[0], home_team], [team_tables[1], away_team]]
    for team in data:
        table = team[0]
        team_name = team[1]
        opposition_name = home_team if team_name == away_team else away_team
        display_name = '_'.join(word.lower() for word in team_name.split())
        csv_file_path = os.path.join(game_directory, f"{display_name}_match_details.csv")

        th_elements = table.find('thead').find('th', string='#').find_all_next('th')
        headers = ['#']
        headers.extend([th.get_text() for th in th_elements])
        header = ['Year', 'Round', 'Team', 'Opposition', *headers[:25], 'Subbed']

        os.makedirs(game_directory, exist_ok=True)
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)

            for row in table.find('tbody').find_all('tr'):
                data = [td.get_text() for td in row.find_all('td')]
                writer.writerow([year, round_name, team_name, opposition_name, *data[:25]])


# Process the final round section
def process_final_round_section(final_round_section, year_directory, curr_round, year):
    """
    Processes the final round section which differs from the main sections
    :param final_round_section: final round section
        final_round_section begins in the format <table><tr><td><b>Final Round</b></td></tr></table>
        It contains the final round name and the game table
    :param writer: csv writer
    :param year: year of the round
    :return: None
    """
    i = 1
    while final_round_section:
        final_round_name = final_round_section.find('b')
        if final_round_name:
            final_round_name = ''.join([c for c in final_round_name.text if c.isupper()])
            game_table = final_round_section.find_next_sibling('table')
            if game_table:
                rows = game_table.find_all('tr', recursive=False)
                game_directory = os.path.join(year_directory, f'round_{curr_round}_game_{i}')
                process_rows(rows, game_directory, final_round_name, str(year))
                final_round_section = game_table.find_next_sibling('table') if game_table else None
            else:
                final_round_section = None
        else:
            final_round_section = final_round_section.find_next_sibling('table')
        i += 1
