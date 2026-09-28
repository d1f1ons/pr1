import json
from .db import get_connection
def log_syscall(syscall_name: str, args: dict, user: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO syscalls_log (syscall_name, arguments, user, status) VALUES (?, ?, ?, ?)",
        (syscall_name, json.dumps(args), user, status)
    )
    conn.commit()
    conn.close()

def sys_echo(message: str, user: str = "guest") -> str:
    log_syscall("sys_echo", {"message": message}, user, "SUCCESS")
    return message

def sys_get_users(user: str = "guest") -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    log_syscall("sys_get_users", {}, user, "SUCCESS")
    return users