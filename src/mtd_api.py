import os
from dotenv import load_dotenv
import requests
import json


class Mtd_Api:
    def __init__(self):
        load_dotenv()
        self.api = os.getenv("MTD_API_KEY")
        self.data_format = "JSON"
        self.version = "v2.2"
        self.base_url = "https://developer.mtd.org/api/{}/{}/{{}}?key={}".format(
            self.version, self.data_format, self.api
        )
        self.changeset_id = None
        self.cache = {}

    def get_routes_by_stop(self, stop_id: str) -> dict:
        request_method = "getroutesbystop"
        param = {"stop_id": stop_id, "changeset_id": self.changeset_id}
        response = requests.get(self.base_url.format(request_method), params=param)
        response_json = response.json()
        if response.status_code == 202 or response.json()["new_changeset"] == False:
            # data not modified check in cache and return
            print("Return from cache")
            return self.cache["getroutesbystop"]

        elif response.status_code == 200:
            print("Insert to cache")

            self.changeset_id = response_json["changeset_id"]
            self.cache["getroutesbystop"] = response_json
            return response_json
        else:
            return {}

    def save_stops_json(self) -> None:
        response = requests.get(mtd.base_url.format("getstops"))
        response_json = response.json()
        with open("stops.json", "w") as outfile:
            json.dump(response_json, outfile, indent=4)

    def save_name_to_id_json(self) -> None:
        stops_json = json.load(open("stops.json"))
        stop_name_to_id_dict = {}
        for stop in stops_json["stops"]:
            stop_name_to_id_dict[stop["stop_name"]] = stop["stop_id"]
        with open("stop_name_to_id.json", "w") as outfile:
            json.dump(stop_name_to_id_dict, outfile, indent=4)

    def pretty_print(self, data: dict):
        return json.dumps(data, indent=4)


if __name__ == "__main__":
    mtd = Mtd_Api()
    mtd.save_name_to_id_json()

    # print(mtd.pretty_print(mtd.get_routes_by_stop("IT:1")))
    # print(mtd.pretty_print(mtd.get_routes_by_stop("IT:1")))
