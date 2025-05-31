import pygame
from src.domain.gravity_simulation import GravitySimulation
# CelestialBody is implicitly used via GravitySimulation.bodies, direct import not strictly needed unless type hinting individual bodies.
# from src.domain.celestial_body import CelestialBody

class PygameRenderer:
    """
    Handles rendering the gravity simulation using Pygame.
    """
    def __init__(self, screen_width: int, screen_height: int, screen_caption: str):
        """
        Initializes Pygame, sets up the screen, and defines basic colors.

        Args:
            screen_width: The width of the screen in pixels.
            screen_height: The height of the screen in pixels.
            screen_caption: The caption for the Pygame window.
        """
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(screen_caption)

        # Basic colors
        self.BLACK: tuple[int, int, int] = (0, 0, 0)
        self.WHITE: tuple[int, int, int] = (255, 255, 255)
        self.RED: tuple[int, int, int] = (255, 0, 0)
        self.GREEN: tuple[int, int, int] = (0, 255, 0)

        # Font for displaying text
        try:
            self.font = pygame.font.Font(None, 28) # Default system font, size 28
        except Exception as e:
            print(f"Could not load default font: {e}. Using fallback.")
            self.font = pygame.font.SysFont("arial", 24)


    def _render_text(self, text: str, position: tuple[int, int], color: tuple[int, int, int] = WHITE) -> None:
        """Helper to render text on the screen."""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, position)

    def render(self, simulation: GravitySimulation) -> None:
        """
        Renders the current state of the simulation.

        This involves:
        1. Filling the screen with a background color.
        2. Drawing each celestial body as a circle.
        3. Updating the display.

        Args:
            simulation: The GravitySimulation object containing the bodies to render.
        """
        self.screen.fill(self.BLACK)  # Fill screen with black background

        for body in simulation.bodies:
            # Pygame's y-axis is inverted if simulation's origin is bottom-left.
            # For now, assume simulation's (0,0) is top-left, matching Pygame.
            # If simulation y increases upwards, use: int(self.screen_height - body.position.y)
            pos_x = int(body.position.x)
            pos_y = int(body.position.y)

            # Ensure radius is at least 1 for visibility if it's too small (e.g. < 1)
            radius = max(1, int(body.radius))

            pygame.draw.circle(self.screen, body.color, (pos_x, pos_y), radius)

        # Display PAUSED message if simulation is paused
        if hasattr(simulation, 'paused') and simulation.paused:
            paused_text = "PAUSED (Press SPACE to resume)"
            # Calculate position for PAUSED text (e.g., center screen)
            text_surf = self.font.render(paused_text, True, self.RED)
            text_rect = text_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(text_surf, text_rect)

        # Display simulation parameters
        g_text = f"G: {simulation.gravitational_constant:.1f} (UP/DOWN to change)"
        ts_text = f"Time Step: {simulation.time_step_display:.3f} (LEFT/RIGHT to change)"
        bodies_text = f"Bodies: {len(simulation.bodies)}"

        self._render_text(g_text, (10, 10), self.GREEN)
        self._render_text(ts_text, (10, 35), self.GREEN)
        self._render_text(bodies_text, (10, 60), self.GREEN)
        self._render_text("SPACE: Pause/Resume", (10, 85), self.WHITE)
        self._render_text("LCLICK: Add Body", (10, 110), self.WHITE)


        # Draw trails first, then bodies on top
        for body in simulation.bodies:
            if hasattr(body, 'trail') and len(body.trail) > 1:
                # Make trail color slightly dimmer or different (optional)
                # trail_color = tuple(max(0, c - 50) for c in body.color) # Example: dimmer
                trail_color = body.color # For now, use body color

                # Convert trail Vector2D points to list of tuples for pygame.draw.lines
                trail_points = [(int(p.x), int(p.y)) for p in body.trail]
                pygame.draw.lines(self.screen, trail_color, False, trail_points, 1) # thickness 1

        # Draw bodies (re-iterating, or do this in the first loop if order doesn't matter much)
        for body in simulation.bodies:
            pos_x = int(body.position.x)
            pos_y = int(body.position.y)
            radius = max(1, int(body.radius))
            pygame.draw.circle(self.screen, body.color, (pos_x, pos_y), radius)


        pygame.display.flip()  # Update the full display

    def quit(self) -> None:
        """
        Quits Pygame.
        """
        pygame.quit()

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of the renderer.
        """
        return f"PygameRenderer(width={self.screen_width}, height={self.screen_height})"

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the renderer.
        """
        # pygame.display.get_caption() returns a tuple (title, icon_title)
        caption_info = pygame.display.get_caption() # In Pygame 2, this is just a string.
        caption_str = caption_info if isinstance(caption_info, str) else caption_info[0]

        return (f"PygameRenderer(screen_width={self.screen_width!r}, "
                f"screen_height={self.screen_height!r}, "
                f"caption='{caption_str}')")

# Minimal example for testing if run directly (optional, can be removed for production)
if __name__ == '__main__':
    # This block allows direct testing of the renderer.
    # For this to run, you'd need to ensure that the domain classes are accessible,
    # or use mock objects as shown previously.

    # Mock Vector2D for testing if not wanting to import the real one here
    class MockVector2D:
        def __init__(self, x, y):
            self.x = x
            self.y = y
        def __add__(self, other): return MockVector2D(self.x + other.x, self.y + other.y)
        def __sub__(self, other): return MockVector2D(self.x - other.x, self.y - other.y)
        def __mul__(self, scalar): return MockVector2D(self.x * scalar, self.y * scalar)
        def normalize(self): return MockVector2D(0,0) # Simplified
        def __repr__(self): return f"MockVector2D({self.x}, {self.y})"


    # Mock CelestialBody for testing
    class MockCelestialBody:
        def __init__(self, x, y, radius, color, mass=1, vel_x=0, vel_y=0):
            self.position = MockVector2D(x, y)
            self.velocity = MockVector2D(vel_x, vel_y)
            self.radius = radius
            self.color = color
            self.mass = mass
        def apply_force(self, force, time_step): pass # Simplified
        def update_position(self, time_step): pass # Simplified
        def __repr__(self): return f"MockCelestialBody({self.position}, r={self.radius})"


    # Mock GravitySimulation for testing
    class MockGravitySimulation:
        def __init__(self):
            self.bodies: list[MockCelestialBody] = []
            self.gravitational_constant = 6.674e-11 # Example value
            # Add some bodies for testing
            self.bodies.append(MockCelestialBody(100, 150, 20, (255, 0, 0)))  # Red
            self.bodies.append(MockCelestialBody(300, 200, 30, (0, 0, 255)))  # Blue
        def add_body(self, body): self.bodies.append(body)
        def update(self, time_step): pass # Simplified
        def __repr__(self): return f"MockGravitySimulation(bodies={len(self.bodies)})"


    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    CAPTION = "Pygame Renderer Test"

    renderer = PygameRenderer(SCREEN_WIDTH, SCREEN_HEIGHT, CAPTION)
    simulation_state = MockGravitySimulation()

    running = True
    clock = pygame.time.Clock()

    print("Starting Pygame test loop...")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        renderer.render(simulation_state)
        clock.tick(60) # Limit to 60 FPS

    print("Exiting Pygame test loop.")
    renderer.quit()
