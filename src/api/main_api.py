from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field # Added Field
from typing import List, Optional

from .simulation_manager import SimulationManager
from .domain.celestial_body import CelestialBody # For type hinting complex objects if needed in future
from .domain.vector2d import Vector2D # For type hinting if needed

app = FastAPI(title="Gravity Simulation API")

# --- Pydantic Models ---

class Vector2DResponse(BaseModel):
    x: float
    y: float

class CelestialBodyResponse(BaseModel):
    id: str
    mass: float
    position: Vector2DResponse
    velocity: Vector2DResponse
    radius: float
    color: tuple[int, int, int]
    trail: List[Vector2DResponse] # List of recent positions

    class Config:
        from_attributes = True # Updated from orm_mode=True for Pydantic v2

class SimulationStatusResponse(BaseModel):
    is_paused: bool
    gravitational_constant: float
    time_step: float # This is time_step_display from simulation
    num_bodies: int
    # bodies: List[CelestialBodyResponse] # Consider adding list of bodies for more detailed status

class SimulationStartRequest(BaseModel):
    gravitational_constant: Optional[float] = None
    time_step: Optional[float] = None
    # initial_bodies: Optional[List[dict]] = None # For future extension

class SimulationParametersRequest(BaseModel):
    gravitational_constant: Optional[float] = Field(default=None, ge=0.0, description="Gravitational constant (G). Must be non-negative.")
    time_step: Optional[float] = Field(default=None, gt=0.0, description="Time step for simulation physics. Must be positive.")

class Vector2DRequest(BaseModel): # For nested position/velocity in AddBodyRequest
    x: float
    y: float

class AddBodyRequest(BaseModel):
    id: str
    mass: float
    position: Vector2DRequest  # Changed from pos_x, pos_y
    velocity: Vector2DRequest  # Changed from vel_x, vel_y
    radius: float
    color: tuple[int,int,int] = (200, 200, 200)


# --- API Endpoints ---

@app.get("/")
async def root():
    """
    Root endpoint for the API.
    Provides a welcome message.
    """
    return {"message": "Welcome to the Gravity Simulation API"}

@app.post("/simulation/start_reset", response_model=SimulationStatusResponse, tags=["Simulation Control"])
async def start_reset_simulation(request_data: Optional[SimulationStartRequest] = None):
    """
    Starts or resets the simulation.
    Optionally sets a new gravitational_constant and time_step.
    If no parameters are provided, it resets to the system's default G and time_step.
    Default bodies are re-initialized.
    """
    sim_manager = SimulationManager() # Get the singleton instance

    # Determine parameters for reset: use request data if provided, else current manager defaults.
    g_const = sim_manager.DEFAULT_G
    t_step = sim_manager.DEFAULT_TIME_STEP

    if request_data:
        g_const = request_data.gravitational_constant if request_data.gravitational_constant is not None else g_const
        t_step = request_data.time_step if request_data.time_step is not None else t_step

    sim_instance = sim_manager.reset_simulation(
        gravitational_constant=g_const,
        time_step=t_step
    )
    return SimulationStatusResponse(
        is_paused=sim_instance.paused,
        gravitational_constant=sim_instance.gravitational_constant,
        time_step=sim_instance.time_step_display,
        num_bodies=len(sim_instance.bodies)
    )

@app.post("/simulation/pause", response_model=SimulationStatusResponse, tags=["Simulation Control"])
async def pause_simulation():
    """
    Pauses the simulation.
    """
    sim_instance = SimulationManager().get_simulation_instance()
    sim_instance.paused = True
    return SimulationStatusResponse(
        is_paused=sim_instance.paused,
        gravitational_constant=sim_instance.gravitational_constant,
        time_step=sim_instance.time_step_display,
        num_bodies=len(sim_instance.bodies)
    )

@app.post("/simulation/resume", response_model=SimulationStatusResponse, tags=["Simulation Control"])
async def resume_simulation():
    """
    Resumes the simulation if it was paused.
    """
    sim_instance = SimulationManager().get_simulation_instance()
    sim_instance.paused = False
    return SimulationStatusResponse(
        is_paused=sim_instance.paused,
        gravitational_constant=sim_instance.gravitational_constant,
        time_step=sim_instance.time_step_display,
        num_bodies=len(sim_instance.bodies)
    )

@app.get("/simulation/status", response_model=SimulationStatusResponse, tags=["Simulation Status"])
async def get_simulation_status():
    """
    Retrieves the current status of the simulation.
    """
    sim_instance = SimulationManager().get_simulation_instance()
    return SimulationStatusResponse(
        is_paused=sim_instance.paused,
        gravitational_constant=sim_instance.gravitational_constant,
        time_step=sim_instance.time_step_display,
        num_bodies=len(sim_instance.bodies)
    )

