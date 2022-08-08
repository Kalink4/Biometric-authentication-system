import sqlite3
import numpy as np
import io

# преобразование np.array в TEXT при вставке в ДБ
def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

# преобразование TEXT в np.array при извлечении из БД
def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)
sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("array", convert_array)
def create_db():
    conn = sqlite3.connect(r'profiles.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        nickname TEXT PRIMARY KEY,
        face_features array);
                """)
    conn.commit()
    conn.close()

def create_profile(nickname,face_features):
    conn = sqlite3.connect(r'profiles.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE nickname = (?);", (nickname,))
    results=cur.fetchone()
    if results==None:
        cur.execute("INSERT INTO users VALUES(?, ?);", (nickname,face_features))
        conn.commit()
    conn.close()


def get_user(nickname):
    conn = sqlite3.connect(r'profiles.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users where nickname=(?)",(nickname,))
    result=cur.fetchone()[1]
    conn.close()
    return result

def get_users():
    conn = sqlite3.connect(r'profiles.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ")
    result=cur.fetchall()
    conn.close()
    return result

def get_users_nicknames():
    conn = sqlite3.connect(r'profiles.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    cur.execute("SELECT nickname FROM users ")
    result=cur.fetchall()
    conn.close()
    return result

def remove_user(nickname):
    conn = sqlite3.connect(r'profiles.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE nickname=(?)",(nickname,))
    conn.commit()
    print("Успешно удалено")
    conn.close()

create_db()