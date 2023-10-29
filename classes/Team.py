import pandas as pd
import Player
import os
from typing import List, Dict, Any, Optional, Union

AFL_TEAM_CODES = {
    'adelaide': 'ADE',
    'brisbane bears': 'BBR',
    'brisbane lions': 'BRL',
    'carlton': 'CAR',
    'collingwood': 'COL',
    'essendon': 'ESS',
    'fitzroy': 'FIT',
    'fremantle': 'FRE',
    'geelong': 'GEE',
    'gold coast': 'GCS',
    'greater western sydney': 'GWS',
    'hawthorn': 'HAW',
    'melbourne': 'MEL',
    'kangaroos': 'NM',
    'north melbourne': 'NM',
    'port adelaide': 'PA',
    'richmond': 'RIC',
    'st kilda': 'STK',
    'south melbourne': 'SOU',
    'footscray': 'FOO',
    'sydney': 'SYD',
    'university': 'UNI',
    'west coast': 'WCE',
    'western bulldogs': 'WB'
}


class Team:
    all_players = {}

    def __init__(self, team_name, year) -> None:
        self.all_players = self.create_team_by_year(team_name, year)

    # Creates a team of players for a given year
    def create_team_by_year(self, team_name, year) -> Dict[str, Player.Player]:
        """
        Creates a team of players for a given year

        Parameters
        team_name (str): The name of the team
        year (int): The year of the team

        Returns
        Dict[str, Player.Player]: A dictionary of players for the given team and year
        """

        player_info = {}
        
        lower_team_name = team_name.lower()
        if lower_team_name not in AFL_TEAM_CODES:
            raise Exception(f"Team name {team_name} not found in AFL_TEAM_CODES. The team name must be one of the following: {AFL_TEAM_CODES.keys()}")

        team_code = AFL_TEAM_CODES[team_name.lower()]
        
        file_name = f"match_and_player_data/player_data_by_year/{year}/{team_name.capitalize()}/{year}_{team_code}_PLAYER_STATS.csv"
        
        team_data = pd.read_csv(file_name, header=0)
        for _, row in team_data.iterrows():
            player_personal_stats = row['personal_file_name']
            player_game_stats = row['stats_file_name']
            
            player_object = Player.Player(
                "player_name",
                personal_file_name=player_personal_stats, 
                stats_file_name=player_game_stats)
            
            player_full_name = player_object.full_name
            player_info[player_full_name] = player_object

        return player_info

# Some basic testing
if __name__ == "__main__":
    team = Team("Collingwood", 2023)
    player = team.all_players['Brody Mihocek']
    player.print_player_summary()