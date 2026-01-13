import pandas as pd
from pvlib.solarposition import get_solarposition

def add_altitude_and_azimuth(filename, lat, lon):
    TIMEZONE = "Europe/Warsaw"

    try:
        df = pd.read_csv(filename)

        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        times = pd.DatetimeIndex(df["timestamp"])

        solpos = get_solarposition(time=times, latitude=lat, longitude=lon)

        df["sun_altitude"] = 90 - solpos["apparent_zenith"].values
        df["sun_azimuth"] = solpos["azimuth"].values

        df["timestamp"] = df["timestamp"].dt.tz_convert(TIMEZONE).dt.strftime("%Y-%m-%d %H:%M:%S%z")

        df.to_csv(filename, index=False)
    except Exception as e:
        print(f"Error: {e}")


add_altitude_and_azimuth("../weather_history.csv", 52.39, 16.95)