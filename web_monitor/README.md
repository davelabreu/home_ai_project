# Web Monitor Application

This `README.md` provides specific details about the `web_monitor` application, its architecture, and instructions for development and deployment.

## Architecture Summary

The `web_monitor` is a web application designed to monitor the Jetson device and other home AI components. It follows a client-server architecture:

*   **Backend (Flask):** Located in `app.py`, this is a Python Flask application that serves two primary purposes:
    *   **API Endpoints:** Provides RESTful APIs (e.g., `/api/network_status`, `/api/system_info`) to fetch real-time data from the Jetson device (CPU usage, memory, disk, network devices).
    *   **Frontend Serving:** Serves the built React frontend application (HTML, CSS, JavaScript assets) from the `frontend/dist` directory.
*   **Frontend (React/Vite with Shadcn UI):** Located in the `frontend/` directory, this is a modern single-page application built with React and Vite. It consumes the Flask backend's APIs to display data in a user-friendly dashboard. It utilizes Shadcn UI components, styled with Tailwind CSS, for a modern and responsive user interface.

## Project Structure

*   `app.py`: The main Flask backend application.
*   `frontend/`: Contains the React application source code and build configurations.
    *   `frontend/public/`: Static assets not processed by Vite.
    *   `frontend/src/`: React source code (components, hooks, main entry files).
    *   `frontend/dist/`: The compiled and optimized React application (generated after `npm run build`). This is served by the Flask backend.
*   `static/`: Placeholder for any Flask-served static files not part of the React build.
*   `templates/`: Placeholder for any Flask-served HTML templates not part of the React build (currently used to serve `index.html` from `frontend/dist`).
*   `requirements.txt`: Python dependencies for the Flask backend.
*   `.venv/`: Python virtual environment for the Flask backend.

## Getting Started

### 1. Backend Setup and Run

To run the Flask backend, you need Python 3 and its dependencies.

1.  **Navigate to the `web_monitor` directory:**
    ```bash
    cd web_monitor
    ```
2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Flask application:**
    ```bash
    python3 app.py
    ```
    The Flask app will typically run on `http://0.0.0.0:5000`. Keep this terminal running.

### 2. Frontend Development (Optional, for making changes to the UI)

To work on the React frontend, you'll need Node.js and npm (or yarn).

1.  **Navigate to the `frontend` directory:**
    ```bash
    cd web_monitor/frontend
    ```
2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
3.  **Start the development server:**
    ```bash
    npm run dev
    ```
    This will usually start a development server on a different port (e.g., `http://localhost:5173`). Changes will hot-reload.

### 3. Frontend Build (for deployment)

When you are ready to deploy the frontend changes, you need to build the React application.

1.  **Navigate to the `frontend` directory:**
    ```bash
    cd web_monitor/frontend
    ```
2.  **Build the application:**
    ```bash
    npm run build
    ```
    This will compile the React app into the `frontend/dist` directory. The Flask backend is configured to serve these static files.

## General Role Hand-off

*   **Backend Developer:** Responsible for `app.py`, API endpoint logic, data fetching from system, and Python dependencies.
*   **Frontend Developer:** Responsible for `frontend/` directory (React code, UI components, styling), consuming APIs, and frontend build process.
*   **DevOps/System Admin:** Responsible for ensuring Python and Node.js environments are set up, managing virtual environments, deployment, and monitoring.

## Contributing

Please adhere to the project's coding standards and conventions. Ensure your changes are well-tested and documented.

---
[Back to main project README](../README.md)
