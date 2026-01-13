class SimulationEngine:
    def __init__(self, building):
        self.building = building

    def step(self, dt, weather):
        heat_transfers_room = {name: 0.0 for name in self.building.rooms.keys()}
        heat_transfers_floor = {name: 0.0 for name in self.building.rooms.keys()}

        for wall in self.building.walls:
            energy_transfers = wall.calculate_flow(dt, weather.temp, weather.wind_speed, weather.wind_dir, weather.sun_radiation, weather.sun_altitude, weather.sun_azimuth)

            for room, dE in energy_transfers.items():
                heat_transfers_room[room.name] += dE

        for room in self.building.rooms.values():
            # FLOOR FLOW
            dE = room.floor.calculate_flow(dt, room.temp, self.building.ground_temp)
            heat_transfers_room[room.name] += dE

            # FLOOR HEATING AND COOLING
            # q_hac = self.heat_pump.temp_control(room, dt)
            # heat_transfers_floor[room.name] += q_hac * dt

            # ROOF FLOW
            dE_roof = room.roof.calculate_flow(dt, room.temp, weather.temp, weather.wind_speed, weather.sun_radiation, weather.sun_altitude)
            heat_transfers_room[room.name] += dE_roof

            # INTERNAL GAIN
            q_internal = room.internal_heat
            heat_transfers_room[room.name] += q_internal * dt

        for name, dE in heat_transfers_room.items():
            room = self.building.rooms[name]
            room.temp += dE / room.heat_capacity

        for name, dE_floor in heat_transfers_floor.items():
            room = self.building.rooms[name]
            room.floor.temp += dE_floor / room.floor.heat_capacity

    def run_simulation(self, dt, steps, weather):
        num_steps = int(steps)
        dt_internal = dt / num_steps

        for i in range(num_steps):
            self.step(dt=dt_internal,weather=weather)

        return { r.name: round(r.temp * 100.0) / 100.0 for r in self.building.rooms.values() }
