import sys, traceback
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
print('client ready')
try:
    response = client.post('/auth/login', data={'username': 'test@example.com', 'password': 'test'})
    print('status', response.status_code)
    print('body', response.text)
except Exception:
    traceback.print_exc()
