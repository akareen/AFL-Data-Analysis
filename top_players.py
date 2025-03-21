import os
import pandas as pd
import concurrent.futures
from typing import Dict, List, Tuple

try:
    import cudf
    cudf.DataFrame({'test': [1]})
    USE_GPU = True
    print("Using GPU with CuDF")
except (ImportError, RuntimeError, OSError, AttributeError) as e:
    import pandas as cudf
    USE_GPU = False
    print(f"Failed to initialize CuDF ({e}), falling back to CPU with Pandas")

def calculate_greatness_score(
    df: cudf.DataFrame,
    goal_weight: float = 8.0,
    behind_weight: float = 1.0,
    goal_assist_weight: float = 3.0,
    contested_mark_weight: float = 6.0,
    contested_possession_weight: float = 4.5,
    mark_weight: float = 2.0,
    kick_weight: float = 4.0,
    clanger_weight: float = -4.0,
    free_kick_for_weight: float = 4.0,
    free_kick_against_weight: float = -4.0,
    tackle_weight: float = 4.0,
    one_percenter_weight: float = 2.0,
    clearance_weight: float = 4.0,
    brownlow_vote_weight: float = 50.0,
    disposal_weight: float = 5.0
) -> Tuple[int, int, int, int, int, int, int, int, int, int, int, int, int, int]:
    df['goals'] = df['goals'].astype('float64').fillna(0)
    df['behinds'] = df['behinds'].astype('float64').fillna(0)
    df['goal_assist'] = df['goal_assist'].astype('float64').fillna(0)
    df['contested_marks'] = df['contested_marks'].astype('float64').fillna(0)
    df['contested_possessions'] = df['contested_possessions'].astype('float64').fillna(0)
    df['marks'] = df['marks'].astype('float64').fillna(0)
    df['kicks'] = df['kicks'].astype('float64').fillna(0)
    df['clangers'] = df['clangers'].astype('float64').fillna(0)
    df['free_kicks_for'] = df['free_kicks_for'].astype('float64').fillna(0)
    df['free_kicks_against'] = df['free_kicks_against'].astype('float64').fillna(0)
    df['tackles'] = df['tackles'].astype('float64').fillna(0)
    df['one_percenters'] = df['one_percenters'].astype('float64').fillna(0)
    df['clearances'] = df['clearances'].astype('float64').fillna(0)
    df['brownlow_votes'] = df['brownlow_votes'].astype('float64').fillna(0)
    df['disposals'] = df['disposals'].astype('float64').fillna(0)
    
    total_goals = int(df['goals'].sum())
    total_behinds = int(df['behinds'].sum())
    total_goal_assists = int(df['goal_assist'].sum())
    total_contested_marks = int(df['contested_marks'].sum())
    total_contested_possessions = int(df['contested_possessions'].sum())
    total_marks = int(df['marks'].sum())
    total_kicks = int(df['kicks'].sum())
    total_clangers = int(df['clangers'].sum())
    total_free_kicks_for = int(df['free_kicks_for'].sum())
    total_free_kicks_against = int(df['free_kicks_against'].sum())
    total_tackles = int(df['tackles'].sum())
    total_one_percenters = int(df['one_percenters'].sum())
    total_clearances = int(df['clearances'].sum())
    total_brownlow_votes = int(df['brownlow_votes'].sum())
    total_disposals = int(df['disposals'].sum())
    
    score = (
        total_goals * goal_weight +
        total_behinds * behind_weight +
        total_goal_assists * goal_assist_weight +
        total_contested_marks * contested_mark_weight +
        total_contested_possessions * contested_possession_weight +
        total_marks * mark_weight +
        total_kicks * kick_weight +
        total_clangers * clanger_weight +
        total_free_kicks_for * free_kick_for_weight +
        total_free_kicks_against * free_kick_against_weight +
        total_tackles * tackle_weight +
        total_one_percenters * one_percenter_weight +
        total_clearances * clearance_weight +
        total_brownlow_votes * brownlow_vote_weight +
        total_disposals * disposal_weight
    )
    return (int(score), total_goals, total_behinds, total_goal_assists, total_contested_marks, 
            total_contested_possessions, total_marks, total_kicks, total_clangers, 
            total_free_kicks_for, total_free_kicks_against, total_tackles, total_one_percenters, total_clearances, total_disposals)

