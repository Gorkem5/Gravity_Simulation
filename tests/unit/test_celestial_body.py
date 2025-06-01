import unittest
from src.api.domain.celestial_body import CelestialBody # Updated import path
from src.api.domain.vector2d import Vector2D # Updated import path

class TestCelestialBody(unittest.TestCase):
    """Test suite for the CelestialBody class."""

    def setUp(self):
        """Set up a default CelestialBody instance for tests."""
        self.default_mass = 100.0
        self.default_pos = Vector2D(0.0, 0.0) # Use floats for consistency
        self.default_vel = Vector2D(0.0, 0.0) # Use floats
        self.default_radius = 5.0
        self.default_color = (255, 255, 255)
        self.default_id = "test_body_1"

        self.body = CelestialBody(
            mass=self.default_mass,
            position=self.default_pos,
            velocity=self.default_vel,
            radius=self.default_radius,
            color=self.default_color,
            id=self.default_id
        )

    def test_initialization(self):
        """Test that CelestialBody initializes with correct attributes."""
        self.assertEqual(self.body.mass, self.default_mass)
        self.assertEqual(self.body.position.x, self.default_pos.x)
        self.assertEqual(self.body.position.y, self.default_pos.y)
        self.assertEqual(self.body.velocity.x, self.default_vel.x)
        self.assertEqual(self.body.velocity.y, self.default_vel.y)
        self.assertEqual(self.body.radius, self.default_radius)
        self.assertEqual(self.body.color, self.default_color)
        self.assertEqual(self.body.id, self.default_id)

    def test_update_position_zero_velocity(self):
        """Test position update with zero velocity."""
        time_step = 1.0
        initial_pos_x = self.body.position.x
        initial_pos_y = self.body.position.y

        self.body.update_position(time_step)

        self.assertAlmostEqual(self.body.position.x, initial_pos_x)
        self.assertAlmostEqual(self.body.position.y, initial_pos_y)

    def test_update_position_non_zero_velocity(self):
        """Test position update with non-zero velocity."""
        self.body.velocity = Vector2D(10.0, -5.0)
        time_step = 0.5

        # Expected new position: pos + vel * dt
        # x = 0.0 + 10.0 * 0.5 = 5.0
        # y = 0.0 + (-5.0) * 0.5 = -2.5
        expected_pos_x = 5.0
        expected_pos_y = -2.5

        self.body.update_position(time_step)

        self.assertAlmostEqual(self.body.position.x, expected_pos_x)
        self.assertAlmostEqual(self.body.position.y, expected_pos_y)

    def test_apply_force_at_rest(self):
        """Test applying force to a body at rest."""
        force = Vector2D(200.0, 100.0)
        time_step = 0.1
        # mass = 100.0

        # acceleration = force / mass
        # ax = 200.0 / 100.0 = 2.0
        # ay = 100.0 / 100.0 = 1.0
        #
        # velocity += acceleration * time_step
        # vx = 2.0 * 0.1 = 0.2
        # vy = 1.0 * 0.1 = 0.1
        expected_vel_x = 0.2
        expected_vel_y = 0.1

        self.body.apply_force(force, time_step)

        self.assertAlmostEqual(self.body.velocity.x, expected_vel_x)
        self.assertAlmostEqual(self.body.velocity.y, expected_vel_y)

    def test_apply_force_already_moving(self):
        """Test applying force to a body already in motion."""
        self.body.velocity = Vector2D(1.0, 1.0) # Initial velocity
        force = Vector2D(100.0, -50.0)
        time_step = 0.2
        # mass = 100.0

        # acceleration = force / mass
        # ax = 100.0 / 100.0 = 1.0
        # ay = -50.0 / 100.0 = -0.5
        #
        # delta_v = acceleration * time_step
        # dvx = 1.0 * 0.2 = 0.2
        # dvy = -0.5 * 0.2 = -0.1
        #
        # final_velocity = initial_velocity + delta_v
        # final_vx = 1.0 + 0.2 = 1.2
        # final_vy = 1.0 + (-0.1) = 0.9
        expected_vel_x = 1.2
        expected_vel_y = 0.9

        self.body.apply_force(force, time_step)

        self.assertAlmostEqual(self.body.velocity.x, expected_vel_x)
        self.assertAlmostEqual(self.body.velocity.y, expected_vel_y)

    def test_apply_force_zero_mass(self):
        """Test applying force to a body with zero mass."""
        self.body.mass = 0.0
        force = Vector2D(10.0, 10.0)
        time_step = 1.0

        initial_vel_x = self.body.velocity.x
        initial_vel_y = self.body.velocity.y

        # Current CelestialBody.apply_force returns if mass is 0.
        self.body.apply_force(force, time_step)

        self.assertAlmostEqual(self.body.velocity.x, initial_vel_x, msg="Velocity x should not change for zero mass body.")
        self.assertAlmostEqual(self.body.velocity.y, initial_vel_y, msg="Velocity y should not change for zero mass body.")

    def test_str_representation(self):
        """Test the __str__ representation."""
        s = str(self.body)
        # Example: CelestialBody(mass=100.0, position=Vector2D(0.0, 0.0), velocity=Vector2D(0.0, 0.0), radius=5.0)
        self.assertIn("CelestialBody(mass=100.0", s)
        self.assertIn("position=Vector2D(0.0, 0.0)", s) # Adjusted to float
        self.assertIn("velocity=Vector2D(0.0, 0.0)", s) # Adjusted to float
        self.assertIn("radius=5.0)",s)

    def test_repr_representation(self):
        """Test the __repr__ representation."""
        expected_repr = f"CelestialBody(id={self.body.id!r}, mass={self.body.mass!r}, position={self.body.position!r}, velocity={self.body.velocity!r}, radius={self.body.radius!r}, color={self.body.color!r}, trail_len={len(self.body.trail)})"
        self.assertEqual(repr(self.body), expected_repr)


if __name__ == '__main__':
    unittest.main()
