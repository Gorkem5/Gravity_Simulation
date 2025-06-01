import streamlit as st
import requests # To make API calls
import time # For periodic refresh
import matplotlib.pyplot as plt
import os # For environment variable
# import numpy as np # If needed for more complex drawing later


# FastAPI backend URL, configurable via environment variable
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(layout="wide", page_title="2D Gravity Simulation")

st.title("🪐 2D Gravity Simulation")
st.markdown("Control and observe a 2D gravity simulation running via a FastAPI backend.")

# --- Session State Initialization ---
# Initialize session state variables if they don't exist to prevent errors on first run
# or after a hard refresh. These values serve as defaults until the API syncs.
if 'is_paused' not in st.session_state: # Tracks the simulation's pause state
    st.session_state.is_paused = True
if 'num_bodies' not in st.session_state: # Number of celestial bodies in the simulation
    st.session_state.num_bodies = 0
if 'current_g' not in st.session_state: # Current gravitational constant
    st.session_state.current_g = 100.0 # Default G, should ideally match SimulationManager's default
if 'current_dt' not in st.session_state: # Current time step for the simulation physics
    st.session_state.current_dt = 0.01  # Default dt, should ideally match SimulationManager's default
if 'auto_refresh' not in st.session_state: # Controls the auto-refreshing of the simulation view
    st.session_state.auto_refresh = True
if 'initial_load_done' not in st.session_state: # Flag to ensure initial API fetch happens only once
    st.session_state.initial_load_done = False
if 'error_message' not in st.session_state: # Stores API error messages for display
    st.session_state.error_message = ""

# Plot view controls session state initialization
if 'plot_xmin' not in st.session_state: st.session_state.plot_xmin = 0
if 'plot_xmax' not in st.session_state: st.session_state.plot_xmax = 800
if 'plot_ymin' not in st.session_state: st.session_state.plot_ymin = 0
if 'plot_ymax' not in st.session_state: st.session_state.plot_ymax = 600


