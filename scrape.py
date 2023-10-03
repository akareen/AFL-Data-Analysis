from scripts.helper_functions import get_soup
from scripts.scrape_matches_years_range import scrape_matches_page
from scripts.scrape_players_by_range import scrape_players_by_range
from scripts.scrape_all_players_ever import scrape_all_players_ever

from datetime import datetime
import csv
import os
import sys

def main():
    if len(sys.argv) <= 2:
        usage_message()
    args = sys.argv[1:]
    
    directory = args[0]
    option = args[1]
    match option:
        case "matches":
            if len(args) != 4:
                usage_message()

            scrape_matches_page(
                start_year=int(args[2]),
                end_year=int(args[3]), 
                directory=directory
            )
        case "players":
            if len(args) != 4:
                usage_message()

            scrape_players_by_range(
                start_year=int(args[2]),
                end_year=int(args[3]), 
                directory=directory
            )
        case "all_players":
            scrape_all_players_ever(directory=directory)
        case _:
            usage_message()

    
def usage_message():
    print("Usage: python scrape.py <data_storage_directory> <option>")
    print("Options:")
    print("  <data_storage_directory> matches <start year> <end year>")
    print("  <data_storage_directory> players <start year> <end year>")
    print("  <data_storage_directory> all_players")
    print()
    print("Example: python scrape.py data/match_scores matches 1897 2020")
    print()
    print("The directory should be where the data will be stored.")
    print("The earliest year for which data is available is 1897.")
    print("The latest year for which data is available is the current year.")

    sys.exit(1)


if __name__ == "__main__":
    main()