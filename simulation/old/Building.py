from HeatPump import HeatPump

class Building:
    def __init__(self, ground_temp):
        self.ground_temp = ground_temp

        self.rooms = {}
        self.walls = []

        self.heat_pump = HeatPump()

    def add_room(self, room):
        self.rooms[room.name] = room

    def add_wall(self, wall):
        self.walls.append(wall)
