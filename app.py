import dash
import mqtt_client
from config import APP_TITLE, APP_HOST, APP_PORT
from layout import create_main_layout
from callbacks import register_callbacks

# Start MQTT client background loop
mqtt_client.start_background_loop()

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = APP_TITLE

# Set app layout
app.layout = create_main_layout()

# Register all callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=False, host=APP_HOST, port=APP_PORT)
