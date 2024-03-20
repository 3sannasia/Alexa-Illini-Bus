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
        self.pt = 60
        self.base_url = "https://developer.mtd.org/api/{}/{}/{{}}?key={}".format(
            self.version, self.data_format, self.api
        )
        self.stop_json = json.load(open("mtd bus stop data/stops.json"))
        self.stop_name_to_id_json = json.load(
            open("mtd bus stop data/stop_name_to_id.json")
        )
        self.changeset_id = None
        self.cache = {}
        self.favorite_stop = None

    # Don't need, just for testing cache and api usage
    def get_routes_by_stop(self, stop_id: str) -> dict:
        request_method = "getroutesbystop"
        param = {"stop_id": stop_id, "changeset_id": self.changeset_id}
        response = requests.get(self.base_url.format(request_method), params=param)
        response_json = response.json()

        if response.status_code == 200:
            print("Insert to cache")

            self.changeset_id = response_json["changeset_id"]
            self.cache["getroutesbystop"] = response_json
            return response_json
        elif response.status_code == 202 or response.json()["new_changeset"] == False:
            # data not modified, check in cache and return existing data
            print("Return from cache")
            return self.cache["getroutesbystop"]

        else:
            return {}

    def get_departures_by_stop(self, stop_name: str) -> dict:
        param = {
            "stop_id": self.stop_name_to_id_json[stop_name],
            "changeset_id": self.changeset_id,
            "pt": self.pt,
        }
        response = requests.get(
            mtd.base_url.format("getdeparturesbystop"), params=param
        )
        response_json = response.json()
        if response.status_code == 200:
            self.changeset_id = response_json["changeset_id"][stop_name]
            # parse to format I want -> stop name to all buses and the times they arrive -> then put into cache

            return response_json
        elif response.status_code == 202 or response.json()["new_changeset"] == False:
            # data not modified, check in cache and return existing data
            return self.cache["getdeparturesbystop"]["stop_name"]

        else:
            return {}

    def set_favorite_stop(self, stop_name: str):
        if stop_name in self.stop_name_to_id_json.keys():
            self.favorite_stop = stop_name
        else:
            raise ValueError("Invalid stop name")

    def save_stops_json(self) -> None:
        response = requests.get(mtd.base_url.format("getstops"))
        response_json = response.json()
        with open("mtd bus stop data/stops.json", "w") as outfile:
            json.dump(response_json, outfile, indent=4)

    def save_name_to_id_json(self) -> None:
        stop_name_to_id_dict = {}
        for stop in self.stop_json["stops"]:
            stop_name_to_id_dict[stop["stop_name"]] = stop["stop_id"]
        with open("mtd bus stop data/stop_name_to_id.json", "w") as outfile:
            json.dump(stop_name_to_id_dict, outfile, indent=4)

    def pretty_print(self, data: dict):
        return json.dumps(data, indent=4)


if __name__ == "__main__":
    mtd = Mtd_Api()
    mtd.save_name_to_id_json()

    print(mtd.pretty_print(mtd.get_departures_by_stop("Fourth and Chalmers")))
    # print(mtd.pretty_print(mtd.get_routes_by_stop("IT:1")))
