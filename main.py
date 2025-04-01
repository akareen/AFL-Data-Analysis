import argparse
from game_scraper import MatchScraper
from player_scraper import PlayerScraper

def main(start_year: int, end_year: int, scrape_matches: bool, scrape_players: bool, folder_path: str) -> None:
    match_scraper: MatchScraper = MatchScraper(start_year, end_year)
    player_scraper: PlayerScraper = PlayerScraper()

    if scrape_matches:
        match_scraper.scrape_all_matches(
            match_folder_path=folder_path + "matches", lineup_folder_path=folder_path + "lineups"
        )
    
    if scrape_players:
        player_scraper.scrape_all_players(
            folder_path=folder_path + "players"
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape match and player data.")

    # Command line arguments
    parser.add_argument(
        "--start_year", type=int, default=1897, help="The starting year for scraping."
    )
    parser.add_argument(
        "--end_year", type=int, default=2025, help="The ending year for scraping."
    )
    parser.add_argument(
        "--scrape_matches", action="store_true", help="Flag to scrape match data."
    )
    parser.add_argument(
        "--scrape_players", action="store_true", help="Flag to scrape player data."
    )
    parser.add_argument(
        "--folder_path", type=str, default="data/", help="Path to save the scraped data."
    )

    # Parse the arguments
    args = parser.parse_args()

    # Call the main function with the parsed arguments
    main(
        start_year=args.start_year,
        end_year=args.end_year,
        scrape_matches=args.scrape_matches,
        scrape_players=args.scrape_players,
        folder_path=args.folder_path
    )
