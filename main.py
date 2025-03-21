from game_scraper import GameScraper
from player_scraper import PlayerScraper
from datetime import datetime

def main() -> None:
    start_year: int = 1897
    end_year: int = datetime.now().year  # Dynamically set to current year (2025 as of now)
    folder_path = "data/"

    match_scraper: GameScraper = GameScraper(start_year, end_year)
    player_scraper: PlayerScraper = PlayerScraper()

    match_scraper.scrape_all_matches(
        match_folder_path=folder_path + "matches", 
        lineup_folder_path=folder_path + "lineups"
    )
    player_scraper.scrape_all_players(
        player_folder_path=folder_path + "players"
    )

if __name__ == "__main__":
    main()