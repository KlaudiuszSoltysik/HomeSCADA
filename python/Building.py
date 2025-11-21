from HeatPump import HeatPump

class Building:
    def __init__(self, ground_temp):
        self.ground_temp = ground_temp

        self.rooms = {}
        self.walls = []

        self.heat_pump = HeatPump(heating_cop=4.0, cooling_eer=3.5, heating_power=80.0, cooling_power=40.0)

    def add_room(self, room):
        self.rooms[room.name] = room

    def add_wall(self, wall):
        self.walls.append(wall)
