import json
from fastapi import Request
from typing import List

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    allow_credentials=True,  # Allow including cookies
    expose_headers=["Content-Disposition"],  # Expose specific headers if needed
)

@app.post("/save_data")
async def save_data(request: Request, data: List[str]):
    # Extract the data from the request body
    data_list = await request.json()

    # Convert the list to JSON
    json_data = json.dumps(data_list)

    # Write the JSON data to a text file
    with open("data.txt", "w") as file:
        file.write(json_data)

    return {"message": "Data saved successfully."}

@app.get("/get_data")
def get_data():
    # Read the data from the text file
    with open("data.txt", "r") as file:
        data = file.read()

    return {"data": data}

if __name__ == "__main__":
    uvicorn.run("main:app", host="192.168.0.2", port=8000)