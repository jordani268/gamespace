import random
import sqlite3
import requests

# Constants for the RAWG API
API_KEY = '21c85d8bbca64d1290efcb076da0ea92'
url = "https://api.rawg.io/api/games"

# Setup headers and params correctly for RapidAPI
headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'rawg-video-games-database.p.rapidapi.com'
}

# Parameters for fetching games
params = {
    'key': API_KEY,
    'page_size': 50,         # Limit the number of results per page (increase the page size)
    'page': 1
}

# Connect to SQLite database (or create it)
conn = sqlite3.connect('games.db')
cursor = conn.cursor()

# Create a table for games if it doesn't exist
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,
    name TEXT,
    released DATE,
    rating REAL,
    platforms TEXT,
    genre TEXT  -- Add a genre column for easier filtering
)
''')
conn.commit()

# Check if 'genre' and 'platforms' columns exist, if not, add them
cursor.execute("PRAGMA table_info(games);")
columns = [column[1] for column in cursor.fetchall()]

# Alter the table to add missing columns
if 'genre' not in columns:
    cursor.execute(''' 
        ALTER TABLE games ADD COLUMN genre TEXT;
    ''')
if 'platforms' not in columns:
    cursor.execute(''' 
        ALTER TABLE games ADD COLUMN platforms TEXT;
    ''')
conn.commit()

# Fetch games data from RAWG API and insert into database
def fetch_and_store_games():
    try:
        for page in range(1, 51):  # Fetching 50 pages
            print(f"Fetching data for page {page}...")
            params['page'] = page  # Update the page number for each request
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            games_data = response.json()
            print(f"Page {page} fetched successfully.")

            for game in games_data['results']:
                # Safely handle the genres and platforms (account for missing keys)
                genres = ', '.join([genre['name'] for genre in game.get('genres', [])])  # Collect genres
                platforms = ', '.join([platform['platform']['name'] for platform in game.get('platforms', [])])  # Collect platforms safely
                
                cursor.execute(''' 
                INSERT OR IGNORE INTO games (id, name, released, rating, platforms, genre)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (game['id'], game['name'], game['released'], game['rating'], platforms, genres))
            conn.commit()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from RAWG API: {e}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Function to introduce and gather user preferences
def introduction():
    platforms = []
    print("Hello! Welcome to Gamespace!")
    genre = input("1. What is your favorite game genre? Example: RPG\n")
    
    print("2. Please enter the platforms you have. Type '0' when you are done. Type Platforms to see the available platforms.")
    while True:
        platform = input(f"Platform {len(platforms) + 1}: ")
        if platform == "0":
            break
        if platform == "Platforms":
            print("Android, Classic Macintosh, Dreamcast, Game Boy Advance, GameCube, Linux,\n Nintendo 3DS, Nintendo 64, Nintendo DS, Nintendo Switch, PC, PS Vita, PlayStation,\n PlayStation 2, PlayStation 3, PlayStation 4, PlayStation 5, SEGA Saturn, Web, Wii,\n Wii U, Xbox, Xbox 360, Xbox One, Xbox Series S/X, iOS, macOS")
        platforms.append(platform.lower())  # Convert platform input to lowercase

    return genre, platforms

# Function to search for and calculate game recommendations based on user input
def results_and_calculations(genre, platforms):
    print("Searching the Cosmos...")

    # Create a list to hold recommended games
    recommended_games = []

    # Normalize user input for case-insensitive comparison
    genre_lower = genre.lower()

    # Debugging: Print the user preferences
    print(f"\nUser preferences: Genre: {genre_lower}, Platforms: {platforms}")

    for platform in platforms:
        platform_normalized = platform.strip().lower()  # Normalize the user input platform (remove spaces, convert to lowercase)
        print(f"\nChecking for platform: {platform_normalized}")  # Debugging the current platform
        
        cursor.execute('SELECT * FROM games WHERE platforms LIKE ?', ('%' + platform_normalized + '%',))
        games_for_platform = cursor.fetchall()

        # Debugging: Check if games were found for the platform
        print(f"Found {len(games_for_platform)} games for platform '{platform_normalized}'.")

        # Filter by genre (now we check the genre column explicitly and perform case-insensitive matching)
        for game in games_for_platform:
            # Normalize the platforms stored in the database to lowercase for comparison
            game_platforms = game[4].lower()  # game[4] contains the platform(s) column
            
            print(f"Comparing with game: {game[1]} - Genre: {game[5]}")  # Debugging the genre of each game

            if platform_normalized in game_platforms and genre_lower in game[5].lower():  # Case-insensitive comparison
                recommended_games.append(game)

    if recommended_games:
        print("\nRecommended Games:")
        for game in recommended_games:
            print(f"- {game[1]} (Released: {game[2]}, Rating: {game[3]}, Genre: {game[5]})")
        
        # Random game feature
        random_game = random.choice(recommended_games)
        print(f"\nRandom Game Suggestion: {random_game[1]} (Released: {random_game[2]}, Rating: {random_game[3]}, Genre: {random_game[5]})")
    else:
        print("No recommendations found for your preferences.")

# Main function to run the program
def main():
    fetch_and_store_games()  # Fetch and store games from RAWG API before starting
    genre, platforms = introduction()
    results_and_calculations(genre, platforms)
    conn.close()  # Close the database connection

if __name__ == "__main__":
    main()
