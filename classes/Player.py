import pandas as pd
import math
import sys

class Player:
    details_keys = [
        'team', 'year', 'games_played', 'opponent', 'round', 'result', 'jersey_num'
    ]
    stats_keys = [
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
        self.yearly_performance = {}
        self.yearly_max_performance = {}
        self.yearly_min_performance = {}
        self.yearly_avg_performance = {}
        self.all_time_max_performance = {}
        self.all_time_min_performance = {}
        self.all_time_avg_performance = {}
        self.create_player(personal_page, stats_page)


    # Creates the player based on the CSV files
    def create_player(self, personal_page, stats_page) -> None:
        self.extract_personal_details(personal_page)
        self.extract_stats_details(stats_page)


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
    def extract_stats_details(self, stats_page):
        stats_details = pd.read_csv(stats_page, header=0)
        results = {}
        for _, row in stats_details.iterrows():
            year = str(row['year'])
            round_num = str(row['round'])
            details = {}
            for key in self.details_keys:
                details[key] = row[key]

            for key in self.stats_keys:
                self.set_yearly_performance_stats(details=details, row=row, year=year, key=key)

            if year in results:
                results[year][round_num] = details
            else:
                results[year] = {round_num: details}
            
        self.yearly_performance = results
        self.set_yearly_avg_performance_stats()
        self.set_all_time_performance()


    # This will extaract the summary statistics for each stat
    def set_yearly_performance_stats(self, details, row, year, key):
        value = 0 if math.isnan(row[key]) else row[key]
        details[key] = value
        
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
    def set_yearly_avg_performance_stats(self):
        for year in self.yearly_avg_performance:
            for key in self.yearly_avg_performance[year]:
                length = len(self.yearly_avg_performance[year][key])
                arr_sum = sum(self.yearly_avg_performance[year][key])
                self.yearly_avg_performance[year][key] = arr_sum / length


    # All the various years are analysed to create yearwise summaries
    def set_all_time_performance(self):
        avg_stat = 0
        for key in self.stats_keys:
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


    # Getter for the players yearly performance
    def get_year_yearly_performance(self, year):
        year = str(year)
        if year in self.yearly_performance:
            return self.yearly_performance[year]
        else:
            print("Year not found")
            return None
    

    # Getter for the players performance in the specific year and round
    def get_round_yearly_performance(self, year, round):
        year = str(year)
        round = str(round)
        if year in self.yearly_performance:
            if round in self.yearly_performance[year]:
                return self.yearly_performance[year][round]
            else:
                print("Round not found")
                return None
        else:
            print("Year not found")
            return None
    

    # Getter for the players performance in the specific year and round, targeting a specific statistic
    def get_round_stat_yearly_performance(self, year, round, stat_name):
        round_yearly_performance = self.get_round_yearly_performance(year, round)
        if round_yearly_performance:
            return round_yearly_performance[stat_name]
        else:
            print("Stat not found")

    # Getter for the players performance in the specific year targeting a specific statistic
    def get_stat_yearly_performance(self, year, stat_name):
        year_performance = self.get_year_yearly_performance(year)
        results = []
        for round in year_performance:
            results.append(year_performance[round][stat_name])
        return results
    
    def get_stat_yearly_probability(self, year, stat_name, threshold):
        year_performance_of_stat = self.get_stat_yearly_performance(year, stat_name)
        total_len = len(year_performance_of_stat)
        hits = 0
        for stat in year_performance_of_stat:
            if stat >= threshold:
                hits += 1
        return hits/total_len

if __name__ == "__main__":
    bruz = Player(
        "match_and_player_data/player_all_time_data/MAYNARD_BRAYDEN_20-09-1996_PERSONAL.csv", 
        "match_and_player_data/player_all_time_data/MAYNARD_BRAYDEN_20-09-1996_STATS.csv"
    )
    print(f"The size of the player is: {sys.getsizeof(bruz)}")
    
    print(bruz.get_round_yearly_performance(2019, 1))
    print(bruz.get_round_stat_yearly_performance(2019, 1, 'tackles'))
    print()
    print(bruz.all_time_min_performance)
