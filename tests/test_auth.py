"""Unit tests for user registration, authentication, and Guest Mode."""
import pytest
from database.connection import init_db
from database.models import UserModel
from gui.main_window import MainWindow

@pytest.fixture(autouse=True)
def setup():
    init_db()
    from database.connection import get_db_connection
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE username IN ('alice', 'alice2') OR email IN ('alice@example.com', 'alice2@example.com')")
    conn.commit()
    conn.close()

def test_user_registration_and_authentication():
    # 1. Register new user
    res = UserModel.create_user("Alice Smith", "alice", "alice@example.com", "secret123")
    assert res["success"] is True
    assert res["username"] == "alice"

    # 2. Prevent duplicate username
    res_dup = UserModel.create_user("Alice Two", "alice", "alice2@example.com", "secret123")
    assert res_dup["success"] is False
    assert "already registered" in res_dup["error"]

    # 3. Authenticate with correct credentials
    auth_ok = UserModel.authenticate("alice", "secret123")
    assert auth_ok["success"] is True
    assert auth_ok["user"]["name"] == "Alice Smith"

    # 4. Authenticate with wrong password
    auth_fail = UserModel.authenticate("alice", "wrongpwd")
    assert auth_fail["success"] is False
    assert "Invalid password" in auth_fail["error"]

    # 5. Authenticate via email
    auth_email = UserModel.authenticate("alice@example.com", "secret123")
    assert auth_email["success"] is True

def test_gui_auth_and_guest_flow():
    app = MainWindow(start_authenticated=False)
    app.withdraw()

    # Initial state: AuthView is mounted
    assert app.auth_view is not None
    assert app.sidebar is None

    # Trigger Guest Login
    app.auth_view._handle_guest_login()
    app.update()

    # Main layout is now mounted
    assert app.auth_view is None
    assert app.sidebar is not None
    assert app.header is not None
    assert app.current_user["name"] == "Guest Student"
    assert app.current_user["is_guest"] is True

    # Test Logout back to Home Landing screen
    app.logout()
    app.update()

    assert app.auth_view is not None
    assert app.sidebar is None
    assert app.current_user is None

    app.destroy()