# --- API Helper Functions ---
def fetch_simulation_status():
    """
    Fetches the current simulation status from the API.
    Updates relevant session state variables (is_paused, num_bodies, current_g, current_dt).
    This function is crucial for keeping the UI synchronized with the backend state.
    It tries to be careful not to overwrite user slider inputs unless explicitly synced.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/simulation/status")
        response.raise_for_status()
        status = response.json()

        # Always update pause state and number of bodies from backend
        st.session_state.is_paused = status.get('is_paused', st.session_state.is_paused)
        st.session_state.num_bodies = status.get('num_bodies', st.session_state.num_bodies)

        # Update G and dt from status. If sliders are present, their values might be
        # temporarily different until "Apply & Sync" is pressed. This reflects backend state.
        st.session_state.current_g = status.get('gravitational_constant', st.session_state.current_g)
        st.session_state.current_dt = status.get('time_step', st.session_state.current_dt)

        # Update slider widgets themselves if they exist, to reflect the fetched state.
        # This makes the UI consistent with the actual backend parameters.
        if 'gravity_slider_widget' in st.session_state:
             st.session_state.gravity_slider_widget = st.session_state.current_g
        if 'timestep_slider_widget' in st.session_state:
             st.session_state.timestep_slider_widget = st.session_state.current_dt

        st.session_state.error_message = ""
        return status
    except requests.exceptions.RequestException as e:
        st.session_state.error_message = f"API Error (Status): {e}"
        return None

def fetch_bodies_data():
    """Fetches celestial body data from the API for rendering."""
    try:
        response = requests.get(f"{API_BASE_URL}/simulation/bodies")
        response.raise_for_status()
        st.session_state.error_message = "" # Clear error on successful fetch
        return response.json()
    except requests.exceptions.RequestException as e:
        st.session_state.error_message = f"API Error (Bodies): {e}"
        return [] # Return empty list on error to prevent render failures

def draw_simulation(bodies_data, placeholder):
    """
    Draws the simulation state using Matplotlib.
    Uses plot limits from session state which are configurable via sidebar inputs.
    """
    fig, ax = plt.subplots(figsize=(10, 7.5)) # Adjust figsize as needed for wide layout

    # Use plot limits from session state
    ax.set_xlim(st.session_state.plot_xmin, st.session_state.plot_xmax)
    ax.set_ylim(st.session_state.plot_ymin, st.session_state.plot_ymax)
    ax.set_aspect('equal', adjustable='box')
    ax.set_facecolor('black') # Dark theme for the simulation view

    for body in bodies_data:
        x, y = body['position']['x'], body['position']['y']
        color_api = body['color']
        # Convert RGB[0-255] to Matplotlib's float [0-1] format
        plot_color = [c/255.0 for c in color_api] if isinstance(color_api, (list, tuple)) and len(color_api) == 3 else 'grey'

        trail_data = body.get('trail', [])
        if len(trail_data) > 1:
            trail_x = [p['x'] for p in trail_data]
            trail_y = [p['y'] for p in trail_data]
            ax.plot(trail_x, trail_y, color=plot_color, linewidth=0.7, alpha=0.6) # Trail style

        circle_radius = body['radius']
        # Ensure a minimum visible radius if actual radius is very small relative to plot scale
        # This calculation might need adjustment based on typical zoom levels.
        min_pixel_radius_equiv = (st.session_state.plot_xmax - st.session_state.plot_xmin) * 0.005
        display_radius = max(circle_radius, min_pixel_radius_equiv)

        circle = plt.Circle((x, y), display_radius, color=plot_color, alpha=0.9)
        ax.add_artist(circle)

        # Optional: Display body ID text (can be performance intensive for many bodies)
        # ax.text(x, y + display_radius + 5, body.get('id', ''), color='white', fontsize=6, ha='center', va='bottom')

    ax.grid(False) # No grid lines for a cleaner look
    ax.set_xticks([]) # No axis numbers/ticks
    ax.set_yticks([])

    placeholder.pyplot(fig, clear_figure=True) # clear_figure=True is important for animation updates
    plt.close(fig) # Close the figure to free up memory


# --- Initial state fetch on first actual script run ---
if not st.session_state.initial_load_done:
    status = fetch_simulation_status() # This updates session_state with backend values
    if status:
        st.toast("Successfully connected to API and fetched initial simulation status.", icon="✅")
    else:
        st.error(f"Initial API connection failed. Using default values. Error: {st.session_state.error_message}")
    st.session_state.initial_load_done = True


# --- Main Area for Simulation View ---
st.header("Simulation View")
if st.session_state.error_message and "Initial API connection failed" not in st.session_state.error_message:
    # Display persistent API errors (not initial load) as a toast
    st.toast(f"API Warning: {st.session_state.error_message}", icon="⚠️")

simulation_placeholder = st.empty()
if not st.session_state.auto_refresh: # If auto-refresh is off, draw once on script rerun
    current_bodies_data = fetch_bodies_data()
    draw_simulation(current_bodies_data, simulation_placeholder)
else:
    simulation_placeholder.markdown("_Simulation will appear here (auto-refreshing)... Ensure backend is running._")


# --- Sidebar Controls ---
st.sidebar.header("Controls")

if st.sidebar.button("🔄 Start/Reset Simulation"):
    try:
        # Use current G and dt from session state, which are bound to sliders
        start_payload = {
            "gravitational_constant": st.session_state.current_g,
            "time_step": st.session_state.current_dt
        }
        response = requests.post(f"{API_BASE_URL}/simulation/start_reset", json=start_payload)
        response.raise_for_status()
        new_status = response.json()
        # Update session state from API response
        st.session_state.is_paused = new_status['is_paused']
        st.session_state.num_bodies = new_status['num_bodies']
        st.session_state.current_g = new_status['gravitational_constant'] # Sync G
        st.session_state.current_dt = new_status['time_step']             # Sync dt
        st.session_state.error_message = "" # Clear any old error
        st.success("Simulation (Re)started!")
    except requests.exceptions.RequestException as e:
        st.session_state.error_message = f"API Error (Start/Reset): {e}"
    st.experimental_rerun() # Rerun to update UI, including sliders if G/dt changed

# Pause/Resume buttons use unique keys to help Streamlit manage state if layout changes slightly
pause_resume_key_suffix = "paused" if st.session_state.is_paused else "running"
if st.session_state.is_paused:
    if st.sidebar.button("▶️ Resume", key=f"resume_btn_{pause_resume_key_suffix}"):
        try:
            response = requests.post(f"{API_BASE_URL}/simulation/resume")
            response.raise_for_status()
            st.session_state.is_paused = False; st.session_state.error_message = ""
            st.success("Simulation Resumed.")
        except requests.exceptions.RequestException as e:
            st.session_state.error_message = f"API Error (Resume): {e}"
        st.experimental_rerun()
else:
    if st.sidebar.button("⏸️ Pause", key=f"pause_btn_{pause_resume_key_suffix}"):
        try:
            response = requests.post(f"{API_BASE_URL}/simulation/pause")
            response.raise_for_status()
            st.session_state.is_paused = True; st.session_state.error_message = ""
            st.success("Simulation Paused.")
        except requests.exceptions.RequestException as e:
            st.session_state.error_message = f"API Error (Pause): {e}"
        st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Parameters")

# Sliders for G and dt. Their values are stored in session_state via their keys.
# `value` is set from `st.session_state` to ensure consistency after API updates.
g_value_slider = st.sidebar.slider(
    "Gravitational Constant (G)",
    min_value=0.0, max_value=1000.0,
    value=st.session_state.current_g,
    step=10.0, key='gravity_slider_widget' # This key links the slider to session_state
)
dt_value_slider = st.sidebar.slider(
    "Time Step (dt)", min_value=0.001, max_value=0.1,
    value=st.session_state.current_dt,
    step=0.001, format="%.3f", key='timestep_slider_widget'
)

if st.sidebar.button("Apply & Sync Parameters"):
    try:
        # Use values directly from slider widgets for the API call
        payload = {"gravitational_constant": g_value_slider, "time_step": dt_value_slider}
        response = requests.put(f"{API_BASE_URL}/simulation/parameters", json=payload)
        response.raise_for_status()
        new_status = response.json()
        # Update session state from the authoritative API response
        st.session_state.current_g = new_status['gravitational_constant']
        st.session_state.current_dt = new_status['time_step']
        st.session_state.is_paused = new_status['is_paused']
        st.session_state.num_bodies = new_status['num_bodies']
        st.session_state.error_message = ""
        st.success("Parameters Updated & Synced with Backend!")
    except requests.exceptions.RequestException as e:
        st.session_state.error_message = f"API Error (Update Params): {e}"
    st.experimental_rerun() # Rerun to reflect updated values

# Update current_g and current_dt in session state if sliders are changed by user.
# This makes "Start/Reset Simulation" use the latest slider values without needing "Apply & Sync" first.
st.session_state.current_g = g_value_slider
st.session_state.current_dt = dt_value_slider


# --- Plot View Controls ---
st.sidebar.markdown("---")
st.sidebar.subheader("Plot View Controls")

# Number inputs for plot limits, values are stored in session_state via their keys.
st.session_state.plot_xmin = st.sidebar.number_input("Plot X Min", value=st.session_state.plot_xmin, key="plot_xmin_input", format="%d")
st.session_state.plot_xmax = st.sidebar.number_input("Plot X Max", value=st.session_state.plot_xmax, key="plot_xmax_input", format="%d")
st.session_state.plot_ymin = st.sidebar.number_input("Plot Y Min", value=st.session_state.plot_ymin, key="plot_ymin_input", format="%d")
st.session_state.plot_ymax = st.sidebar.number_input("Plot Y Max", value=st.session_state.plot_ymax, key="plot_ymax_input", format="%d")


# --- Add New Body Section ---
st.sidebar.markdown("---")
st.sidebar.subheader("Add New Celestial Body")

new_body_id = st.sidebar.text_input("ID (unique string)", value="new_planet", key="new_body_id_input") # Changed key
new_body_mass = st.sidebar.number_input("Mass", min_value=0.01, value=10.0, step=1.0, key="new_body_mass_input", format="%.2f")
new_body_radius = st.sidebar.number_input("Radius", min_value=0.1, value=5.0, step=0.5, key="new_body_radius_input", format="%.1f")

st.sidebar.markdown("###### Initial Position (x, y)")
new_body_pos_x = st.sidebar.number_input("Position X", value=float(st.session_state.plot_xmin + (st.session_state.plot_xmax - st.session_state.plot_xmin)*0.25), step=10.0, key="new_body_pos_x_input", format="%.1f")
new_body_pos_y = st.sidebar.number_input("Position Y", value=float(st.session_state.plot_ymin + (st.session_state.plot_ymax - st.session_state.plot_ymin)*0.5), step=10.0, key="new_body_pos_y_input", format="%.1f")

st.sidebar.markdown("###### Initial Velocity (vx, vy)")
new_body_vel_x = st.sidebar.number_input("Velocity X", value=0.0, step=0.1, format="%.1f", key="new_body_vel_x_input")
new_body_vel_y = st.sidebar.number_input("Velocity Y", value=0.0, step=0.1, format="%.1f", key="new_body_vel_y_input")

new_body_color_hex = st.sidebar.color_picker("Color", value="#00FF00", key="new_body_color_picker_input")

def hex_to_rgb(hex_color_str: str) -> tuple[int, int, int]:
    """Converts a hex color string (e.g., #RRGGBB) to an RGB tuple."""
    hex_color = hex_color_str.lstrip('#')
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # Handle short hex format e.g. #RGB -> #RRGGBB
    if len(hex_color) == 3:
        return tuple(int(hex_color[i]*2, 16) for i in (0,1,2))
    raise ValueError("Invalid hex color format. Expected #RRGGBB or #RGB.")

if st.sidebar.button("Add Body to Simulation", key="add_body_button"):
    if not new_body_id: # Use the variable that holds the input value
        st.sidebar.error("Body ID cannot be empty.")
    else:
        try:
            rgb_color = hex_to_rgb(new_body_color_hex)
            payload = {
                "id": new_body_id, "mass": new_body_mass,
                "position": {"x": new_body_pos_x, "y": new_body_pos_y},
                "velocity": {"x": new_body_vel_x, "y": new_body_vel_y},
                "radius": new_body_radius, "color": rgb_color
            }
            response = requests.post(f"{API_BASE_URL}/simulation/bodies", json=payload)

            if response.status_code == 409: # Conflict for duplicate ID
                 st.sidebar.error(f"Error: {response.json().get('detail', 'Duplicate body ID')}")
            elif response.status_code == 422: # Validation error (from Pydantic or explicit check)
                st.sidebar.error(f"Validation Error from API: {response.json().get('detail', 'Invalid data')}")
            else:
                response.raise_for_status() # Raise for other HTTP errors (500, 403, etc.)
                st.sidebar.success(f"Body '{new_body_id}' added!")
                fetch_simulation_status() # Update num_bodies etc.
                st.session_state.error_message = "" # Clear previous errors
        except requests.exceptions.RequestException as e:
            st.session_state.error_message = f"API Error (Add Body): {e}"
            st.sidebar.error(st.session_state.error_message) # Show error in sidebar
        except ValueError as e: # For hex_to_rgb errors or other local value errors
            st.sidebar.error(f"Input Error: {str(e)}")
    st.experimental_rerun() # Rerun to reflect changes or show error messages


# --- Simulation Info Display ---
st.sidebar.markdown("---")
st.sidebar.subheader("Simulation Info")
st.sidebar.write(f"Status: {'Paused' if st.session_state.is_paused else 'Running'}")
st.sidebar.write(f"Bodies: {st.session_state.num_bodies}")
st.sidebar.write(f"G: {st.session_state.current_g:.1f}") # Display G from session state
st.sidebar.write(f"dt: {st.session_state.current_dt:.3f}") # Display dt from session state

st.sidebar.markdown("---")
# Checkbox for auto-refresh control. Its state is stored in st.session_state.auto_refresh.
st.sidebar.checkbox("Auto-refresh View", value=st.session_state.auto_refresh, key="auto_refresh_checkbox")
# Update session_state.auto_refresh directly from the checkbox state
st.session_state.auto_refresh = st.session_state.auto_refresh_checkbox


if st.sidebar.button("🔄 Refresh Status/View Manually"):
    fetch_simulation_status() # Update session state from API
    if not st.session_state.auto_refresh: # If auto-refresh is off, manual refresh should also redraw bodies
        current_bodies_data = fetch_bodies_data()
        draw_simulation(current_bodies_data, simulation_placeholder)
    st.experimental_rerun() # Rerun to reflect changes in the UI

# --- Auto-refresh loop ---
REFRESH_INTERVAL_SECONDS = 0.1 # Approx 10 FPS, adjust as needed for performance/smoothness

if st.session_state.auto_refresh:
    # This part of the script is reached when auto_refresh is True.
    # It will fetch data, draw, sleep, and then rerun the script.

    # Fetch current simulation status (updates session_state for G, dt, pause, num_bodies)
    fetch_simulation_status()

    bodies = fetch_bodies_data() # Fetch current body data for drawing
    if bodies or not st.session_state.error_message : # Draw if bodies exist or no critical error message
        draw_simulation(bodies, simulation_placeholder)
    elif st.session_state.error_message: # If there's an error message (e.g. API not reachable)
         simulation_placeholder.warning(f"Cannot draw simulation: {st.session_state.error_message}")

    time.sleep(REFRESH_INTERVAL_SECONDS) # Wait for the interval

    # Check again in case auto_refresh was turned off during the sleep by user interaction
    if st.session_state.auto_refresh:
        try:
            st.experimental_rerun() # Trigger a rerun to create the loop
        except Exception as e:
            # This can happen if Streamlit server is stopped or tab closed while waiting for rerun
            print(f"Error during auto-refresh rerun: {e}")
            st.session_state.auto_refresh = False # Stop loop if rerun fails to prevent tight error loops
    else:
        # If auto_refresh was disabled (e.g., by checkbox during the sleep), rerun once
        # to ensure the UI correctly reflects the "auto_refresh off" state and clears any loading messages.
        st.experimental_rerun()

# Display any persistent error messages as a toast at the end of the script run
if st.session_state.error_message and "Initial API connection failed" not in st.session_state.error_message:
    st.toast(f"{st.session_state.error_message}", icon="⚠️")
    st.session_state.error_message = "" # Clear the message after showing it once


if __name__ == '__main__':
    # To run this Streamlit app:
    # 1. Ensure FastAPI backend is running: `uvicorn src.api.main_api:app --reload --port 8000`
    # 2. Run Streamlit app: `streamlit run src/frontend/app.py`
    pass
