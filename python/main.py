import datetime
import json
import random
import time
import threading
import pandas as pd
from websocket import create_connection, WebSocketConnectionClosedException

from Building import Building
from Weather import WeatherProvider
from Room import Room
from SimulationEngine import SimulationEngine
from Wall import ExternalWall, InternalWall

def websocket_receive_thread(ws, sim_parameters):
    while ws.connected:
        try:
            parameters = ws.recv()
            if parameters:
                handle_incoming_parameters(parameters, sim_parameters)
        except WebSocketConnectionClosedException:
            print("Connection closed.")
            break
        except Exception as e:
            print(f"Error: {e}.")

def handle_incoming_parameters(parameters_json, sim_parameters):
    try:
        new_params = json.loads(parameters_json)
        print(new_params)

        for key, value in new_params.items():
            if key in sim_parameters:
                sim_parameters[key] = value
    except json.JSONDecodeError:
        print(f"Invalid JSON: {parameters_json}.")
    except Exception as e:
        print(f"Error: {e}.")

def simulation_and_send_thread(ws, engine, weather_provider, sim_parameters):
    DT = 3600.0
    PROCESS_NOISE_STD_DEV = 0.05

    weather = weather_provider.get_current_weather(sim_parameters=sim_parameters)

    data_package = {
        "Type": "SimulationData",
        "Weather": {
            "Temp": weather.temp,
            "WindSpeed": weather.wind_speed,
            "WindDir": weather.wind_dir,
            "SunRadiation": weather.sun_radiation,
            "SunAltitude": weather.sun_altitude,
            "SunAzimuth": weather.sun_azimuth
        },
        "Temperatures": {r.name: round(r.temp * 100.0) / 100.0 for r in engine.building.rooms.values()},
        "SpeedFactor": sim_parameters["SpeedFactor"],
        "SimTimestamp": sim_parameters["SimTimestamp"].isoformat()
    }
    ws.send(json.dumps(data_package))
    print(data_package)

    time.sleep(DT / sim_parameters["SpeedFactor"])

    while ws.connected:
        try:
            sim_parameters["SimTimestamp"] += pd.Timedelta(seconds=DT)

            weather = weather_provider.get_current_weather(sim_parameters=sim_parameters)

            engine.run_simulation(dt=DT, steps=3600.0, weather=weather)

            for room in engine.building.rooms.values():
                noise = random.gauss(0, PROCESS_NOISE_STD_DEV)
                room.temp += noise

            data_package = {
                "Type": "SimulationData",
                "Weather": {
                    "Temp": weather.temp,
                    "WindSpeed": weather.wind_speed,
                    "WindDir": weather.wind_dir,
                    "SunRadiation": weather.sun_radiation,
                    "SunAltitude": weather.sun_altitude,
                    "SunAzimuth": weather.sun_azimuth
                },
                "Temperatures": {r.name: round(r.temp * 100.0) / 100.0 for r in engine.building.rooms.values()},
                "SpeedFactor": sim_parameters["SpeedFactor"],
                "SimTimestamp": sim_parameters["SimTimestamp"].isoformat()
            }
            ws.send(json.dumps(data_package))
            print(data_package)

            time.sleep(DT / sim_parameters["SpeedFactor"])
        except Exception as e:
            print(f"Error: {e}.")

