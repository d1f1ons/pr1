from src.syscalls import sys_delete_file, sys_kill

def test_guest_cannot_delete_admin_file():
    result = sys_delete_file("/admin_file.txt", "guest", owner="admin")
    assert result is False, "guest не должен удалять файл admin"
    print("[PASS] TC-02: guest не может удалить файл admin")

def test_admin_can_delete_any_file():
    result = sys_delete_file("/user_file.txt", "admin", owner="user")
    assert result is True, "admin должен удалять любой файл"
    print("[PASS] admin может удалить файл user")

def test_guest_cannot_kill_process():
    result = sys_kill(1, "guest")
    assert result is False, "guest не должен убивать процессы"
    print("[PASS] guest не может убить процесс")

def test_admin_can_kill_process():
    result = sys_kill(1, "admin")
    assert result is True, "admin должен убивать процессы"
    print("[PASS] admin может убить процесс")

if __name__ == "__main__":
    test_guest_cannot_delete_admin_file()
    test_admin_can_delete_any_file()
    test_guest_cannot_kill_process()
    test_admin_can_kill_process()
    print("\nВсе тесты пройдены.")