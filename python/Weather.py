import datetime
import pandas as pd

class WeatherProvider:
    def __init__(self, history_file_path):
        try:
            self.weather_df = pd.read_csv(history_file_path)
            self.weather_df["timestamp"] = self.weather_df["timestamp"].apply(lambda x: datetime.datetime.strptime(str(x), "%Y-%m-%d %H:%M:%S%z"))
            self.weather_df = self.weather_df.set_index("timestamp")
            print("WeatherProvider: Weather history loaded.")
        except Exception as e:
            print(f"WeatherProvider: {e}")
            self.weather_df = pd.DataFrame()

    def _get_weather_from_df(self, timestamp):
        try:
            localized_ts = timestamp.tz_localize("Europe/Warsaw")

            if localized_ts in self.weather_df.index:
                row = self.weather_df.loc[localized_ts]
                return Weather(
                    temp=row["temp"],
                    wind_speed=row["wind_speed"],
                    wind_dir=row["wind_dir"],
                    sun_radiation=row["sun_radiation"],
                    sun_altitude=row["sun_altitude"],
                    sun_azimuth=row["sun_azimuth"],
                )
            else:
                print(f"WeatherProvider: No weather data for {localized_ts}")
                return None
        except Exception as e:
            print(f"WeatherProvider: {e}")
            return None

    def get_current_weather(self, sim_parameters):
        weather = None
        if sim_parameters["IsAuto"] and not self.weather_df.empty:
            weather = self._get_weather_from_df(timestamp=sim_parameters["SimTimestamp"].round("H"))

        if weather is None:
            weather = Weather(
                temp=sim_parameters["Temp"],
                wind_speed=sim_parameters["WindSpeed"],
                wind_dir=sim_parameters["WindDir"],
                sun_radiation=sim_parameters["SunRadiation"],
                sun_altitude=sim_parameters["SunAltitude"],
                sun_azimuth=sim_parameters["SunAzimuth"]
            )

        return weather

    def get_forecast(self, sim_parameters, horizon_hours):
        forecast_list = []
        current_timestamp = sim_parameters["SimTimestamp"]

        for i in range(horizon_hours):
            future_timestamp = current_timestamp + pd.Timedelta(hours=i)
            forecast_list.append(self._get_weather_from_df(timestamp=future_timestamp))

        return forecast_list

class Weather:
    def __init__(self, temp=0.0, wind_speed=0.0, wind_dir=0.0, sun_radiation=0.0, sun_altitude=0.0, sun_azimuth=0.0):
        self.temp = temp
        self.wind_speed = wind_speed
        self.wind_dir = wind_dir
        self.sun_radiation = sun_radiation
        self.sun_altitude = sun_altitude
        self.sun_azimuth = sun_azimuth
