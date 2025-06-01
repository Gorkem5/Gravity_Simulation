from .domain.gravity_simulation import GravitySimulation
from .domain.celestial_body import CelestialBody
from .domain.vector2d import Vector2D

class SimulationSingletonMeta(type):
    """
    Metaclass for creating a Singleton. Ensures only one instance of SimulationManager exists.
    """
    _instances = {} # type: dict[type, SimulationManager]

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class SimulationManager(metaclass=SimulationSingletonMeta):
    """
    Manages the global instance of the GravitySimulation using a singleton pattern.
    """
    # Default simulation parameters, can be overridden by API calls.
    DEFAULT_G: float = 100.0
    DEFAULT_TIME_STEP: float = 0.01

    def __init__(self):
        """
        Initializes the SimulationManager, which in turn initializes the
        GravitySimulation instance. This constructor is called only once
        due to the singleton metaclass.
        """
        print("SimulationManager __init__ called (should be once).")
        self.simulation: GravitySimulation = GravitySimulation(
            gravitational_constant=self.DEFAULT_G
        )
        self.simulation.time_step_display = self.DEFAULT_TIME_STEP
        self._initialize_default_bodies()

    def _initialize_default_bodies(self) -> None:
        """
        Adds a set of default celestial bodies to the simulation.
        This method is called on initial setup and on reset.
        """
        # Ensure simulation instance exists (it should if __init__ ran)
        if not hasattr(self, 'simulation') or self.simulation is None:
             # This case should ideally not be hit if __init__ is managed by singleton correctly
            print("Re-initializing simulation instance in _initialize_default_bodies")
            self.simulation = GravitySimulation(gravitational_constant=self.DEFAULT_G)
            self.simulation.time_step_display = self.DEFAULT_TIME_STEP

        self.simulation.bodies.clear() # Clear existing bodies before adding defaults

        # Define some default bodies
        # Using somewhat more realistic relative masses for Sun/Earth if G is tuned.
        # With G=100, these masses/velocities might need tuning for stable orbits.
        sun = CelestialBody(
            mass=1.989e6, # Scaled down "large" mass
            position=Vector2D(400, 300),
            velocity=Vector2D(0, 0),
            radius=20,
            color=(255, 255, 0),
            id="sun"
        )
        earth = CelestialBody(
            mass=5.972e3, # Scaled down "small" mass
            position=Vector2D(400, 500), # Position relative to sun (e.g., 200 units away)
            velocity=Vector2D(15, 0), # Initial velocity for orbit (needs tuning with G)
            radius=7,
            color=(0, 100, 255),
            id="earth"
        )
        moon = CelestialBody(
            mass=7.347e1,
            position=Vector2D(400, 520), # Close to earth
            velocity=Vector2D(15+2, 0), # Orbiting with earth, plus a bit more for its own orbit
            radius=3,
            color=(128,128,128),
            id="moon"
        )

        self.simulation.add_body(sun)
        self.simulation.add_body(earth)
        self.simulation.add_body(moon)
        print(f"Default bodies initialized. Total bodies: {len(self.simulation.bodies)}")

    def get_simulation_instance(self) -> GravitySimulation:
        """
        Provides access to the managed simulation instance.
        """
        return self.simulation

    def reset_simulation(self, gravitational_constant: Optional[float] = None, time_step: Optional[float] = None) -> GravitySimulation:
        """
        Resets the global simulation instance with new parameters or defaults.
        Default bodies are re-initialized.

        Args:
            gravitational_constant: The new gravitational constant. If None, uses class default.
            time_step: The new time step for the simulation (primarily for display/reference). If None, uses class default.

        Returns:
            The reset simulation instance.
        """
        current_g = gravitational_constant if gravitational_constant is not None else self.DEFAULT_G
        current_ts = time_step if time_step is not None else self.DEFAULT_TIME_STEP

        print(f"Resetting simulation. G={current_g}, TimeStepRef={current_ts}")
        self.simulation = GravitySimulation(gravitational_constant=current_g)
        self.simulation.time_step_display = current_ts
        self._initialize_default_bodies() # Re-add default bodies

        return self.simulation

# Note: The singleton pattern means `SimulationManager()` will always return the same instance.
# The instance is created when the module is first imported and `SimulationManager()` is called,
# or when `SimulationManager()` is explicitly called the first time.
# For the API, Uvicorn typically loads the module, and then endpoints will access the singleton.
