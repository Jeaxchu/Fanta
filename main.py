import requests
import re
import time
from tqdm import tqdm  # Import tqdm for progress bar

# Multi-line string containing anime entries with their status and episode count
anime_data = """
paste the export here and delete this line
"""

def get_anime_info(anime_id):
    """Fetch anime details from MyAnimeList API using series ID."""
    url = f"https://api.jikan.moe/v4/anime/{anime_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()  # Parse JSON response

        # Extract relevant information
        episodes = data['data']['episodes']
        return episodes  # Return number of episodes

    except requests.exceptions.RequestException as e:
        print(f"Error fetching info for anime ID {anime_id}: {e}")
        return None

def main():
    # Split the input data by lines 
    anime_lines = anime_data.strip().split('\n')

    # Initialize a dictionary to hold lists for each category 
    anime_status = {}
    current_status = None  # Variable to keep track of the current status

    # Define a mapping for status display names
    status_mapping = {
        "completed": "Completed",
        "plan_to_watch": "Plan to Watch",
        "watching": "Watching",
        "on-hold": "On-Hold",
        "dropped": "Dropped"
    }

    # Loop through the lines to categorize anime entries with a progress bar
    for line in tqdm(anime_lines, desc="Categorizing Anime Entries", unit="entry"):
        line = line.strip()
        if line.startswith("#"):  # Detect the status 
            current_status = line[2:].strip().lower().replace(" ", "_")  # Format status name for internal use
            if current_status not in anime_status:  # Initialize list for new status if it doesn't exist 
                anime_status[current_status] = []
        elif "|" in line and current_status:  # If there's a pipe character, it's an anime title with URL
            anime_status[current_status].append(line)

    # Creating XML data structure 
    xml_data = '<?xml version="1.0" encoding="UTF-8"?>\n<myanimelist>\n'
    xml_data += '\t<myinfo>\n\t\t<user_export_type>1</user_export_type>\n\t</myinfo>\n'

    # Adding anime entries to XML data based on their statuses with a progress bar
    for status, anime_list in tqdm(anime_status.items(), desc="Generating XML Entries", unit="category"):
        for anime in tqdm(anime_list, leave=False):  # Nested progress bar for each category
            name, url = [part.strip() for part in anime.split("|")]
            series_id = url.split('/')[-1]  # Extracting series_id from URL

            if status == "plan_to_watch":
                episodes = 0  # Automatically set episodes to 0 for Plan to Watch
            elif status == "dropped":
                episodes = 1  # Automatically set episodes to 1 for Dropped
            elif status in ["watching", "on-hold"]:
                episodes = input(f"Enter number of episodes watched for '{name}': ")  # User input for Watching and On-Hold
                while not episodes.isdigit():  # Ensure valid input (non-negative integer)
                    print("Please enter a valid number.")
                    episodes = input(f"Enter number of episodes watched for '{name}': ")
                episodes = int(episodes)  # Convert input to integer
            else:
                episodes = get_anime_info(series_id)  # Fetch episode information using series_id

            entry_string = (
                "\t<anime>\n"
                f"\t\t<series_animedb_id>{series_id}</series_animedb_id>\n"
                f"\t\t<series_title><![CDATA[{name}]]></series_title>\n"
                f"\t\t<my_watched_episodes>{episodes}</my_watched_episodes>\n"  # Use appropriate episode count based on status
                f"\t\t<my_status>{status_mapping[status]}</my_status>\n"  # Use mapped status name for display
                "\t\t<update_on_import>1</update_on_import>\n"
                "\t</anime>\n"
            )
            xml_data += entry_string

            time.sleep(2)  # Delay of 2 seconds between requests

    xml_data += '</myanimelist>'

    # Writing the XML data to a file 
    save_path = "anime_data.xml" 
    with open(save_path, "w") as file: 
        file.write(xml_data)

    print(f"✅ Saving file at {save_path}") 

if __name__ == "__main__":
    main()