import pandas as pd
import math
from typing import List, Dict, Any, Optional, Union

"""
List of the functions for the player and what they do:

"""


class Player:
    DETAIL_KEYS = [
        'team', 'year', 'games_played', 'opponent', 'round', 'result', 'jersey_num'
    ]
    STATS_KEYS = [
        'kicks', 'marks', 'handballs', 'disposals', 'goals', 'behinds', 'hit_outs', 'tackles',
        'rebound_50s', 'inside_50s', 'clearances', 'clangers', 'free_kicks_for', 'free_kicks_against',
        'brownlow_votes', 'contested_possessions', 'uncontested_possessions', 'contested_marks',
        'marks_inside_50', 'one_percenters%', 'bounces', 'goal_assist', '%percentage_of_game_played'
    ]

    # Initialises all the variables of the players
    def __init__(self, personal_page, stats_page) -> None:
        self.first_name = ""
        self.last_name = ""
        self.full_name = ""
        self.born_date = ""
        self.debut_date = ""
        self.height = 0
        self.weight = 0
        self.teams_played = []

        self.yearly_performance = {}
        self.yearly_max_performance = {}
        self.yearly_min_performance = {}
        self.yearly_avg_performance = {}
        self.all_time_max_performance = {}
        self.all_time_min_performance = {}
        self.all_time_avg_performance = {}
        self.create_player(personal_page, stats_page)


    # ---- The below functions are public functions that can be used to get the data from the player ----

    # Getter for the players yearly performance
    def get_year_performance(self, year, metric="all") -> Optional[Dict[str, Any]]:
        """
        Returns the yearly performance of the player in the given year

        Parameters
        year (int): The desired year of the player performance
        metric (str): The metric to return. The valid choices are: all, max, min, avg. Defaults to all

        Returns
        dict: The dictionary of the performance in the given year. The format is as follows:
        {
            '[Round Number]': {  player performance },
            ...
        }
        """
        
        year = str(year) # Converted to string to ensure that the year is in the correct format
        
        if metric == "all":
            stats = self.yearly_performance
        elif metric == "max":
            stats = self.yearly_max_performance
        elif metric == "min":
            stats = self.yearly_min_performance
        elif metric == "avg":
            stats = self.yearly_avg_performance
        else:
            raise ValueError(f"Invalid metric: {metric}. The valid choices are: all, max, min, avg")


        if year in stats:
            return stats[year]
        else:
            print(f"The performance of player {self.full_name} is not found for: {year}")
            return None
    

    # Getter for the players yearly performance, targeting a specific statistic
    def get_year_performance_by_stat(self, year, stat_name, metric="all") -> Optional[List[Any]]:
        if stat_name not in self.STATS_KEYS:
            raise ValueError(f"Invalid stat_name: {stat_name}. The valid choices are: {self.STATS_KEYS}")
        year_performance = self.get_year_performance(year, metric)
        if year_performance:
            results = []
            for round in year_performance:
                results.append(year_performance[round][stat_name])
            return results
        return None


    # Getter for the players performance in the specific year and round
    def get_round_performance(self, year, round, metric="all") -> Optional[Dict[str, Any]]:
        """
        Returns the performance of the player in the given year and round

        Parameters
        year (int): The desired year of the player performance
        round (int): The desired round within that year
        metric (str): The metric to return. The valid choices are: all, max, min, avg. Defaults to all

        Returns
        dict: The dictionary of the performance in the given year and round. The format is as follows:
        {
            'team': '', 'year': '', 'games_played': '', 'opponent': '', 'round': '', 'result': '', 'jersey_num': '', etc.
        }

        """

        year_performance = self.get_year_performance(year, metric)
        if year_performance:
            round = str(round) # Converted to string to esnure it is in the right format
            if round in year_performance:
                return year_performance[round]
            else:
                print(f"The performance of player {self.full_name} is not found for: {year} round: {round}")
                return None
        else:
            print(f"The performance of player {self.full_name} is not found for: {year}")
            return None


    # Getter for the players performance in the specific year and round, targeting a specific statistic
    def get_round_performance_by_stat(self, year, round, stat_name, metric="all") -> Optional[Any]:
        """
        Returns the performance of the player in the given year and round, targeting a specific statistic

        Parameters
        year (int): The desired year of the player performance
        round (int): The desired round within that year
        stat_name (str): The desired statistic to return
        metric (str): The metric to return. The valid choices are: all, max, min, avg. Defaults to all

        Returns
        float: The value of the statistic in the given year and round

        """

        round_performance = self.get_round_performance(year, round, metric)
        if round_performance:
            return round_performance[stat_name]
        else:
            print(f"The performance of player {self.full_name} is not found for: {year} round: {round}")
            return None
        

    # Get all time probability of a stat being above a threshold
    def get_all_time_probability(self, stat_name, threshold) -> float:
        """
        Returns the probability of the player having a statistic above the threshold

        Parameters
        stat_name (str): The desired statistic to return. The choices are: 'kicks', 'marks', 'handballs', 'disposals', 'goals', 'behinds', 'hit_outs', 'tackles',
        'rebound_50s', 'inside_50s', 'clearances', 'clangers', 'free_kicks_for', 'free_kicks_against',
        'brownlow_votes', 'contested_possessions', 'uncontested_possessions', 'contested_marks',
        'marks_inside_50', 'one_percenters%', 'bounces', 'goal_assist', '%percentage_of_game_played'

        threshold (float): The threshold to compare the statistic to

        Returns
        float: The probability of the statistic being above the threshold
        """
        
        total_len = 0
        hits = 0
        for year in self.yearly_performance:
            year_performance_of_stat = self.get_year_performance_by_stat(year, stat_name)
            total_len += len(year_performance_of_stat)
            for stat in year_performance_of_stat:
                if stat >= threshold:
                    hits += 1
        return hits/total_len


    # Get yearly probability of a stat being above a threshold
    def get_year_probability(self, year, stat_name, threshold) -> float:
        """
        Returns the probability of the player having a statistic above the threshold in the given year

        Parameters
        year (int): The desired year of the player performance
        stat_name (str): The desired statistic to return. The choices are: 'kicks', 'marks', 'handballs', 'disposals', 'goals', 'behinds', 'hit_outs', 'tackles',
        'rebound_50s', 'inside_50s', 'clearances', 'clangers', 'free_kicks_for', 'free_kicks_against',
        'brownlow_votes', 'contested_possessions', 'uncontested_possessions', 'contested_marks',
        'marks_inside_50', 'one_percenters%', 'bounces', 'goal_assist', '%percentage_of_game_played'

        threshold (float): The threshold to compare the statistic to

        Returns
        float: The probability of the statistic being above the threshold
        """

        year_performance_of_stat = self.get_year_performance_by_stat(year, stat_name)
        total_len = len(year_performance_of_stat)
        hits = 0
        for stat in year_performance_of_stat:
            if stat >= threshold:
                hits += 1
        return hits/total_len
    
    # ------------------------------

    # ----- The below functions are to create summaries ----
    def print_player_summary(self) -> None:
        """
        This function prints a comprehensive summary of the player include personal details and performance statistics (of the most recent year)
        """


        most_recent_year = max(self.yearly_performance.keys())
        rounds_for_most_recent_year = self.yearly_performance[most_recent_year].keys()
        max_key_length = max(len(key) for key in self.STATS_KEYS)

        stat_width = 2 

        header_format = f"{{:<{max_key_length}}}  {{}}"

        round_numbers_header = '  '.join(f"{round_num:>{stat_width}}" for round_num in rounds_for_most_recent_year)
        formatted_teams_years = ', '.join([f"{year} - {team}" for year, team in self.teams_played])
        
        round_numbers_header = header_format.format('ROUND NUMBERS', round_numbers_header)
        long_line = "-" * len(round_numbers_header)

        print(f"Name: {self.full_name}")
        print(f"Born: {self.born_date}")
        print(f"Debut: {self.debut_date}")
        print(f"Height (cm): {self.height}")
        print(f"Weight (kg): {self.weight}")
        print(f"List of all teams played that {self.full_name} has played for: \n\t{formatted_teams_years}")
        print(f"Most recent year of performance: {most_recent_year}\n")

        print(f"Selected statistics for the most recent year ({most_recent_year}):")

        print(round_numbers_header)
        print(long_line)

        for key in self.STATS_KEYS:
            stats_list = self.get_year_performance_by_stat(most_recent_year, key)

            # Creating a space-separated string of stats, ensuring each stat is right-aligned within a fixed width
            stats_str = '  '.join(f"{stat:>{stat_width}}" for stat in stats_list)

            # Print the stat key and its values, ensuring alignment with the round numbers
            print(header_format.format(key, stats_str))
            print(long_line)
        print()


    # ----- All of the below functions are used to create the player and extract the data from the CSV files -----

    # Creates the player based on the CSV files
    def create_player(self, personal_page, stats_page) -> None:
        self.extract_personal_details(personal_page)
        self.extract_and_process_stats_details(stats_page)


    # The personal details are extracted for processing
    def extract_personal_details(self, personal_page) -> None:
        personal_details = pd.read_csv(personal_page, header=0)
        self.first_name =  personal_details['first_name'][0]
        self.last_name =  personal_details['last_name'][0]
        self.full_name = self.first_name + " " + self.last_name
        self.born_date =  personal_details['born_date'][0]
        self.debut_date =  personal_details['debut_date'][0]
        self.height = personal_details['height'][0]
        self.weight = personal_details['weight'][0]
    

    # Whilst extracting the stats it also creates summaries min, max, avg for each stat
    def extract_and_process_stats_details(self, stats_page):
        stats_details = pd.read_csv(stats_page, header=0)
        results = {}
        for _, row in stats_details.iterrows():
            year = str(row['year'])
            round_num = str(row['round'])
            details = {}
            for key in self.DETAIL_KEYS:
                details[key] = row[key]

            for key in self.STATS_KEYS:
                self.calculate_yearly_performance_stats(details=details, row=row, year=year, key=key)

            if year in results:
                results[year][round_num] = details
            else:
                self.teams_played.append([year, details['team']])
                results[year] = {round_num: details}
            
        self.yearly_performance = results
        self.calculate_yearly_avg_performance_stats()
        self.calculate_all_time_performance()


    # This will extaract the summary statistics for each stat
    def calculate_yearly_performance_stats(self, details: Dict[str, Any], row: pd.Series, year: str, key: str) -> None: 
        value = 0 if math.isnan(row[key]) else row[key]
        details[key] = int(value)
        
        if year not in self.yearly_max_performance:
            self.yearly_max_performance[year] = {}
            self.yearly_min_performance[year] = {}
            self.yearly_avg_performance[year] = {}
        
        self.yearly_max_performance[year][key] = max(self.yearly_max_performance[year].get(key, float('-inf')), value)
        self.yearly_min_performance[year][key] = min(self.yearly_min_performance[year].get(key, float('inf')), value)
        if key in self.yearly_avg_performance[year]:
            self.yearly_avg_performance[year][key].append(value)
        else:
            self.yearly_avg_performance[year][key] = [ value ]


    # Setting average stats requires length wise division
    def calculate_yearly_avg_performance_stats(self) -> None:
        for year in self.yearly_avg_performance:
            for key in self.yearly_avg_performance[year]:
                length = len(self.yearly_avg_performance[year][key])
                arr_sum = sum(self.yearly_avg_performance[year][key])
                self.yearly_avg_performance[year][key] = arr_sum / length


    # All the various years are analysed to create yearwise summaries
    def calculate_all_time_performance(self) -> None:
        avg_stat = 0
        for key in self.STATS_KEYS:
            min_stat = float('inf')
            max_stat = float('-inf')
            num_years = len(self.yearly_avg_performance)
            for year in self.yearly_avg_performance:
                min_stat = min(min_stat, self.yearly_min_performance[year][key])
                max_stat = max(max_stat, self.yearly_max_performance[year][key])
                avg_stat += self.yearly_avg_performance[year][key]
            avg_stat /= num_years

            self.all_time_min_performance[key] = min_stat
            self.all_time_max_performance[key] = max_stat
            self.all_time_avg_performance[key] = avg_stat


if __name__ == "__main__":
    bruz = Player(
        "match_and_player_data/player_all_time_data/MAYNARD_BRAYDEN_20-09-1996_PERSONAL.csv", 
        "match_and_player_data/player_all_time_data/MAYNARD_BRAYDEN_20-09-1996_STATS.csv"
    )
    bruz.print_player_summary()