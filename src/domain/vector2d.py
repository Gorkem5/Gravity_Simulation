import math

class Vector2D:
    """
    A 2D vector class with common vector operations.
    """
    def __init__(self, x: float, y: float):
        """
        Initializes a Vector2D object.

        Args:
            x: The x-component of the vector.
            y: The y-component of the vector.
        """
        self.x = x
        self.y = y

    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        """
        Adds two vectors.

        Args:
            other: The vector to add.

        Returns:
            A new Vector2D object representing the sum of the two vectors.
        """
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        """
        Subtracts two vectors.

        Args:
            other: The vector to subtract.

        Returns:
            A new Vector2D object representing the difference of the two vectors.
        """
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2D':
        """
        Multiplies the vector by a scalar (vector * scalar).

        Args:
            scalar: The scalar to multiply by.

        Returns:
            A new Vector2D object representing the scaled vector.
        """
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> 'Vector2D':
        """
        Multiplies the vector by a scalar (scalar * vector).

        Args:
            scalar: The scalar to multiply by.

        Returns:
            A new Vector2D object representing the scaled vector.
        """
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector2D(self.x * scalar, self.y * scalar)

    def magnitude(self) -> float:
        """
        Calculates the magnitude (length) of the vector.

        Returns:
            The magnitude of the vector.
        """
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> 'Vector2D':
        """
        Normalizes the vector to a unit vector.

        Returns:
            A new Vector2D object representing the unit vector.
            Returns a zero vector if the magnitude is zero.
        """
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of the vector.

        Returns:
            A string representation of the vector.
        """
        return f"Vector2D({self.x}, {self.y})"

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the vector.

        Returns:
            A string representation of the vector.
        """
        return f"Vector2D({self.x!r}, {self.y!r})"

    def copy(self) -> 'Vector2D':
        """
        Creates a shallow copy of this Vector2D object.

        Returns:
            A new Vector2D object with the same x and y components.
        """
        return Vector2D(self.x, self.y)
