from hypothesis import given, strategies as st
from backend.models import Location
from backend.forecasting.engine import generate_price_forecast


@given(crop=st.text(min_size=1), lat=st.floats(-90,90), lon=st.floats(-180,180), horizon=st.integers(min_value=1, max_value=60))
def test_generate_forecast(crop, lat, lon, horizon):
    loc = Location(latitude=lat, longitude=lon)
    fc = generate_price_forecast(crop, loc, horizon)
    assert fc.crop == crop
    assert len(fc.predictions) == horizon
    assert all(p.price >= 0 for p in fc.predictions)
    assert fc.confidenceLevel >= 0
