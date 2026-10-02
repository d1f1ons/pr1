"""Модуль системных вызовов с логированием и проверкой прав."""

import json
from src import auth, db, fs, scheduler
from src.db import get_connection


def log_syscall(syscall_name: str, args: dict, user: str, status: str):
    """Записывает системный вызов в журнал базы данных."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO syscalls_log (syscall_name, arguments, user, status) VALUES (?, ?, ?, ?)",
            (syscall_name, json.dumps(args), user, status),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[LOG ERROR] Не удалось записать лог: {e}")


# --- Системные вызовы ядра и аутентификации ---


def sys_echo(message: str, current_user: str = "guest") -> str:
    """Возвращает переданное сообщение."""
    log_syscall("sys_echo", {"message": message}, current_user, "SUCCESS")
    return message


def sys_get_users(current_user: str = "guest"):
    """Возвращает список пользователей (с проверкой прав)."""
    if not auth.check_permission(current_user, "get_users"):
        log_syscall("sys_get_users", {}, current_user, "DENIED")
        return "Ошибка: Недостаточно прав"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, login, role, created_at FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()

    log_syscall("sys_get_users", {}, current_user, "SUCCESS")
    return users


def sys_register(login: str, password_hash: str, role: str = "user", current_user: str = "guest"):
    """Регистрирует нового пользователя."""
    user_id = auth.register_user(login, password_hash, role)
    if user_id is None:
        log_syscall("sys_register", {"login": login, "role": role}, current_user, "ERROR_EXISTS")
        return "Ошибка: Пользователь уже существует"

    log_syscall("sys_register", {"login": login, "role": role}, current_user, "SUCCESS")
    return f"Пользователь создан с ID {user_id}"


def sys_login(login: str, password_hash: str, current_user: str = "guest"):
    """Аутентифицирует пользователя."""
    user = auth.authenticate(login, password_hash)
    if user:
        log_syscall("sys_login", {"login": login}, current_user, "SUCCESS")
        return f"Успешный вход: {user['login']} ({user['role']})"

    log_syscall("sys_login", {"login": login}, current_user, "DENIED")
    return "Ошибка: Неверный логин или пароль"


def sys_whoami(current_user: str = "guest") -> str:
    """Возвращает текущего пользователя."""
    log_syscall("sys_whoami", {}, current_user, "SUCCESS")
    return current_user


def sys_logs(limit: int = 10, current_user: str = "guest"):
    """Возвращает последние записи из журнала системных вызовов."""
    if not auth.check_permission(current_user, "read_logs"):
        log_syscall("sys_logs", {"limit": limit}, current_user, "DENIED")
        return "Ошибка: Недостаточно прав"

    logs = db.execute_select("syscalls_log")
    log_syscall("sys_logs", {"limit": limit}, current_user, "SUCCESS")
    return logs[-limit:]


# --- Вызовы Файловой Системы ---


def sys_create_file(path: str, content: str, current_user: str = "guest"):
    """Создает файл."""
    log_syscall("sys_create_file", {"path": path}, current_user, "check")
    file_id = fs.create_file(path, content, current_user)
    if file_id == -1:
        log_syscall("sys_create_file", {"path": path}, current_user, "EXISTS")
        return -1
    log_syscall("sys_create_file", {"path": path}, current_user, "OK")
    return file_id


def sys_read_file(path: str, current_user: str = "guest") -> str:
    """Читает содержимое файла."""
    log_syscall("sys_read_file", {"path": path}, current_user, "check")
    content = fs.read_file(path)
    log_syscall("sys_read_file", {"path": path}, current_user, "OK")
    return content


def sys_list_files(prefix: str = "", current_user: str = "guest") -> list:
    """Возвращает список файлов."""
    log_syscall("sys_list_files", {"prefix": prefix}, current_user, "OK")
    return fs.list_files(prefix)


def sys_delete_file(path: str, current_user: str = "guest") -> bool:
    """Удаляет файл с проверкой прав владельца."""
    log_syscall("sys_delete_file", {"path": path}, current_user, "check")
    owner = fs.get_owner(path)
    if owner is None:
        log_syscall("sys_delete_file", {"path": path}, current_user, "NOT_FOUND")
        return False
    if not auth.check_permission(current_user, "delete_file", owner):
        log_syscall("sys_delete_file", {"path": path}, current_user, "DENIED")
        return False
    fs.delete_file(path)
    log_syscall("sys_delete_file", {"path": path}, current_user, "OK")
    return True


# --- Вызовы Планировщика Процессов ---


def sys_exec(name: str, current_user: str = "guest"):
    """Запускает процесс."""
    log_syscall("sys_exec", {"name": name}, current_user, "check")
    pid = scheduler.create_process(name, current_user)
    if pid == -1:
        log_syscall("sys_exec", {"name": name}, current_user, "NO_MEMORY")
        return -1
    log_syscall("sys_exec", {"name": name}, current_user, "OK")
    return pid


def sys_ps(current_user: str = "guest") -> list:
    """Возвращает список запущенных процессов."""
    log_syscall("sys_ps", {}, current_user, "OK")
    return scheduler.list_processes()


def sys_kill(pid: int, current_user: str = "guest") -> bool:
    """Завершает процесс с проверкой прав."""
    log_syscall("sys_kill", {"pid": pid}, current_user, "check")
    if not auth.check_permission(current_user, "kill"):
        log_syscall("sys_kill", {"pid": pid}, current_user, "DENIED")
        return False
    result = scheduler.terminate_process(pid)
    log_syscall("sys_kill", {"pid": pid}, current_user, "OK" if result else "NOT_FOUND")
    return result