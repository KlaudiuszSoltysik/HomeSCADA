import numpy as np


class ThermalSolver:
    def __init__(self, G, C, G_ext_air, G_ext_ground, T_ground=8.0):
        self.G = G
        self.C = C
        self.G_ext_air = G_ext_air
        self.G_ext_ground = G_ext_ground
        self.T_ground = T_ground

        self.T = np.full(len(C), 21.0)

    def step(self, dt, T_outside, Q_extra):
        dT_inter = np.dot(self.G, self.T) - (np.sum(self.G, axis=1) * self.T)

        dT_air = self.G_ext_air * (T_outside - self.T)

        dT_ground = self.G_ext_ground * (self.T_ground - self.T)

        total_Q = dT_inter + dT_air + dT_ground + Q_extra

        self.T += (total_Q / self.C) * dt

        return self.T
