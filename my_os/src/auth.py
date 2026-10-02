"""Модуль аутентификации и проверки прав доступа."""
import hashlib
import src.db as db


def hash_password(password: str) -> str:
    """Хэширует пароль алгоритмом SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(login: str, password: str, role: str = "user"):
    """Регистрирует нового пользователя. Возвращает user_id или None."""
    existing = db.execute_select("users", {"login": login})
    if existing:
        return None

    user_id = db.execute_insert(
        "users",
        {
            "login": login,
            "password_hash": hash_password(password),
            "role": role,
        },
    )
    return user_id


def authenticate(login: str, password: str):
    """Проверяет логин и пароль. Возвращает пользователя или None."""
    users = db.execute_select("users", {"login": login})
    if not users:
        return None

    user = users[0]
    if user["password_hash"] == hash_password(password):
        return user
    return None


def check_permission(current_user: str, action: str, target_owner: str = None) -> bool:
    """Проверяет права доступа текущего пользователя."""
    users = db.execute_select("users", {"login": current_user})
    if not users:
        return False

    role = users[0]["role"]
    if role == "admin":
        return True

    if action in ("delete_file", "kill") and target_owner and target_owner != current_user:
        return False

    return True