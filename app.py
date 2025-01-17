from flask import Flask, jsonify, request, render_template, send_file, make_response
import sqlite3
import io

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('pokemon.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Serve the homepage."""
    return render_template('index.html')

@app.route('/pokemon', methods=['GET'])
def get_pokemon():
    """Return Pokémon data for display."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page

    # Search and Filter
    search = request.args.get('search', '')
    pokemon_type = request.args.get('type', '')

    query = 'SELECT id, name, type FROM pokemon WHERE name LIKE ?'
    params = [f'%{search}%']

    if pokemon_type:
        query += ' AND type LIKE ?'
        params.append(f'%{pokemon_type}%')

    query += ' LIMIT ? OFFSET ?'
    params.append(per_page)
    params.append(offset)

    cursor.execute(query, params)
    pokemons = cursor.fetchall()

    # Get total count for pagination
    count_query = 'SELECT COUNT(*) FROM pokemon WHERE name LIKE ?'
    if pokemon_type:
        count_query += ' AND type LIKE ?'
    cursor.execute(count_query, params[:-2])
    total_count = cursor.fetchone()[0]

    conn.close()

    # Add dynamic links for Pokémon details and images
    return jsonify({
        'pokemons': [
            {
                **dict(pokemon),
                'detail_url': f'/pokemon/{pokemon["id"]}',  # Link to Pokémon detail page
                'image_url': f'/pokemon/{pokemon["id"]}/image'  # Link to Pokémon image
            }
            for pokemon in pokemons
        ],
        'total_count': total_count,
        'per_page': per_page,
        'current_page': page
    })

@app.route('/pokemon/<int:pokemon_id>', methods=['GET'])
def get_pokemon_details(pokemon_id):
    """Serve Pokémon detail page."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch Pokémon details
    cursor.execute('SELECT * FROM pokemon WHERE id = ?', (pokemon_id,))
    pokemon = cursor.fetchone()

    if pokemon is None:
        return jsonify({'error': 'Pokemon not found'}), 404

    # Find similar Pokémon
    cursor.execute('SELECT * FROM pokemon WHERE type LIKE ? AND id != ? LIMIT 3', (pokemon['type'], pokemon_id))
    similar_pokemons = cursor.fetchall()

    conn.close()

    return render_template('pokemon_detail.html', pokemon=dict(pokemon), similar=[dict(similar) for similar in similar_pokemons])

@app.route('/pokemon/<int:pokemon_id>/image', methods=['GET'])
def get_pokemon_image(pokemon_id):
    """Serve Pokémon image."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT image_blob FROM pokemon WHERE id = ?', (pokemon_id,))
    result = cursor.fetchone()
    conn.close()

    if result and result['image_blob']:
        return make_response(send_file(io.BytesIO(result['image_blob']), mimetype='image/png'))
    else:
        return jsonify({'error': 'Image not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
