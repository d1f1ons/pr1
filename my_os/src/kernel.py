from .db import init_db
from . import syscalls
import syscalls

class Kernel:
    """Ядро учебной операционной системы."""
    def __init__(self):
        init_db()
        self.current_user = "admin"

    def execute_syscall(self, name: str, *args):
        if name == "sys_echo":
            return syscalls.sys_echo(args[0] if args else "", self.current_user)
        elif name == "sys_get_users":
            return syscalls.sys_get_users(self.current_user)
        else:
            raise ValueError(f"Неизвестный системный вызов: {name}")