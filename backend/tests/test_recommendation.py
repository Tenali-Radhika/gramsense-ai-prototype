from hypothesis import given, strategies as st
from backend.models import Location
from backend.recommendation.engine import (
    generate_selling_recommendation,
    suggest_optimal_markets,
    provide_crop_planning_advice,
)


@given(crop=st.text(min_size=1), lat=st.floats(-90, 90), lon=st.floats(-180, 180), quantity=st.floats(min_value=0))
def test_recommendation(crop, lat, lon, quantity):
    loc = Location(latitude=lat, longitude=lon)
    rec = generate_selling_recommendation(crop, loc, quantity)
    assert rec.type in {"SELL_NOW", "WAIT", "CHANGE_MARKET", "PLAN_CROP", "MONITOR"}
    assert 0.0 <= rec.confidence <= 1.0


@given(crop=st.text(min_size=1), lat=st.floats(-90, 90), lon=st.floats(-180, 180))
def test_optimal_markets(crop, lat, lon):
    loc = Location(latitude=lat, longitude=lon)
    markets = suggest_optimal_markets(crop, loc)
    assert isinstance(markets, list)


@given(lat=st.floats(-90, 90), lon=st.floats(-180, 180), season=st.text(min_size=1))
def test_crop_planning(lat, lon, season):
    loc = Location(latitude=lat, longitude=lon)
    advice = provide_crop_planning_advice(loc, season)
    assert isinstance(advice, list)
