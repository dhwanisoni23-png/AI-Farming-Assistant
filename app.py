from flask import Flask, render_template
from tensorflow.keras.models import load_model
from dotenv import load_dotenv
import os
import database.init_db
import requests

from routes.crop import crop_bp
from routes.disease import disease_bp
from routes.weather import weather_bp
from routes.chatbot import chatbot_bp
from routes.history import history_bp
from routes.dashboard import dashboard_bp
from routes.about import about_bp
from routes.contact import contact_bp

app = Flask(__name__)
# Register Blueprints
app.register_blueprint(crop_bp)
app.register_blueprint(disease_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(history_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(about_bp)
app.register_blueprint(contact_bp)

# Load environment variables
load_dotenv()

# API Keys
OPENCAGE_API = os.getenv("OPENCAGE_API") 
OPENWEATHER_API = os.getenv("OPENWEATHER_API")
app.secret_key = os.getenv("SECRET_KEY", "my_super_secret_key_123")


def get_coordinates(city):
    url = "https://api.opencagedata.com/geocode/v1/json"

    params = {
        "q": city,
        "key": OPENCAGE_API
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    data = response.json()

    if data["results"]:
        lat = data["results"][0]["geometry"]["lat"]
        lon = data["results"][0]["geometry"]["lng"]
        return lat, lon

    return None, None


def get_weather(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API,
        "units": "metric"
    }

    response = requests.get(url, params=params)

    return response.json()


# Load AI Model
disease_model = load_model("models/mobilenetv2_plant_disease_model.keras")


# Home Route
@app.route("/")
def home():
    return render_template("home.html")


   
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)