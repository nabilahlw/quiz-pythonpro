import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = 'quiz.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabel users untuk menyimpan data pengguna
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nickname TEXT UNIQUE NOT NULL,
            score INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def register_user(username, password, nickname):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        cursor.execute('''
            INSERT INTO users (username, password, nickname, score)
            VALUES (?, ?, ?, 0)
        ''', (username, hashed_password, nickname))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        print(f"✅ User registered: {username} (ID: {user_id})")
        return True
    except sqlite3.IntegrityError as e:
        print(f"❌ IntegrityError: {e}")
        return False
    except Exception as e:
        print(f"❌ Error registering user: {e}")
        return False

def check_user(username, password):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, nickname, score, password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            print(f"🔍 User found: {username}")
            if check_password_hash(user[3], password):
                print(f"✅ Password correct for: {username}")
                return (user[0], user[1], user[2])  # id, nickname, score
            else:
                print(f"❌ Password incorrect for: {username}")
                return None
        else:
            print(f"❌ User not found: {username}")
            return None
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return None

def username_exists(username):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        exists = cursor.fetchone() is not None
        conn.close()
        print(f"🔍 Username '{username}' exists: {exists}")
        return exists
    except Exception as e:
        print(f"❌ Error checking username: {e}")
        return False

def nickname_exists(nickname):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE nickname = ?', (nickname,))
        exists = cursor.fetchone() is not None
        conn.close()
        print(f"🔍 Nickname '{nickname}' exists: {exists}")
        return exists
    except Exception as e:
        print(f"❌ Error checking nickname: {e}")
        return False

def update_user_score(user_id, points):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET score = score + ? WHERE id = ?', (points, user_id))
        
        conn.commit()
        conn.close()
        print(f"✅ Score updated: User ID {user_id} +{points} points")
        return True
    except Exception as e:
        print(f"❌ Error updating score: {e}")
        return False

def get_user_score(user_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT score FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        score = result[0] if result else 0
        print(f"📊 User ID {user_id} score: {score}")
        return score
    except Exception as e:
        print(f"❌ Error getting score: {e}")
        return 0

def get_leaderboard(limit=10):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT nickname, score 
            FROM users 
            ORDER BY score DESC 
            LIMIT ?
        ''', (limit,))
        
        leaderboard = cursor.fetchall()
        conn.close()
        
        print(f"🏆 Leaderboard fetched: {len(leaderboard)} players")
        return [(row[0], row[1]) for row in leaderboard]
    except Exception as e:
        print(f"❌ Error getting leaderboard: {e}")
        return []

def reset_database():
    """Debug function to reset database"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS users')
        conn.commit()
        conn.close()
        print("🗑️ Database reset!")
        init_db()
    except Exception as e:
        print(f"❌ Error resetting database: {e}")

# Initialize database when module is imported
if __name__ == "__main__":
    print("Initializing database...")
    init_db()