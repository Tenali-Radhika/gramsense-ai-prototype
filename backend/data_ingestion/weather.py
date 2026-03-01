from typing import List, Tuple
from ..models import Location


def fetch_weather_data(location: Location, date_range: Tuple[str, str]) -> List[dict]:
    """Retrieve weather data for a location between the given date range.

    This is a placeholder; real implementation would call IMD or another API.
    """
    return []
