"""Модуль командной оболочки."""

from src.kernel import kernel_instance
from src.syscalls import (
    sys_login, sys_whoami, sys_get_users, sys_register,
    sys_create_file, sys_read_file, sys_delete_file, sys_list_files,
    sys_exec, sys_ps, sys_kill, sys_logs
)


def run_shell():
    print("=== Учебная ОС запущена ===")
    print("Команды: login, whoami, users, register, create, cat, ls, run, ps, kill, mem, logs, exit\n")

    while True:
        user = kernel_instance.get_user()
        try:
            cmd_input = input(f"[{user}@my_os]$ ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nЗавершение работы...")
            break

        if not cmd_input:
            continue

        parts = cmd_input.split()
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "exit":
            print("Завершение сеанса.")
            break

        elif cmd == "whoami":
            print(f"Текущий пользователь: {user}")

        elif cmd == "login":
            login_arg = input("Логин: ")
            pwd_arg = input("Пароль: ")
            res = sys_login(login_arg, pwd_arg, user)
            print(res)
            if "Успешный вход" in res:
                kernel_instance.set_user(login_arg)

        elif cmd == "users":
            res = sys_get_users(user)
            if isinstance(res, list):
                for u in res:
                    print(f"ID: {u['id']} | Логин: {u['login']} | Роль: {u['role']}")
            else:
                print(res)

        elif cmd == "cat":
            if not arg:
                print("Укажите путь к файлу")
            else:
                content = sys_read_file(arg, user)
                print(content if content else "(файл пуст или не существует)")

        elif cmd == "run":
            if not arg:
                print("Укажите имя программы")
            else:
                pid = sys_exec(arg, user)
                if pid == -1:
                    print("Не удалось запустить: нет свободной памяти")
                else:
                    print(f"Запущен процесс с PID={pid}")

        elif cmd == "kill":
            if not arg:
                print("Укажите PID процесса")
            else:
                try:
                    pid = int(arg)
                except ValueError:
                    print("PID должен быть числом")
                    continue
                if sys_kill(pid, user):
                    print(f"Процесс {pid} завершён")
                else:
                    print(f"Не удалось завершить процесс {pid}")

        elif cmd == "ls":
            files = sys_list_files(arg or "/", user)
            if not files:
                print("(нет файлов)")
            else:
                for f in files:
                    print(f"  {f}")

        elif cmd == "create":
            path = input("Путь: ")
            content = input("Содержимое: ")
            fid = sys_create_file(path, content, user)
            if fid == -1:
                print("Файл с таким путём уже существует")
            else:
                print(f"Создан файл с id={fid}")

        elif cmd == "mem":
            info = kernel_instance.memory_info()
            print(f"Использовано: {info['used']} / {info['limit']} МБ")
            print(f"Свободно: {info['free']} МБ")

        elif cmd == "logs":
            res = sys_logs(10, user)
            for log in res:
                print(f"[{log['timestamp']}] User: {log['user']} | Call: {log['syscall_name']} | Status: {log['status']}")

        else:
            print(f"Неизвестная команда: {cmd}")


if __name__ == "__main__":
    run_shell()