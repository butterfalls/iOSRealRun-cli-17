from pymobiledevice3.cli.developer import LocationSimulation

def create_simulation(dvt):
    return LocationSimulation(dvt)

def set_location(dvt, lat: float, lng: float):
    create_simulation(dvt).set(lat, lng)

def set_simulated_location(simulation, lat: float, lng: float):
    simulation.set(lat, lng)

def clear_location(target):
    if hasattr(target, "clear"):
        target.clear()
    else:
        create_simulation(target).clear()
