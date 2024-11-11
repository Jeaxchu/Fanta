# 1) export your file as txt file from any anime stream website
# 2) go to Shell/Terminal and paste 'pip install requests', and 'pip install tqdm' then click Enter
# 3) copy and paste the export.txt on anime_data in main.py
# 4) run it
# 5) download the anime_data.xml if you're using replit, it will auto download if you're using vscode or any other downloaded software
# 6) go to 'https://myanimelist.net/import.php'
# 7) choose MyAnimeList Import
# 8) import
# Honorable Mention : Exam might cook me up, but I'm cooking ts

import requests
import time
from tqdm import tqdm

print("""
   NN    NN  EEEEE  RRRRR   VVV       VVV
   NN N  NN  E      RR  RR   VVV     VVV
   NN  N NN  EEEE   RRRRR     VVV   VVV
   NN   NNN  E      RR  RR     VVV VVV
   NN    NN  EEEEE  RR   RR     VVVVV

""")

anime_data = """
Put your export text here
"""

def get_anime_info(anime_id):
    url = f"https://api.jikan.moe/v4/anime/{anime_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        episodes = data['data']['episodes']
        return episodes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching info for anime ID {anime_id}: {e}")
        return None

def main():
    anime_lines = anime_data.strip().split('\n')
    anime_status = {}
    current_status = None

    status_mapping = {
        "completed": "Completed",
        "plan_to_watch": "Plan to Watch",
        "watching": "Watching",
        "on-hold": "On-Hold",
        "dropped": "Dropped"
    }

    for line in tqdm(anime_lines, desc="NERV Operation: Categorizing Anime Entries", unit="entry", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
        line = line.strip()
        if line.startswith("#"):
            current_status = line[2:].strip().lower().replace(" ", "_")
            if current_status not in anime_status:
                anime_status[current_status] = []
        elif "|" in line and current_status:
            anime_status[current_status].append(line)

    xml_data = '<?xml version="1.0" encoding="UTF-8"?>\n<myanimelist>\n'
    xml_data += '\t<myinfo>\n\t\t<user_export_type>1</user_export_type>\n\t</myinfo>\n'

    for status, anime_list in tqdm(anime_status.items(), desc="NERV Operation: Generating XML Entries", unit="category", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
        for anime in tqdm(anime_list, leave=False, desc=f"NERV Processing: {status.capitalize()}", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
            name, url = [part.strip() for part in anime.split("|")]
            series_id = url.split('/')[-1]

            if status == "plan_to_watch":
                episodes = 0
            elif status == "dropped":
                episodes = 1
            elif status in ["watching", "on-hold"]:
                episodes = input(f" Enter number of episodes watched for '{name}':  ")
                while not episodes.isdigit():
                    print("Please enter a valid number.")
                    episodes = input(f" Enter number of episodes watched for '{name}':  ")
                episodes = int(episodes)
            else:
                episodes = get_anime_info(series_id)

            entry_string = (
                "\t<anime>\n"
                f"\t\t<series_animedb_id>{series_id}</series_animedb_id>\n"
                f"\t\t<series_title><![CDATA[{name}]]></series_title>\n"
                f"\t\t<my_watched_episodes>{episodes}</my_watched_episodes>\n"
                f"\t\t<my_status>{status_mapping[status]}</my_status>\n"
                "\t\t<update_on_import>1</update_on_import>\n"
                "\t</anime>\n"
            )
            xml_data += entry_string

            time.sleep(2)

    xml_data += '</myanimelist>'

    save_path = "anime_data.xml"
    with open(save_path, "w") as file:
        file.write(xml_data)

    print(f"✅ Saving file at {save_path}")

if __name__ == "__main__":
    main()
