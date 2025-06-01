from .vector2d import Vector2D

class CelestialBody:
    """
    Represents a celestial body with physical properties and movement capabilities.
    """
    def __init__(self, mass: float, position: Vector2D, velocity: Vector2D, radius: float, color: tuple, id: str):
        """
        Initializes a CelestialBody object.

        Args:
            mass: The mass of the celestial body.
            position: The initial position of the celestial body (a Vector2D object).
            velocity: The initial velocity of the celestial body (a Vector2D object).
            radius: The radius of the celestial body.
            color: The color of the celestial body (e.g., an RGB tuple).
            id: A unique identifier for the celestial body.
        """
        if mass <= 0:
            raise ValueError("Mass must be positive.")
        if radius <= 0:
            raise ValueError("Radius must be positive.")

        self.id: str = id
        self.mass: float = mass
        self.position: Vector2D = position
        self.velocity: Vector2D = velocity
        self.radius: float = radius
        self.color: tuple = color
        self.trail: list[Vector2D] = []
        self.max_trail_length: int = 50 # Default max length for the trail

    def update_position(self, time_step: float) -> None:
        """
        Updates the position of the celestial body based on its velocity.

        Args:
            time_step: The duration of the time step.
        """
        self.position += self.velocity * time_step

        # Add current position to the trail
        self.trail.append(self.position.copy()) # Use copy to store a snapshot

        # Ensure the trail doesn't exceed max_trail_length
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0) # Remove the oldest position

    def apply_force(self, force: Vector2D, time_step: float) -> None:
        """
        Updates the velocity of the celestial body based on an applied force.

        Args:
            force: The force applied to the celestial body (a Vector2D object).
            time_step: The duration of the time step.
        """
        if self.mass == 0:
            # Or raise an error: raise ValueError("Mass cannot be zero.")
            return  # No acceleration if mass is zero

        acceleration: Vector2D = force * (1.0 / self.mass) # scalar multiplication is right-associative
        self.velocity += acceleration * time_step

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of the celestial body.

        Returns:
            A string representation of the celestial body.
        """
        return (f"CelestialBody(mass={self.mass}, position={self.position}, "
                f"velocity={self.velocity}, radius={self.radius})")

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the celestial body.

        Returns:
            A string representation of the celestial body.
        """
        return (f"CelestialBody(id={self.id!r}, mass={self.mass!r}, position={self.position!r}, "
                f"velocity={self.velocity!r}, radius={self.radius!r}, color={self.color!r}, "
                f"trail_len={len(self.trail)})")
