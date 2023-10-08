import csv, os
from datetime import datetime
from tqdm import tqdm

from scripts.helper_classes.helper_functions import get_soup
from scripts.helper_classes.match_extraction_helper import extract_match_info

from scripts.helper_objects.row_titles import MATCH_COL_TITLES

# Peforms the web scraping integrating all the functions stores the data in a CSV file for each year
def scrape_matches_page(start_year=1897, end_year=datetime.now().year, directory='data/match_scores'):
    """
    Main function that performs the scraping
    It will scrape the match results from the start year to the end year
    :return: None
    """

    MATCH_URL_TEMPLATE = 'https://afltables.com/afl/seas/{}.html'
    os.makedirs(directory, exist_ok=True) # Ensure the directory exists

    for year in tqdm(range(start_year, end_year + 1), desc="Processing", ncols=100):
        
        # Update the description to include the current year being processed
        tqdm.write("Current Year Being Processed: {}".format(year))

        url = MATCH_URL_TEMPLATE.format(year)
        file_name = os.path.join(directory, f'{year}_MATCH_RESULTS.csv')
        soup = get_soup(url)
        
        with open(file_name, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Writing header
            writer.writerow(MATCH_COL_TITLES)
            
            # Iterating through sections and games
            for section in soup.find_all('td', {'width': '85%', 'valign': 'top'}):
                round_name = section.find_previous('a', {'name': True}).get('name')
                for game in section.find_all('table', recursive=False):
                    rows = game.find_all('tr', recursive=False)
                    process_rows(rows, writer, round_name, str(year))
            
            # Process final round section
            final_round_section = soup.find('a', {'name': 'fin'}).find_next_sibling('table').find_next_sibling('table')
            process_final_round_section(final_round_section, writer, year)
            

# Extract data from rows and write to CSV
def process_rows(rows, writer, round_name, year='2023'):
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


# Process the final round section
def process_final_round_section(final_round_section, writer, year):
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
                process_rows(rows, writer, final_round_name, str(year))
                final_round_section = game_table.find_next_sibling('table') if game_table else None
            else:
                final_round_section = None
        else:
            final_round_section = final_round_section.find_next_sibling('table')
