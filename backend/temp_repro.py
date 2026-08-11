import os
import tempfile
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

os.environ['DATABASE_URL'] = 'sqlite:///' + str(Path(tempfile.gettempdir()) / f'test_doctor_{uuid.uuid4().hex}.db')

from app.main import app
from app.database.base import Base
from app.database.session import engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)
resp = client.post('/doctors/', json={'full_name':'Dr Test','specialty':'Cardiology','email':'dr@example.com','phone':'1'})
print(resp.status_code)
print(resp.text)
