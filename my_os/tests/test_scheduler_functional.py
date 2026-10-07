"""Функциональные тесты планировщика."""
from src import scheduler, db
from src.kernel import kernel_instance

def setup():
    """Очищаем процессы и сбрасываем память."""
    all_procs = db.execute_select('processes')
    for p in all_procs:
        kernel_instance.free_memory(p['memory_used'])
        db.execute_delete('processes', {'pid': p['pid']})

def test_create_process():
    pid = scheduler.create_process('ft_app', 'admin', 10)
    assert pid > 0
    print(f"[PASS] FT-10: создание процесса PID={pid}")

def test_memory_overflow():
    pid = scheduler.create_process('huge', 'admin', 5000)
    assert pid == -1
    print("[PASS] FT-11: переполнение памяти отклонено")

def test_list_processes():
    scheduler.create_process('list1', 'admin', 5)
    scheduler.create_process('list2', 'admin', 5)
    procs = scheduler.list_processes()
    assert len(procs) >= 2
    print("[PASS] FT-12: список процессов")

def test_get_process():
    pid = scheduler.create_process('get_app', 'admin', 5)
    p = scheduler.get_process(pid)
    assert p is not None
    assert p['name'] == 'get_app'
    print("[PASS] FT-13: поиск процесса по PID")

def test_get_missing():
    assert scheduler.get_process(99999) is None
    print("[PASS] FT-14: несуществующий PID возвращает None")

def test_terminate_frees_memory():
    pid = scheduler.create_process('term_app', 'admin', 50)
    used_before = kernel_instance.memory_used
    assert scheduler.terminate_process(pid) is True
    assert kernel_instance.memory_used == used_before - 50
    print("[PASS] FT-15: завершение процесса освобождает память")

def test_terminate_missing():
    assert scheduler.terminate_process(99999) is False
    print("[PASS] FT-16: завершение несуществующего процесса")

def test_round_robin():
    scheduler.create_process('rr1', 'admin', 5)
    scheduler.create_process('rr2', 'admin', 5)
    running = scheduler.schedule_round_robin()
    assert running is not None
    assert running['state'] == 'running'
    print("[PASS] FT-17: Round Robin выбирает процесс")

def test_process_count():
    before = scheduler.process_count()
    scheduler.create_process('count_app', 'admin', 5)
    after = scheduler.process_count()
    assert after == before + 1
    print("[PASS] FT-18: подсчёт процессов")

if __name__ == "__main__":
    setup()
    test_create_process()
    test_memory_overflow()
    test_list_processes()
    test_get_process()
    test_get_missing()
    test_terminate_frees_memory()
    test_terminate_missing()
    test_round_robin()
    test_process_count()
    print("\nВсе функциональные тесты планировщика пройдены.")