from hypothesis import given, strategies as st
from backend.models import Location
from backend.data_ingestion.mandi import fetch_mandi_prices
from backend.data_ingestion.weather import fetch_weather_data
from backend.data_ingestion.crop_calendar import fetch_crop_calendar


@given(crop=st.text(min_size=1), lat=st.floats(-90, 90), lon=st.floats(-180, 180))
def test_fetch_prices(crop, lat, lon):
    loc = Location(latitude=lat, longitude=lon)
    prices = fetch_mandi_prices(crop, loc)
    assert isinstance(prices, list)
    for p in prices:
        assert p.crop == crop


def test_fetch_weather():
    loc = Location(latitude=0, longitude=0)
    data = fetch_weather_data(loc, ("2020-01-01", "2020-01-10"))
    assert isinstance(data, list)


def test_fetch_calendar():
    cal = fetch_crop_calendar("wheat", "region")
    assert isinstance(cal, dict)
