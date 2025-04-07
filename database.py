import sqlite3

DB_NAME_TEAMS = "teams.db"
DB_NAME_MATCHES = "game_data.db"

def init_db():
    """Initialize the teams database."""
    conn = sqlite3.connect(DB_NAME_TEAMS)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        logo TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY (team_id) REFERENCES teams(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fixtures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team1_id INTEGER NOT NULL,
        team2_id INTEGER NOT NULL,
        score TEXT NOT NULL,
        FOREIGN KEY (team1_id) REFERENCES teams(id),
        FOREIGN KEY (team2_id) REFERENCES teams(id)
    )""")

    conn.commit()
    conn.close()

def create_matches_table():
    """Create the matches table in game_data.db"""
    conn = sqlite3.connect(DB_NAME_MATCHES)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team1_name TEXT NOT NULL,
            team2_name TEXT NOT NULL,
            team1_score INTEGER DEFAULT 0,
            team2_score INTEGER DEFAULT 0,
            margin INTEGER DEFAULT 0,
            live Boolean DEFAULT 0,
            match_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def save_match(team1, team2, score1, score2, margin):
    """Save match details to the database"""
    conn = sqlite3.connect(DB_NAME_MATCHES)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO matches (team1_name, team2_name, team1_score, team2_score, margin)
        VALUES (?, ?, ?, ?, ?)
    ''', (team1, team2, score1, score2, margin))

    conn.commit()
    conn.close()

def get_matches():
    """Retrieve match history"""
    conn = sqlite3.connect(DB_NAME_MATCHES)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM matches ORDER BY match_date DESC")
    matches = cursor.fetchall()

    conn.close()
    return matches

def get_teams():
    """Retrieve team data"""
    conn = sqlite3.connect(DB_NAME_TEAMS)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM teams")
    teams = cursor.fetchall()

    conn.close()
    return teams

def save_team(name, logo):
    """Save team data to the database"""
    conn = sqlite3.connect(DB_NAME_TEAMS)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO teams (name, logo)
        VALUES (?, ?)
    ''', (name, logo))
    conn.commit()
    conn.close()

def save_matches(team1, team2, score1, score2, margin):
    """Save team data to the database"""
    conn = sqlite3.connect(DB_NAME_TEAMS)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO teams (team1, team2, score1, score2, margin)
        VALUES (?, ?)
    ''', (team1, team2, score1, score2, margin))

    conn.commit()
    conn.close()

    conn.commit()
    conn.close()

def delete_team(team_id):
    """Delete a team from the database."""
    conn = sqlite3.connect("teams.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
    conn.commit()
    conn.close()

def get_team_logo(team_name):
    """Retrieve team logo from the database"""
    conn = sqlite3.connect(DB_NAME_TEAMS)
    cursor = conn.cursor()

    cursor.execute("SELECT logo FROM teams WHERE name=?", (team_name,))
    logo = cursor.fetchone()

    conn.close()
    return logo[0] if logo else None

def get_team_by_id(team_id):
    """Fetch a team by its ID from the database."""
    conn = sqlite3.connect('teams.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    team = cursor.fetchone()
    conn.close()
    return team

# Initialize databases
init_db()
create_matches_table()
