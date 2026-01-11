import yaml
import numpy as np

class ThermalModelParser:
    def __init__(self, yaml_path):
        with open(yaml_path, "r") as f:
            self.raw_data = yaml.safe_load(f)

        self.nodes = {}
        self.node_to_building_map = {}
        self.room_data = []

        self._build_node_index()
        self.N = len(self.nodes)

        self.G = np.zeros((self.N, self.N))
        self.C = np.zeros(self.N)

    def _build_node_index(self):
        idx = 0
        
        for b_idx, building in enumerate(self.raw_data["buildings"]):
            b_standards = building["standards"]

            for apt in building["apartments"]:
                apt_id = apt["id"]

                for room in apt["rooms"]:
                    room_id = f"{apt_id}:{room['id']}"
                    self.nodes[room_id] = idx

                    self.room_data.append({
                        "room": room,
                        "standards": b_standards
                    })
                    idx += 1

    def parse(self):
        for i, data in enumerate(self.room_data):
            room = data["room"]
            standards = data["standards"]

            c_air = room["volume"] * 1200

            capacity_key = room["heat_capacity_per_m2"]

            capacity_value = standards[capacity_key]["heat_capacity_per_m2"]

            c_interior = room["area"] * capacity_value
            self.C[i] = c_air + c_interior

        for building in self.raw_data["buildings"]:
            b_standards = building["standards"]

            if "internal_connections" in building:
                for conn in building["internal_connections"]:
                    self._apply_internal_connection(conn, b_standards)

            if "external_connections" in building:
                for conn in building["external_connections"]:
                    self._apply_external_connection(conn, b_standards)

        return self.G, self.C

    def _apply_internal_connection(self, connection, standards):
        idx_a = self.nodes[connection["from"]]
        idx_b = self.nodes[connection["to"]]

        code = standards[connection["thermal_code"]]
        ua = connection["area"] * code["u_value"]

        self.G[idx_a, idx_b] += ua
        self.G[idx_b, idx_a] += ua

        wall_capacity = connection["area"] * code["heat_capacity_per_m2"]

        self.C[idx_a] += wall_capacity * 0.5
        self.C[idx_b] += wall_capacity * 0.5

    def _apply_external_connection(self, connection, standards):
        idx_a = self.nodes[connection["from"]]
        thermal_code = standards[connection["thermal_code"]]

        windows_list = connection.get("windows", [])

        windows_area = sum(w["area"] for w in windows_list)
        wall_net_area = connection["area"] - windows_area

        ua_wall = wall_net_area * thermal_code["u_value"]

        ua_windows = sum(w["area"] * standards[w["thermal_code"]]["u_value"] for w in windows_list)

        connection["calculated_ua"] = ua_wall + ua_windows

        if not hasattr(self, 'G_ext'):
            self.G_ext = np.zeros(self.N)
        self.G_ext[idx_a] += (ua_wall + ua_windows)

        wall_capacity = wall_net_area * thermal_code["heat_capacity_per_m2"]
        self.C[idx_a] += wall_capacity

parser = ThermalModelParser("district_config.yaml")
G, C = parser.parse()

print(G)
print(C)