def process_player_file(filepath: str, **weights) -> Tuple[str, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int]:
    try:
        df = cudf.read_csv(filepath) if USE_GPU else pd.read_csv(filepath)
        if df.empty:
            return None
        
        player_name = "_".join(os.path.basename(filepath).split("_")[:-2])
        
        score, goals, behinds, goal_assists, contested_marks, contested_possessions, marks, kicks, clangers, free_kicks_for, free_kicks_against, tackles, one_percenters, clearances, disposals = calculate_greatness_score(
            df, **weights
        )
        games_played = len(df)
        
        return (player_name, score, goals, behinds, goal_assists, contested_marks, contested_possessions, marks, kicks, clangers, free_kicks_for, free_kicks_against, tackles, one_percenters, clearances, disposals, games_played)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def get_top_players(
    data_dir: str = "./data/player_data/",
    top_n: int = 100,
    **weights
) -> List[Tuple[str, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int]]:
    player_scores: Dict[str, Tuple[int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int]] = {}

    filepaths = [
        os.path.join(data_dir, filename)
        for filename in os.listdir(data_dir)
        if filename.endswith("_performance_details.csv")
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(
            lambda filepath: process_player_file(filepath, **weights),
            filepaths
        )
        
        for result in results:
            if result:
                player_name, score, goals, behinds, goal_assists, contested_marks, contested_possessions, marks, kicks, clangers, free_kicks_for, free_kicks_against, tackles, one_percenters, clearances, disposals, games = result
                player_scores[player_name] = (score, goals, behinds, goal_assists, contested_marks, contested_possessions, marks, kicks, clangers, free_kicks_for, free_kicks_against, tackles, one_percenters, clearances, disposals, games)

    sorted_players = sorted(
        player_scores.items(),
        key=lambda x: (x[1][0], x[1][15]),  # Sort by score, then games_played (index 15)
        reverse=True
    )
    
    top_list = [(name, score, goals, behinds, goal_assists, contested_marks, contested_possessions, marks, kicks, clangers, free_kicks_for, free_kicks_against, tackles, one_percenters, clearances, disposals, games) 
                for name, (score, goals, behinds, goal_assists, contested_marks, contested_possessions, marks, kicks, clangers, free_kicks_for, free_kicks_against, tackles, one_percenters, clearances, disposals, games) in sorted_players[:top_n]]
    return top_list

def main() -> None:
    data_dir = "./data/player_data/"
    
    weights = {
        'disposal_weight': 12.0,      # Increased from 9.0
        'goal_weight': 60.0,          # Increased from 45.0
        'behind_weight': 1.0,
        'goal_assist_weight': 3.0,
        'contested_mark_weight': 6.0,
        'contested_possession_weight': 4.5,
        'mark_weight': 2.0,
        'kick_weight': 4.0,
        'clanger_weight': -4.0,
        'free_kick_for_weight': 4.0,
        'free_kick_against_weight': -4.0,
        'tackle_weight': 2.0,
        'one_percenter_weight': 2.0,
        'clearance_weight': 4.0,
        'brownlow_vote_weight': 50.0
    }
    
    top_players = get_top_players(data_dir, top_n=100, **weights)
    
    print(f"\nTop 100 Greatest AFL Players (Disposal: {weights['disposal_weight']}, Goal: {weights['goal_weight']}, Tackle: {weights['tackle_weight']}, Kick: {weights['kick_weight']}, Mark: {weights['mark_weight']}, Clearance: {weights['clearance_weight']}, Contested: {weights['contested_possession_weight']}, Brownlow: {weights['brownlow_vote_weight']}):")
    print("Rank | Player Name             | Score     | Games | Disposals | Goals | Tackles | Kicks | Marks | Clearances | Contested")
    print("-" * 110)
    for i, (name, score, goals, behinds, goal_assists, contested_marks, contested_possessions, marks, kicks, clangers, free_kicks_for, free_kicks_against, tackles, one_percenters, clearances, disposals, games) in enumerate(top_players, 1):
        print(f"{i:3d}  | {name:<23} | {score:>9d} | {games:>5d} | {disposals:>9d} | {goals:>5d} | {tackles:>7d} | {kicks:>5d} | {marks:>5d} | {clearances:>10d} | {contested_possessions:>9d}")

if __name__ == "__main__":
    main()