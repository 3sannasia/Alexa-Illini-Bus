import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

mtd_api = os.getenv("MTD_API_KEY")
version = "v2.2"
data_format = "JSON"
key_url = f"key={mtd_api}"
method = "getroutesbystop"
base_url = f"https://developer.mtd.org/api/{version}/{data_format}/{method}?{key_url}"
print(base_url)

param = {
    "stop_id": "it:1",
    "changeset_id": "0"
}

response = requests.get(base_url, params = param)
response_json = response.json()
changeset_id = response_json["changeset_id"]
param["changeset_id"] = changeset_id

print(response.status_code)
print(json.dumps(response_json, indent=4))