if __name__ == "__main__":
    sim_parameters = {
        "SimTimestamp": pd.Timestamp("2024-01-01 00:00"),
        "SpeedFactor": 1000.0,
        "IsAuto": True,
        "Temp": 0.0,
        "WindSpeed": 0.0,
        "WindDir": 0.0,
        "SunRadiation": 0.0,
        "SunAltitude": 0.0,
        "SunAzimuth": 0.0
    }

    b = Building(ground_temp=10.0)

    r1 = Room(name="boiler", area=6.4, volume=16.0, air_heat_capacity_per_volume=1200.0, initial_temp=20.0)
    r2 = Room(name="garage", area=18.24, volume=45.6, air_heat_capacity_per_volume=1200.0, initial_temp=20.0)
    r3 = Room(name="bedroom1", area=11.1, volume=27.75, air_heat_capacity_per_volume=1200.0, initial_temp=20.0)
    r4 = Room(name="bedroom2", area=9.86, volume=24.65, air_heat_capacity_per_volume=1200.0, initial_temp=20.0)
    r5 = Room(name="bathroom", area=4.68, volume=11.7, air_heat_capacity_per_volume=1200.0, initial_temp=20.0)
    r6 = Room(name="living_room", area=37.34, volume=93.35, air_heat_capacity_per_volume=1200.0, initial_temp=20.0)

    b.add_room(r1)
    b.add_room(r2)
    b.add_room(r3)
    b.add_room(r4)
    b.add_room(r5)
    b.add_room(r6)

    w1 = ExternalWall(area=8.0, wall_mass_per_area=120000.0, u_value_internal=7.5, u_value_external=0.2, absorptance=0.5, room_a=r1, wall_dir=0)
    w2 = ExternalWall(area=9.25, wall_mass_per_area=120000.0, u_value_internal=7.5, u_value_external=0.2, absorptance=0.5, room_a=r3, wall_dir=0)
    w3 = ExternalWall(area=10.5, wall_mass_per_area=120000.0, u_value_internal=7.5, u_value_external=0.2, absorptance=0.5, room_a=r6, wall_dir=0)
    w4 = ExternalWall(area=19.75, wall_mass_per_area=120000.0, u_value_internal=7.5, u_value_external=0.2, absorptance=0.5, room_a=r6, wall_dir=90)
    w5 = ExternalWall(area=11.75, wall_mass_per_area=120000.0, u_value_internal=7.5, u_value_external=0.2, absorptance=0.5, room_a=r6, wall_dir=180)
    w6 = ExternalWall(area=8.25, wall_mass_per_area=120000.0, u_value_internal=7.5, u_value_external=0.2, absorptance=0.5, room_a=r4, wall_dir=180)
    w7 = ExternalWall(area=8.0, wall_mass_per_area=120000.0, u_value_internal=7.5, u_value_external=0.2, absorptance=0.5, room_a=r2, wall_dir=180)
    w8 = ExternalWall(area=14.25, wall_mass_per_area=120000.0, u_value_internal=7.5, u_value_external=0.2, absorptance=0.5, room_a=r2, wall_dir=270)
    w9 = ExternalWall(area=5.0, wall_mass_per_area=120000.0, u_value_internal=7.5, u_value_external=0.2, absorptance=0.5, room_a=r1, wall_dir=270)

    w10 = InternalWall(area=8.0, wall_mass_per_area=60000.0, u_value=0.5, room_a=r1, room_b=r2)
    w11 = InternalWall(area=5.0, wall_mass_per_area=90000.0, u_value=0.35, room_a=r1, room_b=r3)
    w12 = InternalWall(area=2.0, wall_mass_per_area=90000.0, u_value=0.35, room_a=r2, room_b=r3)
    w13 = InternalWall(area=4.5, wall_mass_per_area=90000.0, u_value=0.35, room_a=r2, room_b=r5)
    w14 = InternalWall(area=7.25, wall_mass_per_area=90000.0, u_value=0.35, room_a=r2, room_b=r4)
    w15 = InternalWall(area=7.5, wall_mass_per_area=60000.0, u_value=0.5, room_a=r3, room_b=r6)
    w16 = InternalWall(area=3.0, wall_mass_per_area=60000.0, u_value=0.5, room_a=r3, room_b=r6)
    w17 = InternalWall(area=6.5, wall_mass_per_area=60000.0, u_value=0.5, room_a=r3, room_b=r5)
    w18 = InternalWall(area=4.5, wall_mass_per_area=60000.0, u_value=0.5, room_a=r5, room_b=r6)
    w19 = InternalWall(area=6.5, wall_mass_per_area=60000.0, u_value=0.5, room_a=r5, room_b=r4)
    w20 = InternalWall(area=1.75, wall_mass_per_area=60000.0, u_value=0.5, room_a=r4, room_b=r6)
    w21 = InternalWall(area=7.25, wall_mass_per_area=60000.0, u_value=0.5, room_a=r4, room_b=r6)

    w1.add_window(area=0.9, u_value=0.75, g_value=0.5)
    w2.add_window(area=1.5, u_value=0.75, g_value=0.5)
    w3.add_window(area=3.6, u_value=0.75, g_value=0.5)
    w4.add_window(area=3.2, u_value=0.75, g_value=0.5)
    w5.add_window(area=1.2, u_value=0.75, g_value=0.5)
    w6.add_window(area=1.5, u_value=0.75, g_value=0.5)
    w8.add_window(area=0.9, u_value=0.75, g_value=0.5)

    b.add_wall(w1)
    b.add_wall(w2)
    b.add_wall(w3)
    b.add_wall(w4)
    b.add_wall(w5)
    b.add_wall(w6)
    b.add_wall(w7)
    b.add_wall(w8)
    b.add_wall(w9)
    b.add_wall(w10)
    b.add_wall(w11)
    b.add_wall(w12)
    b.add_wall(w13)
    b.add_wall(w14)
    b.add_wall(w15)
    b.add_wall(w16)
    b.add_wall(w17)
    b.add_wall(w18)
    b.add_wall(w19)
    b.add_wall(w20)
    b.add_wall(w21)

    weather_provider = WeatherProvider("weather_history.csv")
    engine = SimulationEngine(b)

    WS_SERVER_URL = "wss://localhost:6101/ws"

    try:
        ws = create_connection(WS_SERVER_URL)
        print("Connected.")

        receive_thread = threading.Thread(target=websocket_receive_thread, args=(ws, sim_parameters))
        receive_thread.start()

        send_thread = threading.Thread(target=simulation_and_send_thread, args=(ws, engine, weather_provider, sim_parameters))
        send_thread.start()

        send_thread.join()
        receive_thread.join()
    except Exception as e:
        print(f"Error: {e}.")
