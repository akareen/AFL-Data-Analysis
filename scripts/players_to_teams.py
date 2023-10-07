import os, glob, csv
from tqdm import tqdm
import pandas as pd
from scripts.helper_objects.translation import AFL_TEAM_CODES

PLAYER_INFO_HEADER = ['first_name', 'last_name', 'born_date', 'debut_date', 'height', 'weight', 'stats_file_name', 'personal_file_name']

# Goes through the folder with all the player data and creates a new sorted forlder with year/team_name/csv with all players for that year details
def tie_all_players_to_their_teams():
    # Specify the directory path
    directory_path = "match_and_player_data/player_all_time_data"

    # Define the pattern to match files ending with "_PERSONAL.csv"
    file_pattern = os.path.join(directory_path, "*_PERSONAL.csv")

    # Use glob to get a list of matching files
    matching_files = glob.glob(file_pattern)

    output_directory = "match_and_player_data/player_data_by_year"
    os.makedirs(output_directory, exist_ok=True)
    
    # Iterate through the matching files
    for player_personal_stats_path in tqdm(matching_files, desc="Processing files"):
        tie_player_to_teams(output_directory, player_personal_stats_path)


# Uses the player personal stats file to get the player details and then uses the player stats file to get the year and team
def tie_player_to_teams(output_directory, player_personal_stats_path):
    personal_details = pd.read_csv(player_personal_stats_path).iloc[0].tolist()

    stats_data_file_path = player_personal_stats_path.split("_PERSONAL.csv")[0] + "_STATS.csv"
    df = pd.read_csv(stats_data_file_path)

    # Get unique years from the "year" column
    unique_years = df["year"].unique()

    for year in unique_years:
        year_folder = os.path.join(output_directory, str(year))
        if not os.path.exists(year_folder):
            os.makedirs(year_folder)

        # Filter the DataFrame for the current year
        year_df = df[df["year"] == year]

        # Get unique team names for the current year
        unique_teams = year_df["team"].unique()

        for team in unique_teams:
            team_folder = os.path.join(year_folder, team)
            if not os.path.exists(team_folder):
                os.makedirs(team_folder)

            team_code = AFL_TEAM_CODES[team.lower()]
            # Define the file path for player stats
            file_name = f"{year}_{team_code}_PLAYER_STATS.csv"
            file_path = os.path.join(team_folder, file_name)

            details_to_write = personal_details + [stats_data_file_path, player_personal_stats_path]

            if not os.path.exists(file_path):
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(PLAYER_INFO_HEADER)
                    writer.writerow(details_to_write)
            else:
                with open(file_path, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(details_to_write)