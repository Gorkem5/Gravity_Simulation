import asyncio
import logging # Added logging
from .simulation_manager import SimulationManager

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# This interval controls how often the simulation state is advanced in real-time.
# It's different from the simulation's internal 'time_step' which dictates the physics accuracy.
# 0.05 seconds = 20 updates per real-time second.
simulation_update_interval_seconds: float = 0.05

# Flag to signal the background task to stop
_simulation_task_should_stop: bool = False
_simulation_task_handle: asyncio.Task = None


async def _run_simulation_update_loop():
    """
    Continuously updates the simulation state in the background.
    This loop runs independently of API requests.
    """
    global _simulation_task_should_stop
    sim_manager = SimulationManager() # Get the singleton instance
    simulation = sim_manager.get_simulation_instance()

    logger.info("Background simulation update loop starting...")
    while not _simulation_task_should_stop:
        if not simulation.paused:
            # The simulation's own time_step_display is used for the physics update
            # This value can be changed via API or other means.
            simulation.update(simulation.time_step_display)

        try:
            # Wait for the next update interval, allowing other asyncio tasks to run.
            await asyncio.sleep(simulation_update_interval_seconds)
        except asyncio.CancelledError:
            # Handle task cancellation if the event loop is shutting down abruptly
            logger.info("Background simulation update loop cancelled.")
            _simulation_task_should_stop = True # Ensure loop terminates
            break # Exit loop immediately
        except Exception as e: # Catch other potential errors in the loop
            logger.error(f"Error in simulation update loop: {e}", exc_info=True)
            # Decide if the loop should stop or continue after an error
            # For now, let it continue, but this could be made configurable
            await asyncio.sleep(simulation_update_interval_seconds) # Prevent tight loop on continuous error


    logger.info("Background simulation update loop has finished.")

def start_simulation_loop_task() -> None:
    """Starts the simulation update loop as an asyncio task."""
    global _simulation_task_should_stop, _simulation_task_handle

    if _simulation_task_handle and not _simulation_task_handle.done():
        logger.info("Simulation update task already running.")
        return

    _simulation_task_should_stop = False
    # Get the current event loop. If running within FastAPI/Uvicorn, this should be the main loop.
    loop = asyncio.get_event_loop()
    _simulation_task_handle = loop.create_task(_run_simulation_update_loop())
    logger.info("Background simulation update task created.")

def stop_simulation_loop_task() -> None:
    """Signals the simulation update loop to stop."""
    global _simulation_task_should_stop, _simulation_task_handle

    if not _simulation_task_handle or _simulation_task_handle.done():
        logger.info("Simulation update task is not running or already stopped.")
        return

    _simulation_task_should_stop = True
    logger.info("Simulation update task stop signal sent. Waiting for completion...")
    # Note: Actual waiting for the task to finish (if needed beyond app shutdown)
    # would require `await _simulation_task_handle` in an async context,
    # or more complex cleanup logic. For FastAPI shutdown, signaling is usually enough.
    # The task will complete its current iteration and then exit.

# Example of how to manually test the loop (not for production use with FastAPI)
async def main_test():
    start_simulation_loop_task()
    try:
        # Keep the main_test running for a while to observe the loop
        for _ in range(10): # Let it run for a few intervals
            sim = SimulationManager().get_simulation_instance()
            logger.info(f"Test: Sim G={sim.gravitational_constant}, Bodies={len(sim.bodies)}, Paused={sim.paused}")
            if len(sim.bodies) > 0:
                 logger.info(f"Test: Body 0 pos=({sim.bodies[0].position.x:.2f}, {sim.bodies[0].position.y:.2f})")
            await asyncio.sleep(1) # Print status every second
    finally:
        stop_simulation_loop_task()
        # Give it a moment to stop if it was in the middle of an await asyncio.sleep
        await asyncio.sleep(simulation_update_interval_seconds + 0.1)

if __name__ == "__main__":
    # This allows running this file directly to test the async loop logic.
    # It's a good way to isolate and debug the background task.
    try:
        asyncio.run(main_test())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user.")
    finally:
        logger.info("Test finished.")