@app.post("/simulation/step", response_model=SimulationStatusResponse, tags=["Simulation Control"])
async def step_simulation():
    """
    Advances the simulation by a single time step, even if paused.
    Useful for debugging or controlled progression.
    """
    sim_instance = SimulationManager().get_simulation_instance()
    original_paused_state = sim_instance.paused

    # Temporarily unpause to ensure the simulation can advance one step.
    sim_instance.paused = False
    # Use the simulation's own 'time_step_display' as the duration for this single step.
    # This ensures the step taken is consistent with what the user might expect from UI.
    sim_instance.update(sim_instance.time_step_display)

    # Restore the original paused state after the step.
    sim_instance.paused = original_paused_state

    return SimulationStatusResponse(
        is_paused=sim_instance.paused, # Return the current actual paused state
        gravitational_constant=sim_instance.gravitational_constant,
        time_step=sim_instance.time_step_display,
        num_bodies=len(sim_instance.bodies)
    )

@app.post("/simulation/bodies", response_model=CelestialBodyResponse, status_code=201, tags=["Body Management"])
async def add_simulation_body(body_request: AddBodyRequest):
    """
    Adds a new celestial body to the simulation.
    """
    sim_instance = SimulationManager().get_simulation_instance()

    # Check for ID collision (optional, but good practice)
    for existing_body in sim_instance.bodies:
        if existing_body.id == body_request.id:
            raise HTTPException(status_code=409, detail=f"Body with ID '{body_request.id}' already exists.")

    try:
        new_body = CelestialBody(
            id=body_request.id,
            mass=body_request.mass,
        position=Vector2D(body_request.position.x, body_request.position.y), # Adjusted access
        velocity=Vector2D(body_request.velocity.x, body_request.velocity.y), # Adjusted access
        radius=body_request.radius,
        color=body_request.color
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid body parameter: {str(e)}")

    sim_instance.add_body(new_body)

    # Convert to CelestialBodyResponse for the response
    # This assumes Vector2D can be directly used by Pydantic or has a compatible structure
    return CelestialBodyResponse(
        id=new_body.id,
        mass=new_body.mass,
        position=Vector2DResponse(x=new_body.position.x, y=new_body.position.y),
        velocity=Vector2DResponse(x=new_body.velocity.x, y=new_body.velocity.y),
        radius=new_body.radius,
        color=new_body.color,
        trail=[Vector2DResponse(x=p.x, y=p.y) for p in new_body.trail] # Ensure trail is also converted
    )

@app.get("/simulation/bodies", response_model=List[CelestialBodyResponse], tags=["Body Management"])
async def get_all_simulation_bodies():
    """
    Retrieves a list of all celestial bodies currently in the simulation.
    """
    sim_instance = SimulationManager().get_simulation_instance()
    response_bodies = []
    for body in sim_instance.bodies:
        response_bodies.append(CelestialBodyResponse(
            id=body.id,
            mass=body.mass,
            position=Vector2DResponse(x=body.position.x, y=body.position.y),
            velocity=Vector2DResponse(x=body.velocity.x, y=body.velocity.y),
            radius=body.radius,
            color=body.color,
            trail=[Vector2DResponse(x=p.x, y=p.y) for p in body.trail]
        ))
    return response_bodies

@app.put("/simulation/parameters", response_model=SimulationStatusResponse, tags=["Simulation Control"])
async def update_simulation_parameters(params: SimulationParametersRequest):
    """
    Updates simulation parameters like gravitational_constant and time_step.
    Only updates parameters that are provided in the request.
    """
    sim_instance = SimulationManager().get_simulation_instance()

    # Pydantic validation handles g>=0 and time_step > 0 via Field constraints
    if params.gravitational_constant is not None:
        sim_instance.gravitational_constant = params.gravitational_constant
        print(f"API: Set gravitational_constant to {sim_instance.gravitational_constant}")

    if params.time_step is not None:
        # This updates the value that is reported by /status and used by /step
        sim_instance.time_step_display = params.time_step
        print(f"API: Set time_step_display to {sim_instance.time_step_display}")

    return SimulationStatusResponse(
        is_paused=sim_instance.paused,
        gravitational_constant=sim_instance.gravitational_constant,
        time_step=sim_instance.time_step_display,
        num_bodies=len(sim_instance.bodies)
    )

# Example of how to run for local testing:
# uvicorn src.api.main_api:app --reload --port 8000
# (Assuming file is saved as src/api/main_api.py)

# --- FastAPI Lifecycle Events ---
# Import the task management functions
from . import tasks
import asyncio

@app.on_event("startup")
async def startup_event():
    """
    Event handler for application startup.
    Starts the background simulation update task.
    """
    print("Application startup: Initializing simulation loop.")
    tasks.start_simulation_loop_task()

@app.on_event("shutdown")
async def shutdown_event():
    """
    Event handler for application shutdown.
    Stops the background simulation update task.
    """
    print("Application shutdown: Signaling simulation loop to stop.")
    tasks.stop_simulation_loop_task()
    # Give the task a moment to finish its current iteration and exit cleanly.
    # The duration should ideally be slightly longer than simulation_update_interval_seconds.
    await asyncio.sleep(tasks.simulation_update_interval_seconds + 0.1)
    print("Application shutdown complete.")
