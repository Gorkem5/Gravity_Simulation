"""
Main entry point for the 2D Gravity Simulation application.

This script initializes and runs the simulation service, which in turn handles
the simulation logic and rendering.
"""
from src.application.simulation_service import SimulationService

# Screen dimensions for the Pygame window
SCREEN_WIDTH: int = 1200
SCREEN_HEIGHT: int = 800

# Simulation parameters
# TIME_STEP influences the speed and stability of the simulation.
# Smaller values increase accuracy but slow down the perceived speed.
TIME_STEP: float = 0.01  # Start with a small time step

# GRAVITATIONAL_CONSTANT is a key factor in the strength of gravitational forces.
# This value is not the real-world G, but one tuned for the simulation's scale
# of mass, distance (pixels), and time (steps).
# It will likely require experimentation to find a value that produces
# visually appealing and stable simulations with the chosen masses and distances.
GRAVITATIONAL_CONSTANT: float = 100  # Example value, may need significant tuning

if __name__ == "__main__":
    print("Starting 2D Gravity Simulation...")

    # Create the simulation service with the defined parameters
    service = SimulationService(
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
        time_step=TIME_STEP,
        gravitational_constant=GRAVITATIONAL_CONSTANT
    )

    print(f"Simulation service initialized with G={GRAVITATIONAL_CONSTANT}, time_step={TIME_STEP}.")
    print(f"Initial bodies: {len(service.simulation.bodies)}")
    for i, body in enumerate(service.simulation.bodies):
        print(f"  Body {i+1}: mass={body.mass:.2e}, pos=({body.position.x:.2f}, {body.position.y:.2f}), vel=({body.velocity.x:.2f}, {body.velocity.y:.2f})")

    # Run the main simulation loop
    print("Running simulation loop... Press ESC or close the window to exit.")
    service.run_simulation_loop()

    print("Simulation finished. Exiting application.")
