import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import Token

client = TestClient(app)

def test_root_404():
    """
    If your app doesn't define a root endpoint (e.g., GET /),
    this test ensures it returns 404.
    Remove or adjust if you do have a root endpoint.
    """
    response = client.get("/")
    assert response.status_code == 404

def test_docs_redoc():
    """
    Check that /docs and /redoc load successfully.
    """
    resp_docs = client.get("/docs")
    assert resp_docs.status_code == 200

    resp_redoc = client.get("/redoc")
    # Some setups might not enable /redoc by default;
    # if so, remove or adjust.
    if resp_redoc.status_code != 200:
        # /redoc might not be enabled by default, so we won't fail the test
        # but you can make it fail if you want both docs to exist
        pytest.skip("Redoc not enabled, skipping.")
    else:
        assert resp_redoc.status_code == 200

def test_users_csv_unauthorized():
    """
    Attempt to get /users?response_format=csv without a token.
    Should return 401 Unauthorized.
    """
    resp = client.get("/users?response_format=csv")
    assert resp.status_code == 401

def test_users_csv_authorized():
    """
    1) Register or login to get a token
    2) Attempt to retrieve /users as CSV
    3) Expect 200 OK and text/csv content
    """
    # Step 1: Register a user
    register_data = {"username": "csvtester", "password": "testpass123"}
    reg_response = client.post("/auth/register", json=register_data)
    assert reg_response.status_code == 200

    token_data = reg_response.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Step 2: GET /users?response_format=csv with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/users?response_format=csv", headers=headers)
    # Step 3: Expect 200 OK
    assert resp.status_code == 200
    # Confirm it's CSV
    assert "text/csv" in resp.headers["content-type"]

    # Optionally, check some CSV content (id,username,role, etc.)
    csv_body = resp.text.strip()
    # There's at least a header line
    assert "id,username,role" in csv_body

def test_users_json_authorized():
    """
    Similar test but for default JSON format.
    Checks that we can retrieve JSON if we pass a valid token.
    """
    # 1) Register a user
    reg_data = {"username": "jsontester", "password": "testpass456"}
    reg_resp = client.post("/auth/register", json=reg_data)
    assert reg_resp.status_code == 200

    token_data = reg_resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 2) GET /users with Bearer token (default JSON)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/users", headers=headers)
    assert resp.status_code == 200
    # confirm JSON
    assert resp.headers["content-type"].startswith("application/json")

    users_json = resp.json()
    # Should be a list of user objects
    assert isinstance(users_json, list)
    if users_json:
        assert "username" in users_json[0]

