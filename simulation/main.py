from DistrictSimulation import DistrictSimulation

simulation = DistrictSimulation("district_config.yaml", "weather_history.csv")

print(simulation.run_step(dt_seconds=0))

for i in range(61*24):
    print(simulation.run_step(dt_seconds=60))
