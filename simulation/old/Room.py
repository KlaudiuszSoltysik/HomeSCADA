import math

class Room:
    def __init__(self, name, area, volume, air_heat_capacity_per_volume, initial_temp):
        self.name = name
        self.area = area
        self.volume = volume
        self.air_heat_capacity_per_volume = air_heat_capacity_per_volume
        self.temp = initial_temp

        self.setpoint_temp = 20.0
        self.hysteresis = 2.0

        self.internal_heat = 0.0

        self.floor = self.Floor(area=area, heat_capacity_per_area=150000.0, u_value_air=3.0, u_value_ground=0.3, initial_temp=initial_temp)
        self.roof = self.Roof(area=area, mass_per_area=150000.0, u_value_internal=7.5, u_value_external=0.2, absorptance=0.7, initial_temp=initial_temp)

    @property
    def heat_capacity(self):
        return self.air_heat_capacity_per_volume * self.volume

    def set_temp_controls(self, setpoint_temp, hysteresis):
        self.setpoint_temp = setpoint_temp
        self.hysteresis = hysteresis

    class Floor:
        def __init__(self, area, heat_capacity_per_area, u_value_air, u_value_ground, initial_temp):
            self.area = area
            self.heat_capacity_per_area = heat_capacity_per_area
            self.u_value_air = u_value_air
            self.u_value_ground = u_value_ground
            self.temp = initial_temp

        @property
        def heat_capacity(self):
            return self.heat_capacity_per_area * self.area

        def calculate_flow(self, dt, room_temp, ground_temp):
            q_air_to_floor = self.u_value_air * self.area * (room_temp - self.temp)
            q_floor_to_ground = self.u_value_ground * self.area * (self.temp - ground_temp)

            dE_floor = (q_air_to_floor - q_floor_to_ground) * dt

            self.temp += dE_floor / self.heat_capacity

            dE_to_room_air = -q_air_to_floor * dt

            return dE_to_room_air

    class Roof:
        WIND_CHILL_FACTOR = 0.5
        EXTERNAL_SURFACE_FACTOR = 25.0

        def __init__(self, area, mass_per_area, u_value_internal, u_value_external, absorptance, initial_temp):
            self.area = area
            self.mass_per_area = mass_per_area
            self.u_value_internal = u_value_internal
            self.u_value_external = u_value_external
            self.absorptance = absorptance
            self.temp = initial_temp

        @property
        def heat_capacity(self):
            return self.mass_per_area * self.area

        def calculate_flow(self, dt, room_temp, external_temp, wind_speed, sun_radiation, sun_altitude):
            wind_chill_effect = wind_speed * self.WIND_CHILL_FACTOR
            effective_external_temp = external_temp - wind_chill_effect

            radiation_on_surface = self.calculate_solar_on_flat_surface(sun_radiation, sun_altitude)

            absorbed_solar_radiation = self.absorptance * radiation_on_surface
            sol_air_temp = effective_external_temp + (absorbed_solar_radiation / self.EXTERNAL_SURFACE_FACTOR)

            q_room_to_roof = self.u_value_internal * self.area * (room_temp - self.temp)
            q_roof_to_outside = self.u_value_external * self.area * (self.temp - sol_air_temp)

            dE_roof = (q_room_to_roof - q_roof_to_outside) * dt

            self.temp += dE_roof / self.heat_capacity

            dE_to_room_air = -q_room_to_roof * dt

            return dE_to_room_air

        def calculate_solar_on_flat_surface(self, sun_radiation, sun_altitude):
            if sun_altitude <= 0.0:
                return 0.0

            radiation = sun_radiation * math.sin(math.radians(sun_altitude))

            return max(0.0, radiation)