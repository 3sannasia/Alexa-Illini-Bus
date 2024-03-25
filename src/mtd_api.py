import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime, timezone
import inflect


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
        self.last_api_hit = 0
        self.favorite_stop = None

    def get_departures_by_stop(self, stop_name: str) -> list:
        if datetime.now(timezone.utc).timestamp() - self.last_api_hit < 60:
            return self.cache["getdeparturesbystop"][stop_name]
        param = {
            "stop_id": self.stop_name_to_id_json[stop_name],
            "pt": self.pt,
        }
        response = requests.get(
            self.base_url.format("getdeparturesbystop"), params=param
        )
        response_json = response.json()
        if response.status_code == 200:
            self.last_api_hit = datetime.now(timezone.utc).timestamp()
            bus_arrival_time_list = []
            for departure in response_json["departures"]:
                bus_arrival_time_list.append(
                    [departure["headsign"], departure["expected_mins"]]
                )
            self.cache.setdefault("getdeparturesbystop", {}).setdefault(stop_name, {})
            self.cache["getdeparturesbystop"][stop_name] = bus_arrival_time_list
            return bus_arrival_time_list

        else:
            return {}

    def get_mtd_autocomplete_stop_id(self, user_input) -> str:
        mtd_autocomplete_api_url = (
            f"https://search.mtd.org/v1.0.0/stop/suggest/{user_input}"
        )
        autocomplete_response = requests.get(mtd_autocomplete_api_url)
        if autocomplete_response.status_code != 200:
            return None
        bus_id = autocomplete_response.json()[0]["result"]["id"]
        return bus_id

    def set_favorite_stop(self, stop_name: str) -> None:
        if stop_name in self.stop_name_to_id_json.keys():
            self.favorite_stop = stop_name
            self.last_api_hit = 0
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

    def prettify_json(self, data: dict) -> json:
        return json.dumps(data, indent=4)

    def is_ordinal_string(self, s: str):
        if s.endswith("rd") or s.endswith("th") or s.endswith("st") or s.endswith("nd"):
            # Remove the suffix and check if the remaining part is a number
            number_part = s[:-2]
            if number_part.isdigit():
                return True
        return False

    def convert_ordinal(self, intent_request: str):
        split_response = intent_request.split(" ")
        for i in range(len(split_response)):
            if self.is_ordinal_string(split_response[i]):
                p = inflect.engine()
                split_response[i] = p.number_to_words(split_response[i])
        intent_request = " ".join(split_response)

        return intent_request


if __name__ == "__main__":
    mtd = Mtd_Api()
    # print(mtd.prettify_json(mtd.get_departures_by_stop("Fourth and Chalmers")))
    print(mtd.get_mtd_autocomplete_stop_id(mtd.convert_ordinal("4th and Chalmers")))
