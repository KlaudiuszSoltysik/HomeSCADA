import copy
import numpy as np

from SimulationEngine import SimulationEngine

class HeatPump:
    def __init__(self, nominal_heating_power_w=8000.0, nominal_cooling_power_w=7000.0,
                 nominal_temp_c=7.0, nominal_cop=4.5, nominal_eer=3.5,
                 optimal_load_percent=0.4):

        self.nominal_heating_power_w = nominal_heating_power_w
        self.nominal_cooling_power_w = nominal_cooling_power_w
        self.nominal_temp_c = nominal_temp_c
        self.nominal_cop = nominal_cop
        self.nominal_eer = nominal_eer
        self.optimal_load_percent = optimal_load_percent

        self.electrical_energy_consumed = 0.0

        self.heating_power_curve_temps = [-15.0, -7.0, 0.0, 7.0, 15.0]
        self.heating_power_curve_watts = [5000.0, 6000.0, 7000.0, 8000.0, 8500.0]
        self.heating_cop_curve_temps = [-15.0, -7.0, 0.0, 7.0, 15.0]
        self.heating_cop_curve_values = [2.2, 2.8, 3.5, 4.5, 5.5]

        self.cooling_power_curve_temps = [25.0, 30.0, 35.0]
        self.cooling_power_curve_watts = [7500.0, 7200.0, 7000.0]
        self.cooling_eer_curve_temps = [25.0, 30.0, 35.0]
        self.cooling_eer_curve_values = [4.0, 3.8, 3.5]

    def get_efficiency(self, external_temp, current_thermal_power_w, is_heating):
        if is_heating:
            max_power = np.interp(external_temp, self.heating_power_curve_temps, self.heating_power_curve_watts)

            if max_power == 0:
                return 1.0

            load_percent = min(current_thermal_power_w / max_power, 1.0)

            base_cop = np.interp(external_temp, self.heating_cop_curve_temps, self.heating_cop_curve_values)

            load_factor = self._calculate_load_factor(load_percent)
            final_cop = base_cop * load_factor

            return max(1.0, final_cop)
        else:
            max_power = np.interp(external_temp, self.cooling_power_curve_temps, self.cooling_power_curve_watts)

            if max_power == 0:
                return 1.0

            load_percent = min(current_thermal_power_w / max_power, 1.0)

            base_eer = np.interp(external_temp, self.cooling_eer_curve_temps, self.cooling_eer_curve_values)

            load_factor = self._calculate_load_factor(load_percent)
            final_eer = base_eer * load_factor

            return max(1.0, final_eer)

    def calculate_energy_stats(self, thermal_power_watts, dt_seconds, external_temp, is_heating):
        efficiency = self.get_efficiency(external_temp, thermal_power_watts, is_heating)

        if efficiency == 0:
            return

        electrical_power_watts = thermal_power_watts / efficiency
        electrical_energy_J = electrical_power_watts * dt_seconds
        electrical_energy_Wh = electrical_energy_J / 3600.0
        self.electrical_energy_consumed += electrical_energy_Wh

    def _calculate_load_factor(self, load_percent):
        penalty_factor = 0.3

        deviation_sq = (load_percent - self.optimal_load_percent)**2
        load_factor = 1.0 - penalty_factor * deviation_sq

        return max(0.7, load_factor)

class HeatPumpController:
    def __init__(self, building, weather_provider):
        self.building = building
        self.weather_provider = weather_provider

        self.horizon_hours = 4

    def calculate_optimal_actions(self, sim_parameters):
        forecast = self.weather_provider.get_forecast(sim_parameters=sim_parameters, horizon_hours=self.horizon_hours)

    def _run_virtual_simulation(self):
        pass

    def _calculate_cost(self):
        pass

    def _create_plan(self):
        pass

    # def _run_virtual_simulation(self, plan, forecast):
    #     virtual_building = copy.deepcopy(self.building)
    #     virtual_engine = SimulationEngine(virtual_building)
    #
    #     total_cost = 0
    #
    #     for i in range(self.horizon_hours):
    #         weather_step = forecast[i]
    #         action_step = plan[i]
    #
    #         virtual_engine.building.heat_pump.electrical_energy_consumed = 0
    #
    #         virtual_engine.run_simulation(
    #             dt=3600.0,
    #             steps=3600,
    #             weather=weather_step,
    #             heat_pump_actions=action_step
    #         )
    #
    #         total_cost += self._calculate_cost(virtual_building)
    #
    #     return total_cost
    #
    # def _calculate_cost(self, building_state):
    #     comfort_penalty = 0
    #     for room in building_state.rooms.values():
    #         comfort_penalty += max(0, self.target_temp - room.temp)**2
    #
    #     # TODO: Prices
    #     energy_cost = building_state.heat_pump.electrical_energy_consumed
    #
    #     return (comfort_penalty * 100) + energy_cost
    #
    # def _create_plan(self, power_watts, start_hour):
    #     plan = []
    #     for hour in range(self.horizon_hours):
    #         current_power = 0.0
    #         if hour >= start_hour:
    #             current_power = power_watts
    #
    #         plan.append({"living_room": current_power, "bedroom1": current_power})
    #     return plan