import logging
import os
import sys
import threading

from app import create_app
import threading
import sys

app = create_app()

if __name__ == "__main__":
    # Determine environment settings
    flask_env = os.getenv("FLASK_ENV", "production").lower()
    debug_mode = flask_env == "development"

    # Configure logging based on debug mode
    log_level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(level=log_level)
    logging.getLogger("werkzeug").setLevel(log_level)

    # Initialize a threading lock for debugpy to avoid multiple instances
    debugpy_lock = threading.Lock()

    # Enable Debugpy for remote debugging in debug mode
    if debug_mode:
        try:
            import debugpy
            debug_port = int(os.getenv("DEBUG_PORT", 5678))

            with debugpy_lock:
                if not hasattr(debugpy, "_initialized") or not debugpy._initialized:
                    debugpy.listen(("0.0.0.0", debug_port))
                    debugpy._initialized = True
                    print(f"Debugpy is listening on port {debug_port}")
        except Exception as e:
            print(f"Failed to initialize debugpy on port {debug_port}: {e}")
            sys.exit(1)  # Exit the app to avoid retrying

    # Run Flask development server in debug mode, or display production usage
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", 5001))

    if debug_mode:
        print(f"Starting Flask app in debug mode on {host}:{port}")
        # file deepcode ignore RunWithDebugTrue: <We are running in debug deliberately>
        app.run(host=host, port=port, debug=True, use_reloader=False)
    else:
        print("This application is configured for production. Use Gunicorn to run.")
