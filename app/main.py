import os, socket
import uvicorn
from fastapi import FastAPI

# Init App
app = FastAPI()

# Get Filepath from ENV
FILEPATH = os.environ.get("FILEPATH")

# Fake DB
fake_items_db = [
        {"item_name": "Foo"}, 
        {"item_name": "Bar"}, 
        {"item_name": "Baz"}
    ]

# Read File
@app.get("/text")
async def read_text():
    print(FILEPATH)
    with open(f"{FILEPATH}") as f:
        data = f.read()
        return data

# Get Items
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

# Get Hostname
@app.get("/")
async def hostname():
    if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount') or os.getenv('KUBERNETES_SERVICE_HOST') is not None:
        hostname = os.environ.get("HOSTNAME")
        return hostname            
    else:
        hostname = socket.gethostname()
        return hostname

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True, access_log=True)