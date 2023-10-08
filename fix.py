import os
import re

directory = "match_and_player_data/player_all_time_data"

# Iterate through all files in the directory
for filename in os.listdir(directory):
    # Check if the file has consecutive underscores
    if '__' in filename:
        new_filename = re.sub('_+', '_', filename)
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_filename)
        os.rename(old_path, new_path)
        print(f"Renamed {filename} to {new_filename}")
