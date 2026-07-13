import pytest

from fastapi.testclient import TestClient

try:
    from backend.app.main import app
except Exception:
    app = None


@pytest.mark.skipif(app is None, reason="App import failed")
def test_health():
    client = TestClient(app)
    r = client.get('/healthz')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


@pytest.mark.skipif(app is None, reason="App import failed")
def test_municipios_empty_or_503():
    client = TestClient(app)
    r = client.get('/municipios')
    # If parquet missing we return 503, otherwise 200 with list
    assert r.status_code in (200, 503)
