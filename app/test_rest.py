from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_read_item_001():
    response = client.get("/items/")
    assert response.status_code == 200
    assert response.json() == [
            {"item_name": "Foo"}, 
            {"item_name": "Bar"}, 
            {"item_name": "Baz"}
    ]

def test_read_item_002():
    response = client.get("/items/?skip=0&limit=3")
    assert response.status_code == 200
    assert response.json() == [
            {"item_name": "Foo"}, 
            {"item_name": "Bar"}, 
            {"item_name": "Baz"}
    ]
    
def test_read_item_003():
    response = client.get("/foo")
    assert response.status_code == 404