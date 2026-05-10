# Conexión a la DB (Niveles, Tickets, Config)
import sqlite3
import os

DB_PATH = 'rra_engine.db'

def init_database():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de Niveles y XP
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS levels (
            user_id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            last_xp_time INTEGER DEFAULT 0
        )
    ''')
    
    # Tabla de Tickets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            channel_id INTEGER,
            status TEXT DEFAULT 'open',
            created_at INTEGER,
            closed_at INTEGER DEFAULT NULL
        )
    ''')
    
    # Tabla de Configuración
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            guild_id INTEGER PRIMARY KEY,
            prefix TEXT DEFAULT '!',
            mod_role_id INTEGER DEFAULT NULL,
            support_role_id INTEGER DEFAULT NULL,
            ticket_category_id INTEGER DEFAULT NULL
        )
    ''')
    
    # Tabla de Warns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warns (
            warn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            guild_id INTEGER,
            reason TEXT,
            moderator_id INTEGER,
            warn_date INTEGER
        )
    ''')
    
    # Tabla de Sorteos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS giveaways (
            giveaway_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            channel_id INTEGER,
            message_id INTEGER,
            prize TEXT,
            winners INTEGER DEFAULT 1,
            end_time INTEGER,
            participants TEXT DEFAULT '',
            status TEXT DEFAULT 'active'
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_level(user_id):
    """Obtiene el nivel y XP de un usuario"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT level, xp FROM levels WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result or (1, 0)

def add_xp(user_id, xp_amount):
    """Añade XP a un usuario"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    current_level, current_xp = get_user_level(user_id)
    new_xp = current_xp + xp_amount
    new_level = 1 + (new_xp // 100)  # Cada 100 XP = 1 nivel
    
    cursor.execute('''
        INSERT OR REPLACE INTO levels (user_id, xp, level)
        VALUES (?, ?, ?)
    ''', (user_id, new_xp, new_level))
    
    conn.commit()
    conn.close()
    
    return new_level > current_level  # True si subió de nivel

def create_ticket(user_id, channel_id):
    """Crea un nuevo ticket"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    import time
    
    cursor.execute('''
        INSERT INTO tickets (user_id, channel_id, created_at)
        VALUES (?, ?, ?)
    ''', (user_id, channel_id, int(time.time())))
    
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return ticket_id

def close_ticket(ticket_id):
    """Cierra un ticket"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    import time
    
    cursor.execute('''
        UPDATE tickets SET status = 'closed', closed_at = ?
        WHERE ticket_id = ?
    ''', (int(time.time()), ticket_id))
    
    conn.commit()
    conn.close()

def get_leaderboard(guild_id, limit=10):
    """Obtiene el leaderboard de un servidor"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, level, xp FROM levels
        ORDER BY level DESC, xp DESC
        LIMIT ?
    ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

# Inicializar DB al importar
if __name__ == '__main__':
    init_database()
    print('Base de datos inicializada')
