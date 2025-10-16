from fastapi.testclient import TestClient
from jobpulse_api.main import create_app
def test_health_and_readiness_basic():
    """Verify that the service is alive and ready (Lifespan initialized)."""
    client = TestClient(create_app())
    assert client.get("/health").status_code == 200, "Health endpoint should return 200"
    assert client.get("/health").json() == {"status": "ok"}, "Health response mismatch"
    assert client.get("/readyz").status_code == 200, "Readiness should return 200"
    assert client.get("/readyz").json() == {"ready": True}, "Readiness response mismatch"

