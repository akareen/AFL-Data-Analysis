import sys

from scripts.scrape_matches_years_range import scrape_matches_page
from scripts.scrape_all_players_ever import scrape_all_players_ever
from scripts.scrape_matches_details_years_range import scrape_matches_page_directory
from scripts.players_to_teams import tie_all_players_to_their_teams


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
        case "match_details":
            if len(args) != 4:
                usage_message()

            scrape_matches_page_directory(
                start_year=int(args[2]),
                end_year=int(args[3]), 
                directory=directory
            )
        case "all_players":
            scrape_all_players_ever(directory=directory)
        case "tie_players_to_teams":
            if len(args) != 3:
                usage_message()

            tie_all_players_to_their_teams(
                output_directory=directory,
                search_directory_path=args[2]
            )
        case _:
            usage_message()


def usage_message():
    print("Usage: python scrape.py <data_storage_directory> <option>")
    print("Options:")
    print("  <data_storage_directory> matches <start year> <end year>")
    print("  <data_storage_directory> match_details <start year> <end year>")
    print("  <data_storage_directory> all_players")
    print("  <data_storage_directory>  tie_players_to_teams <all_players_directory>")
    print()
    print("Example: python scrape.py data/match_scores matches 1897 2020")
    print("Example: python scrape.py data/player_data_by_year tie_players_to_teams data/player_data_all_time")
    print()
    print("The directory should be where the data will be stored.")
    print("The earliest year for which data is available is 1897.")
    print("The latest year for which data is available is the current year.")

    sys.exit(1)


if __name__ == "__main__":
    main()