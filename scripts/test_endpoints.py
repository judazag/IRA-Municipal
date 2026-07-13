import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from backend.app.main import app


def run():
    client = TestClient(app)
    r = client.get('/municipios')
    print('/municipios', r.status_code, r.json())
    r2 = client.get('/alertas')
    print('/alertas', r2.status_code, r2.json())


if __name__ == '__main__':
    run()
