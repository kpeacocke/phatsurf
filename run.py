import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use the environment variable FLASK_DEBUG to toggle debug mode
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
