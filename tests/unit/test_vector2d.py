import unittest
import math
from src.domain.vector2d import Vector2D

class TestVector2D(unittest.TestCase):
    """Test suite for the Vector2D class."""

    def test_initialization(self):
        """Test that Vector2D initializes with correct x and y components."""
        v = Vector2D(1.5, -2.5)
        self.assertEqual(v.x, 1.5)
        self.assertEqual(v.y, -2.5)

    def test_addition(self):
        """Test vector addition."""
        v1 = Vector2D(1, 2)
        v2 = Vector2D(3, 4)
        result = v1 + v2
        self.assertEqual(result.x, 4)
        self.assertEqual(result.y, 6)

        # Test addition with non-Vector2D (should return NotImplemented or raise TypeError indirectly)
        # The actual TypeError might come from the other object if Vector2D returns NotImplemented
        try:
            _ = v1 + 5 # type: ignore
        except TypeError:
            pass # Expected
        else:
            self.fail("TypeError not raised for v1 + 5")


    def test_subtraction(self):
        """Test vector subtraction."""
        v1 = Vector2D(5, 3)
        v2 = Vector2D(1, 2)
        result = v1 - v2
        self.assertEqual(result.x, 4)
        self.assertEqual(result.y, 1)

        try:
            _ = v1 - 5 # type: ignore
        except TypeError:
            pass # Expected
        else:
            self.fail("TypeError not raised for v1 - 5")


    def test_scalar_multiplication(self):
        """Test multiplication by a scalar (both v * scalar and scalar * v)."""
        v = Vector2D(2, -3)
        scalar = 3

        # Test v * scalar
        result1 = v * scalar
        self.assertEqual(result1.x, 6)
        self.assertEqual(result1.y, -9)

        # Test scalar * v
        result2 = scalar * v
        self.assertEqual(result2.x, 6)
        self.assertEqual(result2.y, -9)

        try:
            _ = v * Vector2D(1,1) # type: ignore
        except TypeError:
            pass # Expected
        else:
            self.fail("TypeError not raised for v * Vector2D")


    def test_magnitude(self):
        """Test magnitude calculation."""
        v1 = Vector2D(3, 4)
        self.assertAlmostEqual(v1.magnitude(), 5.0)

        v2 = Vector2D(0, 0) # Zero vector
        self.assertAlmostEqual(v2.magnitude(), 0.0)

        v3 = Vector2D(-1, 0)
        self.assertAlmostEqual(v3.magnitude(), 1.0)

    def test_normalize(self):
        """Test vector normalization."""
        v1 = Vector2D(3, 4)
        norm_v1 = v1.normalize()
        self.assertAlmostEqual(norm_v1.x, 3/5)
        self.assertAlmostEqual(norm_v1.y, 4/5)
        self.assertAlmostEqual(norm_v1.magnitude(), 1.0, places=7) # Check if it's a unit vector

        v2 = Vector2D(0, 0) # Zero vector
        norm_v2 = v2.normalize()
        self.assertEqual(norm_v2.x, 0) # Should return zero vector
        self.assertEqual(norm_v2.y, 0)
        self.assertAlmostEqual(norm_v2.magnitude(), 0.0)

        v3 = Vector2D(5, 0)
        norm_v3 = v3.normalize()
        self.assertAlmostEqual(norm_v3.x, 1.0)
        self.assertAlmostEqual(norm_v3.y, 0.0)

    def test_str_representation(self):
        """Test the __str__ representation."""
        v = Vector2D(1.2, 3.4)
        self.assertEqual(str(v), "Vector2D(1.2, 3.4)")

    def test_repr_representation(self):
        """Test the __repr__ representation."""
        v = Vector2D(1, 2)
        self.assertEqual(repr(v), "Vector2D(1, 2)")

if __name__ == '__main__':
    unittest.main()
