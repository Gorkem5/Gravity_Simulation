"""
Handles user input for the simulation.
"""
import pygame
import random
from typing import TYPE_CHECKING

from src.domain.vector2d import Vector2D
from src.domain.celestial_body import CelestialBody

if TYPE_CHECKING:
    from .simulation_service import SimulationService # Forward reference for type hinting

class InputHandler:
    """
    Processes Pygame events and translates them into simulation commands.
    """
    def __init__(self):
        """
        Initializes the InputHandler.
        """
        pass # No specific initialization needed for now

    def handle_input(self, simulation_service: 'SimulationService', event: pygame.event.Event) -> None:
        """
        Handles a single Pygame event and updates the simulation service accordingly.

        Args:
            simulation_service: The main simulation service instance.
            event: The Pygame event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                new_body = CelestialBody(
                    mass=5.0, # Fixed mass for now
                    position=Vector2D(float(mouse_pos[0]), float(mouse_pos[1])),
                    velocity=Vector2D(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)), # Small random initial velocity
                    radius=8.0, # Fixed radius
                    color=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                )
                simulation_service.simulation.add_body(new_body)
                print(f"Added new body at {mouse_pos} with mass {new_body.mass}, vel {new_body.velocity}")

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # This will be linked to simulation_service.simulation.paused
                # which needs to be created in GravitySimulation class.
                if hasattr(simulation_service.simulation, 'paused'):
                    simulation_service.simulation.paused = not simulation_service.simulation.paused
                    action = "paused" if simulation_service.simulation.paused else "resumed"
                    print(f"Simulation {action}. G: {simulation_service.simulation.gravitational_constant:.1f}, TimeStep: {simulation_service.time_step:.3f}")
                else:
                    print("Error: simulation.paused attribute not found.")

            elif event.key == pygame.K_UP:
                simulation_service.simulation.gravitational_constant += 10.0
                print(f"G set to: {simulation_service.simulation.gravitational_constant:.1f}")

            elif event.key == pygame.K_DOWN:
                new_g = simulation_service.simulation.gravitational_constant - 10.0
                simulation_service.simulation.gravitational_constant = max(0.0, new_g) # Prevent negative G
                print(f"G set to: {simulation_service.simulation.gravitational_constant:.1f}")

            elif event.key == pygame.K_LEFT:
                new_time_step = simulation_service.time_step - 0.005
                # Prevent time step from becoming too small or zero
                simulation_service.time_step = max(0.001, new_time_step)
                if hasattr(simulation_service.simulation, 'time_step_display'):
                    simulation_service.simulation.time_step_display = simulation_service.time_step
                print(f"Time step set to: {simulation_service.time_step:.3f}")

            elif event.key == pygame.K_RIGHT:
                simulation_service.time_step += 0.005
                if hasattr(simulation_service.simulation, 'time_step_display'):
                    simulation_service.simulation.time_step_display = simulation_service.time_step
                print(f"Time step set to: {simulation_service.time_step:.3f}")
