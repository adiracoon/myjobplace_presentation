from fastapi.testclient import TestClient
from jobpulse_api.main import create_app
def test_health_ready():
    client = TestClient(create_app())
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/readyz").json() == {"ready": True}
