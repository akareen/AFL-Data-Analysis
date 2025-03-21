import os
import pandas as pd
import concurrent.futures
from typing import Dict, List, Tuple

# Attempt to import cudf with comprehensive fallback to pandas
try:
    import cudf
    # Verify CUDA runtime is accessible
    cudf.DataFrame({'test': [1]})  # Trigger CUDA initialization
    USE_GPU = True
    print("Using GPU with CuDF")
except (ImportError, RuntimeError, OSError, AttributeError) as e:
    # Catch ImportError (cudf not installed), RuntimeError (CUDA issues), OSError (library not found), AttributeError (initialization issues)
    import pandas as cudf
    USE_GPU = False
    print(f"Failed to initialize CuDF ({e}), falling back to CPU with Pandas")

def calculate_greatness_score(df: cudf.DataFrame) -> int:
    """
    Calculate a greatness score for a player based on their career stats.
    
    Args:
        df (cudf.DataFrame or pd.DataFrame): Player's performance stats.
        
    Returns:
        int: Total greatness score.
    """
    # Ensure numeric columns are properly typed
    df['disposals'] = df['disposals'].astype('float64').fillna(0)
    df['goals'] = df['goals'].astype('float64').fillna(0)
    df['tackles'] = df['tackles'].astype('float64').fillna(0)
    
    # Scoring system: 3 points per disposal, 6 per goal, 4 per tackle
    score = (
        df['disposals'].sum() * 3 +
        df['goals'].sum() * 6 +
        df['tackles'].sum() * 4
    )
    return int(score)

def process_player_file(filepath: str) -> Tuple[str, int, int]:
    """
    Process a single player's CSV file and return their name, score, and games played.

    Args:
        filepath (str): Path to the player's performance CSV file.

    Returns:
        Tuple[str, int, int]: (player_name, greatness_score, games_played)
    """
    try:
        df = cudf.read_csv(filepath) if USE_GPU else pd.read_csv(filepath)
        if df.empty:
            return None
        
        # Extract player name from filename (e.g., "mcleod_andrew_04081976")
        player_name = "_".join(os.path.basename(filepath).split("_")[:-2])
        
        # Calculate greatness score and total games played
        score = calculate_greatness_score(df)
        games_played = len(df)  # Number of rows = games played
        
        return (player_name, score, games_played)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def get_top_players(data_dir: str = "./data/player_data/", top_n: int = 10) -> List[Tuple[str, int, int]]:
    """
    Get the top N greatest AFL players based on career stats from scraped data.

    Args:
        data_dir (str): Directory containing player performance CSV files.
        top_n (int): Number of top players to return.

    Returns:
        List[Tuple[str, int, int]]: List of (player_name, greatness_score, games_played) sorted by score.
    """
    player_scores: Dict[str, Tuple[int, int]] = {}

    # Collect all performance CSV files
    filepaths = [
        os.path.join(data_dir, filename)
        for filename in os.listdir(data_dir)
        if filename.endswith("_performance_details.csv")
    ]

    # Process files in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(process_player_file, filepaths)
        
        # Aggregate results
        for result in results:
            if result:
                player_name, score, games = result
                player_scores[player_name] = (score, games)

    # Sort players by score (descending), then games played (descending) as tiebreaker
    sorted_players = sorted(
        player_scores.items(),
        key=lambda x: (x[1][0], x[1][1]),
        reverse=True
    )
    
    # Return top N players with name, score, and games played
    top_list = [(name, score, games) for name, (score, games) in sorted_players[:top_n]]
    return top_list

def main() -> None:
    """
    Main function to run the top players script and print results.
    """
    data_dir = "./data/player_data/"  # Matches your scraper output directory
    top_players = get_top_players(data_dir, top_n=10)
    
    print("\nTop 10 Greatest AFL Players (based on career stats):")
    print("Rank | Player Name             | Greatness Score | Games Played")
    print("-" * 60)
    for i, (name, score, games) in enumerate(top_players, 1):
        print(f"{i:2d}   | {name:<23} | {score:>13d} | {games:>11d}")

if __name__ == "__main__":
    main()