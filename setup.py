import sqlite3
import requests

def create_database():
    # Connect to SQLite database (it will create the database file if it doesn't exist)
    conn = sqlite3.connect('pokemon.db')
    cursor = conn.cursor()

    # Create a table for Pokémon
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pokemon (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            height REAL,
            weight REAL,
            hp INTEGER,
            attack INTEGER,
            defense INTEGER,
            special_attack INTEGER,
            special_defense INTEGER,
            image_url TEXT
        )
    ''')

    # Fetch Pokémon data from PokeAPI
    for i in range(1, 152):  # Fetching first 151 Pokémon
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{i}')
        if response.status_code == 200:
            data = response.json()
            name = data['name']
            height = data['height']
            weight = data['weight']
            hp = data['stats'][0]['base_stat']
            attack = data['stats'][1]['base_stat']
            defense = data['stats'][2]['base_stat']
            special_attack = data['stats'][3]['base_stat']
            special_defense = data['stats'][4]['base_stat']
            types = ', '.join([t['type']['name'] for t in data['types']])  # Join multiple types
            
            # Get the front_default image URL from sprites
            image_url = data['sprites']['front_default']

            # Insert data into the database
            cursor.execute('''
                INSERT OR IGNORE INTO pokemon (id, name, type, height, weight, hp, attack, defense, special_attack, special_defense, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (i, name, types, height, weight, hp, attack, defense, special_attack, special_defense, image_url))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    print("Database created and Pokémon data inserted.")
