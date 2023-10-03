from datetime import datetime
import csv
import os
from scripts.helper_functions import get_soup


# Peforms the web scraping integrating all the functions stores the data in a CSV file for each year
def scrape_matches_page(start_year=1897, end_year=datetime.now().year, directory='data/match_scores'):
    """
    Main function that performs the scraping
    :return: None
    """

    MATCH_URL_TEMPLATE = 'https://afltables.com/afl/seas/{}.html'
    COLUMN_TITLES = ['Year', 'Round', 'Home Team', 'Away Team',
                 'H Goals 1st', 'H Goals 2nd', 'H Goals 3rd', 'H Goals 4th',
                 'H Behind 1st', 'H Behind 2nd', 'H Behind 3rd', 'H Behind 4th',
                 'H Total Goals', 'H Total Behind', 'H Total Score',
                 'A Goals 1st', 'A Goals 2nd', 'A Goals 3rd', 'A Goals 4th',
                 'A Behind 1st', 'A Behind 2nd', 'A Behind 3rd', 'A Behind 4th',
                 'A Total Goals', 'A Total Behind', 'A Total Score',
                 'Winning Team', 'Margin', 'Date', 'Attendance', 'Venue']

    os.makedirs(directory, exist_ok=True) # Ensure the directory exists
    for year in range(start_year, end_year + 1):
        url = MATCH_URL_TEMPLATE.format(year)
        file_name = os.path.join(directory, f'results_{year}.csv')
        soup = get_soup(url)
        
        with open(file_name, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Writing header
            writer.writerow(COLUMN_TITLES)
            
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
            
    winning_team = determine_winner(home_team, home_total_score, away_team, away_total_score)
    margin = abs(home_total_score - away_total_score)
    
    writer.writerow([year, round_name, home_team, away_team,
                     *home_goals, *home_behinds, sum(home_goals), sum(home_behinds), home_total_score,
                     *away_goals, *away_behinds, sum(away_goals), sum(away_behinds), away_total_score,
                     winning_team, margin, date, attendance, venue])


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


# Extracts all relevant information from a table row
def extract_data(row):
    """
    Extract team, scores, and extra_info from a row
    :param row: row from the table
        row begins in the format <tr><td><a>Team</a></td><td width="20%">3.2 4.3 5.4 6.5</td><td>Extra Info</td></tr>
    :return: team, scores, extra_info
        it returns the team, scores, and extra_info
    """
    team = row.find('a').text
    scores = row.find('td', {'width': '20%'}).text.split()
    extra_info = row.find_all('td')[-1].text.split()
    return team, scores, extra_info


# Extracts the date, attendance, and venue from extra_info
def extract_extra_info(extra_info):
    """
    Extracts the date, attendance, and venue from extra_info
    :param extra_info: list of extra info from the row
        extra_info begins in the format ['Sat', '24-Apr-2021', '2:10pm', 'Att:', '7,000', 'Venue:', 'Marvel']
    :return: date, attendance, venue
        it returns the date, attendance, and venue
    """
    date = datetime.strptime(extra_info[1], "%d-%b-%Y").strftime("%d-%m-%Y")
    # if it doesnt contain 'Att:' then dont search and make it 0
    if 'Att:' not in extra_info:
        attendance = 0
    else:
        attendance = extra_info[extra_info.index('Att:') + 1].replace(',', '')
    if 'Venue:' not in extra_info:
        venue = 'Unknown'
    else:
        venue = extra_info[extra_info.index('Venue:') + 1]
    return date, attendance, venue


# Unpacks the scores into goals and behinds for each quarter
def unpack_team_scores(scores):
    """
    Unpacks the scores into goals and behinds for each quarter
    :param scores: list of scores for each quarter
        scores begins in the format ['3.2', '4.3', '5.4', '6.5']
        where it is goals.behinds and accumulates
    :return: goals, behinds
        it returns the goals and behinds for each quarter
    """
    goals_arr = []
    behinds_arr = []
    for score in scores:
        goals, behinds = map(int, score.split('.'))
        goals_arr.append(goals)
        behinds_arr.append(behinds)
    goals = [goals_arr[i] - goals_arr[i-1] if i != 0 else goals_arr[i] for i in range(4)]
    behinds = [behinds_arr[i] - behinds_arr[i-1] if i != 0 else behinds_arr[i] for i in range(4)]
    return goals, behinds


# Determines the winning team and returns the String name
def determine_winner(home_team, home_total_score, away_team, away_total_score):
    if home_total_score > away_total_score:
        return home_team
    elif away_total_score > home_total_score:
        return away_team
    else:
        return 'Match drawn'