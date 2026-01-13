from datetime import timedelta

import pandas as pd

from DistrictModelParser import DistrictModelParser
from ThermalSolver import ThermalSolver
from WeatherService import WeatherService
from WeatherSolver import WeatherSolver


class DistrictSimulation:
    def __init__(self, config_path, weather_path):
        parser = DistrictModelParser(config_path)
        metadata = parser.raw_data["metadata"]
        G, G_ext_air, G_ext_ground, C, N, external_connections, standards, nodes = parser.parse()

        self.thermal_solver = ThermalSolver(
            G=G,
            C=C,
            G_ext_air=G_ext_air,
            G_ext_ground=G_ext_ground,
            T_ground=metadata["ground_temperature"]
        )

        self.weather_solver = WeatherSolver(external_connections, standards, N)

        self.current_time = pd.Timestamp("2024-01-01 00:00:00").tz_localize(metadata["timezone"])
        self.weather_service = WeatherService(weather_path, metadata["timezone"], metadata["latitude"],
                                              metadata["longitude"])

        self.index_to_id = {v: k for k, v in nodes.items()}

    def run_step(self, dt_seconds):
        weather = self.weather_service.get_weather(self.current_time)

        q_env = self.weather_solver.calculate_environmental_gains(
            weather["sun_radiation"], weather["sun_altitude"], weather["sun_azimuth"],
            weather["wind_speed"], weather["wind_direction"], weather["temperature"], self.thermal_solver.T
        )

        temps_array = self.thermal_solver.step(dt_seconds, weather["temperature"], q_env)

        room_temps = {
            self.index_to_id[i]: float(temps_array[i])
            for i in range(len(temps_array))
        }

        output_timestamp = self.current_time.isoformat()
        self.current_time += timedelta(seconds=dt_seconds)

        return {
            "timestamp": output_timestamp,
            "weather": weather,
            "room_temps": room_temps
        }
