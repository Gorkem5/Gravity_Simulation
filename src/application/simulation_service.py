import pygame

from src.domain.gravity_simulation import GravitySimulation
from src.domain.celestial_body import CelestialBody
from src.domain.vector2d import Vector2D
from src.infrastructure.pygame_renderer import PygameRenderer
from .input_handler import InputHandler # Import InputHandler

class SimulationService:
    """
    Manages the overall simulation lifecycle, including initialization,
    the main simulation loop, and rendering.
    """
    def __init__(self, screen_width: int, screen_height: int, time_step: float, gravitational_constant: float):
        """
        Initializes the simulation service, gravity simulation, and renderer.

        Args:
            screen_width: The width of the simulation window.
            screen_height: The height of the simulation window.
            time_step: The time increment for each simulation update.
            gravitational_constant: The value of G to be used in the simulation.
        """
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.time_step: float = time_step

        # Initialize simulation and renderer
        self.simulation: GravitySimulation = GravitySimulation(gravitational_constant)
        self.renderer: PygameRenderer = PygameRenderer(screen_width, screen_height, "2D Gravity Simulation")
        self.input_handler: InputHandler = InputHandler() # Instantiate InputHandler

        self.running: bool = False
        self.clock = pygame.time.Clock()

        self._create_initial_bodies()
        # Initialize the time_step_display in the simulation object
        self.simulation.time_step_display = self.time_step

    def _create_initial_bodies(self) -> None:
        """
        Creates a set of initial celestial bodies and adds them to the simulation.
        These values are examples and might need tuning for interesting behavior
        depending on the gravitational_constant and time_step.
        """
        sun_mass = 1.989e6  # Example mass, significantly scaled for simulation
        sun_pos_x = self.screen_width / 2
        sun_pos_y = self.screen_height / 2

        sun = CelestialBody(
            mass=sun_mass,
            position=Vector2D(sun_pos_x, sun_pos_y),
            velocity=Vector2D(0, 0), # Sun is stationary
            radius=30,
            color=(255, 255, 0)  # Yellow
        )
        self.simulation.add_body(sun)

        # Planet 1 (Earth-like)
        # Orbital velocity v = sqrt(G * M_sun / r)
        # For G=100, M_sun=1.989e6, r=250: v = sqrt(100 * 1.989e6 / 250) ~ sqrt(795600) ~ 891.9
        # This is a very high velocity for typical screen pixel units per time_step.
        # The simulation parameters (G, masses, distances, time_step) need to be consistent.
        # Let's use a much smaller velocity for visual appeal with a G like 100-1000.
        earth_mass = 5.972e3 # Scaled mass
        earth_distance = 250 # Distance from sun
        earth_vy = 20 # Initial tangential velocity; adjust based on G and desired orbit

        earth = CelestialBody(
            mass=earth_mass,
            position=Vector2D(sun_pos_x + earth_distance, sun_pos_y),
            velocity=Vector2D(0, earth_vy),
            radius=10,
            color=(0, 100, 255)  # Blue
        )
        self.simulation.add_body(earth)

        # Planet 2 or Moon (orbiting the Sun for simplicity here)
        moon_mass = 7.347e1 # Scaled mass
        moon_distance = sun_pos_x + earth_distance + 50 # Further out
        moon_vy = earth_vy * 0.7 # Slower, further out

        moon = CelestialBody(
            mass=moon_mass,
            position=Vector2D(moon_distance, sun_pos_y),
            velocity=Vector2D(0, moon_vy),
            radius=5,
            color=(128, 128, 128)  # Grey
        )
        self.simulation.add_body(moon)

        # Third smaller body
        asteroid_mass = 1e1
        asteroid_distance = sun_pos_x - 150 # On the other side
        asteroid_vy = -earth_vy * 1.2 # Opposite direction, faster
        asteroid = CelestialBody(
            mass=asteroid_mass,
            position=Vector2D(asteroid_distance, sun_pos_y),
            velocity=Vector2D(0, asteroid_vy),
            radius=3,
            color=(200,150,100) # Brownish
        )
        self.simulation.add_body(asteroid)


    def run_simulation_loop(self) -> None:
        """
        Runs the main simulation loop, handling events, updating state, and rendering.
        """
        self.running = True # Start the loop
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: # Allow exiting with ESC key
                        self.running = False

                # Handle other inputs using InputHandler
                self.input_handler.handle_input(self, event)

            # Update simulation state (respects simulation.paused)
            self.simulation.update(self.time_step)
            # Ensure the display time_step is current if it was changed by input_handler
            self.simulation.time_step_display = self.time_step

            # Render the current state
            self.renderer.render(self.simulation)

            # Cap the frame rate
            self.clock.tick(60)  # Aim for 60 FPS

        # Clean up Pygame
        self.renderer.quit()

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of the simulation service.
        """
        return (f"SimulationService(screen_width={self.screen_width}, screen_height={self.screen_height}, "
                f"time_step={self.time_step}, running={self.running})")


    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the simulation service.
        """
        return (f"SimulationService(screen_width={self.screen_width!r}, screen_height={self.screen_height!r}, "
                f"time_step={self.time_step!r}, gravitational_constant={self.simulation.gravitational_constant!r}, "
                f"running={self.running!r}, bodies_count={len(self.simulation.bodies)})")

# Example usage (typically in a main.py or similar entry point)
if __name__ == '__main__':
    # This block is for direct testing of the SimulationService.

    SCREEN_WIDTH = 1600  # Larger screen for better visualization
    SCREEN_HEIGHT = 900
    TIME_STEP = 0.01    # A smaller time step can increase accuracy but slows down simulation.
                        # 0.01 to 0.1 are common starting points.

    # This G is not the real-world G (6.674e-11 N(m/kg)^2), but a value tuned
    # for this simulation's scale of mass, distance (pixels), and time (steps).
    # You'll likely need to experiment with this value.
    # If G is too high, bodies fly apart or collapse too quickly.
    # If G is too low, interactions are too weak to be interesting.
    GRAVITATIONAL_CONSTANT = 500 # Increased G for more noticeable interaction with given masses

    print("Initializing SimulationService...")
    service = SimulationService(SCREEN_WIDTH, SCREEN_HEIGHT, TIME_STEP, GRAVITATIONAL_CONSTANT)
    print(f"Created {len(service.simulation.bodies)} initial bodies.")
    print("Starting simulation loop... (Press ESC or close window to exit)")
    service.run_simulation_loop()
    print("Simulation finished.")
