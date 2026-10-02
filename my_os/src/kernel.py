"""Модуль управления состоянием ядра."""

from src.db import init_db, execute_select, execute_delete, execute_insert
from src import syscalls


class Kernel:
    """Ядро учебной операционной системы."""

    def __init__(self):
        init_db()
        self.current_user = "admin"
        self.process_counter = 0
        self.memory_used = 0
        self.memory_limit = 1024
        self.load_memory_state()

    def set_user(self, login: str):
        """Устанавливает текущего пользователя."""
        self.current_user = login

    def get_user(self) -> str:
        """Возвращает текущего пользователя."""
        return self.current_user

    def allocate_pid(self) -> int:
        """Выдает следующий PID процесса."""
        self.process_counter += 1
        return self.process_counter

    def allocate_memory(self, size: int) -> bool:
        """Выделяет память, возвращает True, если успешно."""
        if self.memory_used + size > self.memory_limit:
            return False
        self.memory_used += size
        self.save_memory_state()
        return True

    def free_memory(self, size: int):
        """Освобождает память."""
        self.memory_used = max(0, self.memory_used - size)
        self.save_memory_state()

    def save_memory_state(self):
        """Сохраняет состояние памяти в БД."""
        execute_delete('memory_state', {})
        execute_insert('memory_state', {
            'used': self.memory_used,
            'limit_val': self.memory_limit
        })

    def load_memory_state(self):
        """Загружает состояние памяти из БД."""
        states = execute_select('memory_state')
        if states:
            self.memory_used = states[0]['used']
            self.memory_limit = states[0]['limit_val']

    def memory_info(self) -> dict:
        """Возвращает информацию о памяти."""
        return {
            "used": self.memory_used,
            "limit": self.memory_limit,
            "free": self.memory_limit - self.memory_used,
        }

    def execute_syscall(self, name: str, *args):
        """Диспетчер системных вызовов."""
        if name == "sys_echo":
            return syscalls.sys_echo(args[0] if args else "", self.current_user)
        elif name == "sys_get_users":
            return syscalls.sys_get_users(self.current_user)
        elif name == "sys_register":
            return syscalls.sys_register(args[0], args[1], args[2] if len(args) > 2 else "user", self.current_user)
        elif name == "sys_login":
            return syscalls.sys_login(args[0], args[1], self.current_user)
        elif name == "sys_whoami":
            return syscalls.sys_whoami(self.current_user)
        elif name == "sys_logs":
            limit = args[0] if args else 10
            return syscalls.sys_logs(limit, self.current_user)
        else:
            raise ValueError(f"Неизвестный системный вызов: {name}")


kernel_instance = Kernel()