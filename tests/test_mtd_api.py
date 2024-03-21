import pytest
import time

from src.mtd_api import Mtd_Api


@pytest.fixture
def mtd():
    return Mtd_Api()


def test_stop_json(mtd):
    assert len(mtd.stop_json) == 6


def test_stop_name_to_id_json(mtd):
    assert len(mtd.stop_name_to_id_json) > 1000


def test_set_favorite_stop(mtd):
    assert mtd.favorite_stop is None
    mtd.set_favorite_stop("Fourth and Chalmers")
    assert mtd.favorite_stop == "Fourth and Chalmers"


def test_set_favorite_stop_error(mtd):
    assert mtd.favorite_stop is None
    mtd.set_favorite_stop("Fourth and Chalmers")
    assert mtd.favorite_stop == "Fourth and Chalmers"
    with pytest.raises(ValueError):
        mtd.set_favorite_stop("dsafdkasjfs")
    assert mtd.favorite_stop == "Fourth and Chalmers"


def test_get_departures_by_favorite_stop(mtd):
    mtd.set_favorite_stop("Fourth and Chalmers")
    assert mtd.favorite_stop == "Fourth and Chalmers"
    bus_array = mtd.get_departures_by_stop(mtd.favorite_stop)
    api_hit_time = mtd.last_api_hit
    assert len(bus_array) > 0
    print(bus_array)
    assert len(mtd.cache) > 0

    assert mtd.last_api_hit > 0
    bus_array_cache = mtd.get_departures_by_stop(mtd.favorite_stop)
    assert len(mtd.cache) > 0
    assert len(bus_array_cache) > 0
    assert mtd.last_api_hit == api_hit_time


def test_get_departures_by_stop(mtd):
    bus_array = mtd.get_departures_by_stop("Fourth and Chalmers")
    api_hit_time = mtd.last_api_hit
    assert len(mtd.cache) > 0
    assert len(bus_array) > 0
    assert mtd.last_api_hit > 0
    bus_array_cache = mtd.get_departures_by_stop("Fourth and Chalmers")
    assert len(mtd.cache) > 0
    assert len(bus_array_cache) > 0
    assert mtd.last_api_hit == api_hit_time


# # Takes 1 minute to run
# def test_get_departures_by_stop_no_cache(mtd):
#     bus_array = mtd.get_departures_by_stop("Fourth and Chalmers")
#     api_hit_time = mtd.last_api_hit
#     assert len(mtd.cache) > 0
#     assert len(bus_array) > 0
#     assert mtd.last_api_hit > 0
#     time.sleep(60)
#     bus_array_cache = mtd.get_departures_by_stop("Fourth and Chalmers")
#     assert len(mtd.cache) > 0
#     assert len(bus_array_cache) > 0
#     assert mtd.last_api_hit > api_hit_time


def test_continuous_application_get_departures(mtd):
    assert mtd.favorite_stop is None
    assert mtd.last_api_hit == 0

    mtd.set_favorite_stop("Fourth and Chalmers")
    assert mtd.favorite_stop == "Fourth and Chalmers"
    with pytest.raises(ValueError):
        mtd.set_favorite_stop("dsafdkasjfs")
    assert mtd.favorite_stop == "Fourth and Chalmers"

    assert len(mtd.stop_name_to_id_json) > 1000
    assert len(mtd.stop_json) == 6

    chalmers_bus_array = mtd.get_departures_by_stop(mtd.favorite_stop)
    assert len(mtd.cache) > 0
    assert len(chalmers_bus_array) > 0
    assert mtd.last_api_hit > 0

    mtd.set_favorite_stop("Fourth and Gregory")
    assert mtd.favorite_stop == "Fourth and Gregory"
    gregory_bus_array = mtd.get_departures_by_stop(mtd.favorite_stop)
    assert len(mtd.cache) > 0
    assert len(gregory_bus_array) > 0
    assert chalmers_bus_array != gregory_bus_array
    assert mtd.last_api_hit > 0
