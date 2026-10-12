"""Стресс-тесты системы."""
from src import db
from src.kernel import kernel_instance
from src.syscalls import sys_exec, sys_kill, sys_create_file, sys_delete_file, sys_login
from src.auth import register_user

def setup():
    db.execute_delete('users', {'login': 'stress_admin'})
    register_user('stress_admin', 'stress123', 'admin')
    procs = db.execute_select('processes')
    for p in procs:
        kernel_instance.free_memory(p['memory_used'])
        db.execute_delete('processes', {'pid': p['pid']})

def test_many_processes():
    """Создать 10 процессов и проверить, что система выдерживает."""
    sys_login('stress_admin', 'stress123')
    pids = []
    for i in range(10):
        pid = sys_exec(f'stress_{i}', 'stress_admin')
        assert pid > 0, f"Процесс {i} не создан"
        pids.append(pid)
    print(f" [PASS] создано 10 процессов: {pids}")
    procs = db.execute_select('processes')
    assert len(procs) == 10
    print("[PASS] в таблице 10 процессов")
    for pid in pids:
        sys_kill(pid, 'stress_admin')
    procs_after = db.execute_select('processes')