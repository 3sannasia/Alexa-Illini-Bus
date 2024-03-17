import os
from dotenv import load_dotenv

load_dotenv()

mtd_api = os.getenv("MTD_API_KEY")
version = "v2.2"
data_format = "JSON"
base_url = f"https://developer.mtd.org/api/{version}/{data_format}"
print(base_url)

