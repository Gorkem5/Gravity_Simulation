import unittest
from src.domain.gravity_simulation import GravitySimulation
from src.domain.celestial_body import CelestialBody
from src.domain.vector2d import Vector2D
import math # For more complex calculations if needed

class TestGravitySimulation(unittest.TestCase):
    """Test suite for the GravitySimulation class."""

    def setUp(self):
        """Set up a simulation instance and some bodies."""
        self.G = 100.0  # Use a G that's easy to calculate with
        self.time_step = 0.1
        self.simulation = GravitySimulation(gravitational_constant=self.G, epsilon=1e-12) # smaller epsilon
        self.simulation.time_step_display = self.time_step

        # Define bodies for use in multiple tests
        self.body_at_origin = CelestialBody(mass=10.0, position=Vector2D(0.0, 0.0), velocity=Vector2D(0.0, 0.0), radius=1.0, color=(0,0,0))
        self.body_on_x_axis = CelestialBody(mass=20.0, position=Vector2D(10.0, 0.0), velocity=Vector2D(0.0, 0.0), radius=1.0, color=(0,0,0))
        self.body_in_quadrant1 = CelestialBody(mass=30.0, position=Vector2D(5.0, 5.0), velocity=Vector2D(0.0, 1.0), radius=1.0, color=(0,0,0))

    def test_initialization_attributes(self):
        """Test if GravitySimulation initializes attributes correctly."""
        self.assertEqual(self.simulation.gravitational_constant, self.G)
        self.assertEqual(len(self.simulation.bodies), 0)
        self.assertFalse(self.simulation.paused)
        self.assertEqual(self.simulation.time_step_display, self.time_step)


    def test_add_body(self):
        """Test adding a body to the simulation."""
        self.assertEqual(len(self.simulation.bodies), 0)
        self.simulation.add_body(self.body_at_origin)
        self.assertEqual(len(self.simulation.bodies), 1)
        self.assertIn(self.body_at_origin, self.simulation.bodies)
        self.simulation.add_body(self.body_on_x_axis)
        self.assertEqual(len(self.simulation.bodies), 2)
        self.assertIn(self.body_on_x_axis, self.simulation.bodies)


    def test_calculate_net_forces_two_bodies(self):
        """Test net force calculation for two bodies."""
        self.simulation.add_body(self.body_at_origin)
        self.simulation.add_body(self.body_on_x_axis)

        # F = G * m1 * m2 / r^2
        # r = 10, r^2 = 100
        # F_mag = 100.0 * 10.0 * 20.0 / 100.0 = 200.0

        expected_force_on_b1 = Vector2D(200.0, 0.0) # Force on body1 (at origin) by body2 (+x dir)
        expected_force_on_b2 = Vector2D(-200.0, 0.0) # Force on body2 by body1 (-x dir)

        forces = self.simulation.calculate_net_forces()

        self.assertIn(self.body_at_origin, forces)
        self.assertIn(self.body_on_x_axis, forces)

        self.assertAlmostEqual(forces[self.body_at_origin].x, expected_force_on_b1.x)
        self.assertAlmostEqual(forces[self.body_at_origin].y, expected_force_on_b1.y)
        self.assertAlmostEqual(forces[self.body_on_x_axis].x, expected_force_on_b2.x)
        self.assertAlmostEqual(forces[self.body_on_x_axis].y, expected_force_on_b2.y)

    def test_calculate_net_forces_three_bodies(self):
        """Test net force calculation for three bodies."""
        b1 = self.body_at_origin    # m=10 at (0,0)
        b2 = self.body_on_x_axis  # m=20 at (10,0)
        b3 = self.body_in_quadrant1 # m=30 at (5,5)
        self.simulation.add_body(b1)
        self.simulation.add_body(b2)
        self.simulation.add_body(b3)

        # --- Force on b1 (m=10 at (0,0)) ---
        # Due to b2 (m=20 at (10,0)): r=10, F_mag = G*10*20/100 = 2G = 200. Dir: (1,0)
        F12_vec = Vector2D(200.0, 0.0)

        # Due to b3 (m=30 at (5,5)): r_vec=(5,5), r=sqrt(50), r^2=50. Dir_norm = (5/sqrt(50), 5/sqrt(50))
        # F_mag = G*10*30/50 = 6G = 600.0
        dist_13 = math.sqrt(50)
        F13_mag = self.G * b1.mass * b3.mass / 50.0
        F13_x = F13_mag * (b3.position.x / dist_13)
        F13_y = F13_mag * (b3.position.y / dist_13)
        F13_vec = Vector2D(F13_x, F13_y)
        Expected_F1_total = F12_vec + F13_vec

        # --- Force on b2 (m=20 at (10,0)) ---
        # Due to b1 (m=10 at (0,0)): r=10, F_mag = 200. Dir: (-1,0)
        F21_vec = Vector2D(-200.0, 0.0)

        # Due to b3 (m=30 at (5,5)): r_vec_b3_to_b2=(5,-5), r_vec_b2_to_b3=(-5,5) r=sqrt(50), r^2=50.
        dist_23 = math.sqrt((-5.0)**2 + (5.0)**2) # sqrt(25+25) = sqrt(50)
        F23_mag = self.G * b2.mass * b3.mass / 50.0 # G*20*30/50 = 12G = 1200
        F23_x = F23_mag * (-5.0 / dist_23) # Direction from b2 to b3
        F23_y = F23_mag * (5.0 / dist_23)  # Direction from b2 to b3
        F23_vec = Vector2D(F23_x, F23_y)
        Expected_F2_total = F21_vec + F23_vec

        # --- Force on b3 (m=30 at (5,5)) ---
        # Due to b1 (m=10 at (0,0)): F31_vec = -F13_vec
        F31_vec = Vector2D(-F13_x, -F13_y)

        # Due to b2 (m=20 at (10,0)): F32_vec = -F23_vec
        F32_vec = Vector2D(-F23_x, -F23_y)
        Expected_F3_total = F31_vec + F32_vec

        forces = self.simulation.calculate_net_forces()

        self.assertAlmostEqual(forces[b1].x, Expected_F1_total.x, places=5)
        self.assertAlmostEqual(forces[b1].y, Expected_F1_total.y, places=5)
        self.assertAlmostEqual(forces[b2].x, Expected_F2_total.x, places=5)
        self.assertAlmostEqual(forces[b2].y, Expected_F2_total.y, places=5)
        self.assertAlmostEqual(forces[b3].x, Expected_F3_total.x, places=5)
        self.assertAlmostEqual(forces[b3].y, Expected_F3_total.y, places=5)


    def test_update_no_force_single_body_moving(self):
        """Test update with a single moving body (G will apply no force, or no other bodies)."""
        body = CelestialBody(mass=10.0, position=Vector2D(0.0,0.0), velocity=Vector2D(1.0,2.0), radius=1.0, color=(0,0,0))
        self.simulation.add_body(body)

        # Store G and set to 0 for this test, or ensure only one body is present
        original_G = self.simulation.gravitational_constant
        if len(self.simulation.bodies) > 1: # If other tests added bodies to self.simulation
             self.simulation.bodies = [body] # Isolate the body

        self.simulation.gravitational_constant = 0.0

        self.simulation.update(self.time_step) # time_step = 0.1

        # Expected position: pos + vel * dt = (0,0) + (1,2)*0.1 = (0.1, 0.2)
        self.assertAlmostEqual(body.position.x, 0.1)
        self.assertAlmostEqual(body.position.y, 0.2)
        self.assertAlmostEqual(body.velocity.x, 1.0, msg="Velocity X should not change")
        self.assertAlmostEqual(body.velocity.y, 2.0, msg="Velocity Y should not change")
        self.simulation.gravitational_constant = original_G # Restore G


    def test_update_two_bodies_attraction(self):
        """Test that two bodies attract each other over a small time_step."""
        b1 = self.body_at_origin # m=10 at (0,0), vel(0,0)
        b2 = self.body_on_x_axis # m=20 at (10,0), vel(0,0)
        self.simulation.bodies = [] # Clear any bodies from setUp if they were added to self.simulation
        self.simulation.add_body(b1)
        self.simulation.add_body(b2)

        # Initial forces (as per test_calculate_net_forces_two_bodies):
        # F_on_b1 = (200,0), F_on_b2 = (-200,0)
        # G=100, time_step=0.1

        self.simulation.update(self.time_step)

        # --- Body1 ---
        # acc1 = F/m1 = (200,0)/10 = (20,0)
        # vel1 = acc1 * dt = (20,0)*0.1 = (2,0)
        # pos1 = initial_pos1 + vel1 * dt = (0,0) + (2,0)*0.1 = (0.2, 0)
        self.assertAlmostEqual(b1.velocity.x, 2.0)
        self.assertAlmostEqual(b1.velocity.y, 0.0)
        # Position update uses the *new* velocity for the entire time_step in this model
        self.assertAlmostEqual(b1.position.x, 0.0 + 2.0 * self.time_step)
        self.assertAlmostEqual(b1.position.y, 0.0)

        # --- Body2 ---
        # acc2 = F/m2 = (-200,0)/20 = (-10,0)
        # vel2 = acc2 * dt = (-10,0)*0.1 = (-1,0)
        # pos2 = initial_pos2 + vel2 * dt = (10,0) + (-1,0)*0.1 = (10 - 0.1, 0) = (9.9, 0)
        self.assertAlmostEqual(b2.velocity.x, -1.0)
        self.assertAlmostEqual(b2.velocity.y, 0.0)
        self.assertAlmostEqual(b2.position.x, 10.0 + (-1.0) * self.time_step)
        self.assertAlmostEqual(b2.position.y, 0.0)


    def test_paused_simulation(self):
        """Ensure calling update when paused does not change body states."""
        self.simulation.add_body(self.body_at_origin)
        self.simulation.add_body(self.body_on_x_axis)
        self.simulation.paused = True

        # Capture initial states
        b1_pos_x, b1_pos_y = self.body_at_origin.position.x, self.body_at_origin.position.y
        b1_vel_x, b1_vel_y = self.body_at_origin.velocity.x, self.body_at_origin.velocity.y
        b2_pos_x, b2_pos_y = self.body_on_x_axis.position.x, self.body_on_x_axis.position.y
        b2_vel_x, b2_vel_y = self.body_on_x_axis.velocity.x, self.body_on_x_axis.velocity.y

        self.simulation.update(self.time_step)

        self.assertAlmostEqual(self.body_at_origin.position.x, b1_pos_x)
        self.assertAlmostEqual(self.body_at_origin.position.y, b1_pos_y)
        self.assertAlmostEqual(self.body_at_origin.velocity.x, b1_vel_x)
        self.assertAlmostEqual(self.body_at_origin.velocity.y, b1_vel_y)

        self.assertAlmostEqual(self.body_on_x_axis.position.x, b2_pos_x)
        self.assertAlmostEqual(self.body_on_x_axis.position.y, b2_pos_y)
        self.assertAlmostEqual(self.body_on_x_axis.velocity.x, b2_vel_x)
        self.assertAlmostEqual(self.body_on_x_axis.velocity.y, b2_vel_y)

if __name__ == '__main__':
    unittest.main()
