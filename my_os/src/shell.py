import sys
from .db import init_db
from .syscalls import sys_echo, sys_get_users

def main():
    init_db()
    current_user = "admin"

    print("=" * 45)
    print("      Учебная Операционная Система v0.1")
    print("      AntiGravity Environment / Shell Mode")
    print("      Введите 'help' для списка доступных команд")
    print("=" * 45)

    while True:
        try:
            cmd_input = input(f"[{current_user}@my_os]$ ").strip()
            if not cmd_input:
                continue

            parts = cmd_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == "exit":
                print("Завершение работы ОС...")
                break
            elif command == "help":
                print("Доступные команды: help, echo, users, exit")
            elif command == "echo":
                print(sys_echo(args, user=current_user))
            elif command == "users":
                users = sys_get_users(user=current_user)
                for u in users:
                    print(f"ID: {u['id']} | User: {u['username']} | Role: {u['role']}")
            else:
                print(f"Ошибка: неизвестная команда '{command}'")

        except (KeyboardInterrupt, EOFError):
            print("\nЗавершение работы ОС...")
            break

if __name__ == "__main__":
    main()