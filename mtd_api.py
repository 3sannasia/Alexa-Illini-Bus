import os
from dotenv import load_dotenv
import requests

load_dotenv()

mtd_api = os.getenv("MTD_API_KEY")
version = "v2.2"
data_format = "JSON"
key_url = f"key={mtd_api}"
method = "getroutesbystop"
base_url = f"https://developer.mtd.org/api/{version}/{data_format}/{method}?{key_url}"
print(base_url)
param = {
    "stop_id": "it:1"
}

response = requests.get(base_url, params = param)
print(response.status_code)
print(response.json())
