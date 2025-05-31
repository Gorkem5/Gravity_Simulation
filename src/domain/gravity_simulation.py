from typing import List, Dict
from src.domain.celestial_body import CelestialBody
from src.domain.vector2d import Vector2D

class GravitySimulation:
    """
    Simulates gravitational interactions between celestial bodies.
    """
    def __init__(self, gravitational_constant: float, epsilon: float = 1e-9):
        """
        Initializes a GravitySimulation object.

        Args:
            gravitational_constant: The gravitational constant (G).
            epsilon: A small value to prevent division by zero when calculating forces
                     if two bodies are at the exact same position.
        """
        self.gravitational_constant: float = gravitational_constant
        self.bodies: List[CelestialBody] = []
        self.epsilon: float = epsilon  # To prevent division by zero
        self.paused: bool = False # For pausing the simulation
        # time_step_display is used by the renderer to show the current time_step.
        # It's set by SimulationService.
        self.time_step_display: float = 0.0 # Initial placeholder
        self._net_forces: Dict[CelestialBody, Vector2D] = {}

    def add_body(self, body: CelestialBody) -> None:
        """
        Adds a celestial body to the simulation.

        Args:
            body: The CelestialBody object to add.
        """
        self.bodies.append(body)

    def calculate_net_forces(self) -> None:
        """
        Calculates the net gravitational force on each body due to all other bodies.
        The calculated forces are stored in `self._net_forces`.

        Returns:
            A dictionary mapping each CelestialBody to its calculated net Vector2D force.
        """
        current_forces: Dict[CelestialBody, Vector2D] = {}
        for i, body_a in enumerate(self.bodies):
            net_force_on_a = Vector2D(0, 0)
            for j, body_b in enumerate(self.bodies):
                if i == j: # More robust way to check if it's the same body
                    continue

                # Vector from A to B
                delta_position: Vector2D = body_b.position - body_a.position

                # .magnitude() uses sqrt, so square it back for r^2
                # or calculate x^2 + y^2 directly
                distance_squared: float = delta_position.x**2 + delta_position.y**2

                # Add epsilon to prevent division by zero if bodies are at the same position
                # This also handles the r=0 case for normalization implicitly
                distance_r: float = (distance_squared + self.epsilon)**0.5

                if distance_r == 0: # Should ideally not happen if epsilon > 0
                    force_magnitude = 0.0
                    direction_vec = Vector2D(0,0) # No direction if distance is zero
                else:
                    force_magnitude: float = (self.gravitational_constant * body_a.mass * body_b.mass) / (distance_r**2)
                    # Normalized direction vector from A to B
                    # delta_position / distance_r
                    direction_vec = Vector2D(delta_position.x / distance_r, delta_position.y / distance_r)


                force_vec: Vector2D = direction_vec * force_magnitude
                net_force_on_a += force_vec

            current_forces[body_a] = net_force_on_a

        self._net_forces = current_forces # Store for internal use or debugging if still needed
        return current_forces

    def update(self, time_step: float) -> None:
        """
        Updates the simulation by one time step.

        This involves:
        1. Calculating net forces on all bodies.
        2. Applying these forces to update velocities.
        3. Updating positions based on the new velocities.

        Args:
            time_step: The duration of the time step.
        """
        if self.paused:
            return # Do nothing if paused

        # Calculate forces for this step
        forces_this_step = self.calculate_net_forces()

        # Apply forces to update velocities
        for body in self.bodies:
            net_force_on_body = forces_this_step.get(body, Vector2D(0, 0))
            body.apply_force(net_force_on_body, time_step)

        # Update positions
        for body in self.bodies:
            body.update_position(time_step)

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of the simulation state.
        """
        return f"GravitySimulation(G={self.gravitational_constant}, Bodies: {len(self.bodies)})"

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the simulation.
        """
        return (f"GravitySimulation(gravitational_constant={self.gravitational_constant!r}, "
                f"bodies={[repr(b) for b in self.bodies]}, epsilon={self.epsilon!r})")
