# db.py
import sqlite3
from contextlib import closing
from config import DATABASE
import time

def init_db():
    with closing(sqlite3.connect(DATABASE)) as con:
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                redeemed_free INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                is_premium INTEGER DEFAULT 0,
                premium_expires INTEGER DEFAULT 0
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS keys(
                key TEXT PRIMARY KEY,
                days INTEGER,
                used INTEGER DEFAULT 0,
                used_by INTEGER,
                used_on INTEGER,
                generated_by INTEGER,
                generated_on INTEGER
            )
        ''')
        con.commit()

def get_conn():
    return sqlite3.connect(DATABASE, check_same_thread=False)

# user helpers

def ensure_user(user_id, username=None):
    con = get_conn()
    cur = con.cursor()
    cur.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    if not cur.fetchone():
        cur.execute('INSERT INTO users(user_id, username) VALUES(?,?)', (user_id, username))
        con.commit()
    con.close()

def set_redeemed_free(user_id):
    con = get_conn(); cur = con.cursor()
    cur.execute('UPDATE users SET redeemed_free=1 WHERE user_id=?', (user_id,))
    con.commit(); con.close()

def has_redeemed_free(user_id):
    con = get_conn(); cur = con.cursor()
    cur.execute('SELECT redeemed_free FROM users WHERE user_id=?', (user_id,))
    r = cur.fetchone(); con.close()
    return bool(r and r[0])

def ban_user(user_id):
    con = get_conn(); cur = con.cursor()
    cur.execute('UPDATE users SET is_banned=1 WHERE user_id=?', (user_id,))
    con.commit(); con.close()

def unban_user(user_id):
    con = get_conn(); cur = con.cursor()
    cur.execute('UPDATE users SET is_banned=0 WHERE user_id=?', (user_id,))
    con.commit(); con.close()

def is_banned(user_id):
    con = get_conn(); cur = con.cursor()
    cur.execute('SELECT is_banned FROM users WHERE user_id=?', (user_id,))
    r = cur.fetchone(); con.close()
    return bool(r and r[0])

# premium helpers

def activate_premium(user_id, days):
    expires = int(time.time()) + days * 24 * 3600
    con = get_conn(); cur = con.cursor()
    cur.execute('UPDATE users SET is_premium=1, premium_expires=? WHERE user_id=?', (expires, user_id))
    con.commit(); con.close()

def is_premium(user_id):
    con = get_conn(); cur = con.cursor()
    cur.execute('SELECT is_premium, premium_expires FROM users WHERE user_id=?', (user_id,))
    r = cur.fetchone(); con.close()
    if not r:
        return False
    is_p, exp = r
    if is_p and exp > int(time.time()):
        return True
    # expired -> demote
    if is_p and exp <= int(time.time()):
        con = get_conn(); cur = con.cursor(); cur.execute('UPDATE users SET is_premium=0 WHERE user_id=?', (user_id,)); con.commit(); con.close()
        return False
    return False

# keys

def add_key(key, days, generated_by):
    con = get_conn(); cur = con.cursor()
    cur.execute('INSERT OR REPLACE INTO keys(key, days, generated_by, generated_on, used) VALUES(?,?,?,?,0)', (key, days, generated_by, int(time.time())))
    con.commit(); con.close()

def use_key(key, user_id):
    con = get_conn(); cur = con.cursor()
    cur.execute('SELECT days, used FROM keys WHERE key=?', (key,))
    r = cur.fetchone()
    if not r:
        con.close(); return None
    days, used = r
    if used:
        con.close(); return False
    cur.execute('UPDATE keys SET used=1, used_by=?, used_on=? WHERE key=?', (user_id, int(time.time()), key))
    con.commit(); con.close()
    return days

def key_exists_unused(key):
    con = get_conn(); cur = con.cursor()
    cur.execute('SELECT used FROM keys WHERE key=?', (key,))
    r = cur.fetchone(); con.close()
    return bool(r and r[0]==0)

# iterate users for broadcast

def get_all_users():
    con = get_conn(); cur = con.cursor()
    cur.execute('SELECT user_id FROM users')
    rows = cur.fetchall(); con.close()
    return [r[0] for r in rows]

if __name__ == '__main__':
    init_db()