import pandas as pd
import Player

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
        self.create_team(team_name, year)

    def create_team(self, team_name, year):
        team_code = AFL_TEAM_CODES[team_name.lower()]
        file_name = f"match_and_player_data/player_data_by_year/{year}/{team_name.capitalize()}/{year}_{team_code}_PLAYER_STATS.csv"
        team_data = pd.read_csv(file_name, header=0)
        for _, row in team_data.iterrows():
            player_personal_stats = row['personal_file_name']
            player_game_stats = row['stats_file_name']
            
            player_object = Player.Player(personal_page=player_personal_stats, stats_page=player_game_stats)
            player_full_name = player_object.full_name
            self.all_players[player_full_name] = player_object

if __name__ == "__main__":
    team = Team("Collingwood", 2023)
    print(team.all_players['Brody Mihocek'].get_stat_yearly_performance(2023, 'goals'))
    print(team.all_players['Steele Sidebottom'].get_stat_yearly_probability(2023, 'disposals', 15))
