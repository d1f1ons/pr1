import sqlite3
import os
from src.config import DB_PATH


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Таблица процессов (state и memory_used в соответствии с методичкой)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS processes (
        pid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        state TEXT NOT NULL DEFAULT 'ready',
        owner TEXT NOT NULL,
        memory_used INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Таблица файлов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        content TEXT,
        owner TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Таблица состояния памяти (Задание 3)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS memory_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        used INTEGER DEFAULT 0,
        limit_val INTEGER DEFAULT 1024
    )
    ''')

    # Таблица журнала системных вызовов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS syscalls_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        syscall_name TEXT NOT NULL,
        arguments TEXT,
        user TEXT NOT NULL,
        status TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Тестовый администратор
    cursor.execute('''
    INSERT OR IGNORE INTO users (login, password_hash, role)
    VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin')
    ''')

    conn.commit()
    conn.close()
    print("База данных успешно инициализирована.")


def execute_insert(table: str, data: dict):
    """Вставляет запись в таблицу. data — словарь (поле: значение)."""
    keys = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, tuple(data.values()))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


def execute_select(table: str, conditions: dict = None):
    """Возвращает записи из таблицы. conditions — словарь (поле: значение)."""
    sql = f"SELECT * FROM {table}"
    params = ()
    if conditions:
        where = " AND ".join([f"{k} = ?" for k in conditions.keys()])
        sql += f" WHERE {where}"
        params = tuple(conditions.values())
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return result


def execute_update(table: str, data: dict, conditions: dict):
    """Обновляет записи. data — что менять, conditions — по какому условию."""
    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
    where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, tuple(data.values()) + tuple(conditions.values()))
    conn.commit()
    conn.close()


def execute_delete(table: str, conditions: dict = None):
    """Удаляет записи по условию. Если conditions не передан или пуст — очищает таблицу."""
    conn = get_connection()
    cursor = conn.cursor()
    if conditions:
        where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
        sql = f"DELETE FROM {table} WHERE {where_clause}"
        cursor.execute(sql, tuple(conditions.values()))
    else:
        sql = f"DELETE FROM {table}"
        cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()