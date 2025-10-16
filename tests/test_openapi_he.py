"""OpenAPI contract tests — all current stage endpoints must exist in the specification."""
from jobpulse_api.main import create_app
def test_openapi_contract_contains_paths():
    app = create_app()
    spec = app.openapi()
    paths = spec.get("paths", {})
    required = ["/health", "/readyz", "/jobs/", "/jobs/count", "/jobs/{job_id}"]
    for p in required:
        assert p in paths, f"Missing path in OpenAPI: {p}"






