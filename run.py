from main import create_app
from config import Development, Production
import os

# Determie the environment
flask_env = os.getenv('FLASK_ENV', 'development')

# Set the configuration based on the environment
if flask_env == 'development':
    config = Development
elif flask_env == 'production':
    config = Production
else:
    raise ValueError(f"Invalid FLASK_ENV value: {flask_env}. Expected 'development' or 'production'.")

# Initialise the app here
app = create_app(config)

# Run the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)