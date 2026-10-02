"""Планировщик процессов."""

from src import db
from src.kernel import kernel_instance


def create_process(name: str, owner: str, memory_size: int = 100) -> int:
    """Создает новый процесс и записывает его в БД."""
    # 1. Проверяем/выделяем память в ядре
    if not kernel_instance.allocate_memory(memory_size):
        return -1

    # 2. Вставляем запись без явного указания pid (SQLite сам сгенерирует AUTOINCREMENT pid)
    pid = db.execute_insert('processes', {
        'name': name,
        'state': 'ready',
        'owner': owner,
        'memory_used': memory_size
    })

    return pid


def list_processes() -> list:
    """Возвращает список всех процессов."""
    return db.execute_select('processes')


def get_process(pid: int):
    """Возвращает процесс по pid или None."""
    processes = db.execute_select('processes', {'pid': pid})
    if not processes:
        return None
    return processes[0]


def terminate_process(pid: int) -> bool:
    """Завершает процесс. Освобождает память. Возвращает True или False."""
    process = get_process(pid)
    if not process:
        return False
    kernel_instance.free_memory(process['memory_used'])
    db.execute_delete('processes', {'pid': pid})
    return True


def schedule_round_robin():
    """Выбирает следующий процесс по алгоритму Round Robin."""
    processes = db.execute_select('processes')
    if not processes:
        return None
    for p in processes:
        db.execute_update('processes', {'state': 'ready'}, {'pid': p['pid']})
    first = processes[0]
    db.execute_update('processes', {'state': 'running'}, {'pid': first['pid']})
    return get_process(first['pid'])


def process_count() -> int:
    """Возвращает количество процессов."""
    return len(list_processes())