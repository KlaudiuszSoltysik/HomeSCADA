import math

class BaseWall:
    def __init__(self, area, wall_mass_per_area, room_a):
        self.area = area
        self.wall_mass_per_area = wall_mass_per_area
        self.room_a = room_a
        self.temp = room_a.temp

    @property
    def heat_capacity(self):
        return self.wall_mass_per_area * self.area

    def calculate_flow(self, dt, external_temp, wind_speed, wind_dir, sun_radiation, sun_altitude, sun_azimuth):
        raise NotImplementedError("Need to bo overrided.")

class InternalWall(BaseWall):
    def __init__(self, area, wall_mass_per_area, u_value, room_a, room_b):
        super().__init__(area, wall_mass_per_area, room_a)

        self.u_value = u_value
        self.room_b = room_b

        self.temp = (room_a.temp + room_b.temp) / 2.0

    def calculate_flow(self, dt, external_temp, wind_speed, wind_dir, sun_radiation, sun_altitude, sun_azimuth):
        u_half_wall = self.u_value * 2.0

        q_a_to_wall = u_half_wall * self.area * (self.room_a.temp - self.temp)
        q_wall_to_b = u_half_wall * self.area * (self.temp - self.room_b.temp)

        dE_wall = (q_a_to_wall - q_wall_to_b) * dt

        self.temp += dE_wall / self.heat_capacity

        dE_to_room_a = - q_a_to_wall * dt
        dE_to_room_b = q_wall_to_b * dt

        return {
            self.room_a: dE_to_room_a,
            self.room_b: dE_to_room_b
        }

class ExternalWall(BaseWall):
    WINDOW_MASS_PER_AREA = 0.0
    WIND_CHILL_FACTOR = 0.5
    EXTERNAL_SURFACE_FACTOR = 25.0

    def __init__(self, area, wall_mass_per_area, u_value_internal, u_value_external, absorptance, room_a, wall_dir):
        super().__init__(area, wall_mass_per_area, room_a)

        self.u_value_internal = u_value_internal
        self.u_value_external = u_value_external
        self.absorptance = absorptance
        self.wall_dir = wall_dir

        self.windows = []

    def add_window(self, area, u_value, g_value):
        window = self.Window(area, u_value, g_value)
        self.windows.append(window)

    @property
    def window_area(self):
        return sum(o.area for o in self.windows)

    @property
    def solid_area(self):
        return self.area - self.window_area

    @property
    def effective_mass_per_area(self):
        return (self.solid_area * self.wall_mass_per_area + self.window_area * self.WINDOW_MASS_PER_AREA) / self.area

    @property
    def heat_capacity(self):
        return self.effective_mass_per_area * self.area

    def calculate_flow(self, dt, external_temp, wind_speed, wind_dir, sun_radiation, sun_altitude, sun_azimuth):
        wind_angle_factor = max(0.0, math.cos(math.radians(wind_dir - self.wall_dir)))
        wind_chill_effect = wind_speed * wind_angle_factor * 0.5
        effective_external_temp = external_temp - wind_chill_effect

        radiation_on_wall_surface = self.calculate_solar_on_surface(sun_radiation, sun_altitude, sun_azimuth, self.wall_dir)
        absorbed_solar_radiation = self.absorptance * radiation_on_wall_surface

        sol_air_temp = effective_external_temp + (absorbed_solar_radiation / self.EXTERNAL_SURFACE_FACTOR)

        q_room_to_wall = self.u_value_internal * self.solid_area * (self.room_a.temp - self.temp)
        q_wall_to_outside = self.u_value_external * self.solid_area * (self.temp - sol_air_temp)

        dE_wall = (q_room_to_wall - q_wall_to_outside) * dt

        self.temp += dE_wall / self.heat_capacity

        dE_solid_to_room = -q_room_to_wall * dt

        dE_windows_loss_to_room = 0.0
        dE_windows_solar_gain_to_room = 0.0

        for window in self.windows:
            q_window_loss = window.u_value * window.area * (self.room_a.temp - sol_air_temp)
            dE_windows_loss_to_room -= q_window_loss * dt

            q_window_solar_gain = window.g_value * window.area * radiation_on_wall_surface
            dE_windows_solar_gain_to_room += q_window_solar_gain * dt

        dE_to_room_a = dE_solid_to_room + dE_windows_loss_to_room + dE_windows_solar_gain_to_room

        return { self.room_a: dE_to_room_a }

    @staticmethod
    def calculate_solar_on_surface(sun_radiation, sun_altitude, sun_azimuth, wall_dir):
        if sun_altitude <= 0.0:
            return 0.0

        angle_diff = abs(sun_azimuth - wall_dir)

        if angle_diff > 180.0:
            angle_diff = 360.0 - angle_diff

        if angle_diff > 90.0:
            return 0.0

        radiation = sun_radiation * math.cos(math.radians(angle_diff)) * math.cos(math.radians(sun_altitude))

        return max(0.0, radiation)

    class Window:
        def __init__(self, area, u_value, g_value):
            self.area = area
            self.u_value = u_value
            self.g_value = g_value

            self.shutter = 0.0