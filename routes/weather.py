from flask import Blueprint, render_template, request
import requests
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime

load_dotenv()

weather_bp = Blueprint("weather", __name__)

OPENWEATHER_API = os.getenv("OPENWEATHER_API")
OPENCAGE_API = os.getenv("OPENCAGE_API")


@weather_bp.route("/weather", methods=["GET", "POST"])
def weather():

    weather_data = None
    forecast_data = []
    error = None

    if request.method == "POST":

        city = request.form.get("city", "").strip()

        if not city:
            error = "Please enter a city name."

        else:

            geo_url = (
                f"https://api.opencagedata.com/geocode/v1/json?"
                f"q={city}&key={OPENCAGE_API}"
            )

            geo_response = requests.get(geo_url, timeout=10).json()

            if geo_response["results"]:

                lat = geo_response["results"][0]["geometry"]["lat"]
                lon = geo_response["results"][0]["geometry"]["lng"]

                weather_url = (
                    f"https://api.openweathermap.org/data/2.5/weather?"
                    f"lat={lat}&lon={lon}"
                    f"&appid={OPENWEATHER_API}"
                    f"&units=metric"
                )
                forecast_url = (
                    f"https://api.openweathermap.org/data/2.5/forecast?"
                    f"lat={lat}&lon={lon}"
                    f"&appid={OPENWEATHER_API}"
                    f"&units=metric"
                )

                forecast_response = requests.get(
                    forecast_url,
                    timeout=10
                ).json()

                response = requests.get(weather_url, timeout=10).json()
                
                if response.get("cod") == 200:

                    weather_data = {
                        "city": response["name"],
                        "country": response["sys"]["country"],
                        "temperature": response["main"]["temp"],
                        "feels_like": response["main"]["feels_like"],
                        "humidity": response["main"]["humidity"],
                        "pressure": response["main"]["pressure"],
                        "wind": response["wind"]["speed"],
                        "condition": response["weather"][0]["main"],
                        "description": response["weather"][0]["description"].title(),
                        "icon": response["weather"][0]["icon"],
                        "sunrise": response["sys"]["sunrise"],
                        "sunset": response["sys"]["sunset"],
                        "visibility": response["visibility"] / 1000,
                    }

                    if forecast_response.get("cod") == "200":

                        today = datetime.now().strftime("%Y-%m-%d")

                        used_dates = set()

                        for item in forecast_response["list"]:

                            forecast_date = datetime.strptime(
                                item["dt_txt"],
                                "%Y-%m-%d %H:%M:%S"
                            ).date()

                            # Use only the 12 PM forecast for each day
                            if "12:00:00" not in item["dt_txt"]:
                                continue

                            if forecast_date in used_dates:
                                continue

                            used_dates.add(forecast_date)

                            forecast_data.append({

                                "day": forecast_date.strftime("%a"),

                                "temp": round(item["main"]["temp"]),

                                "icon": item["weather"][0]["icon"],

                                "description": item["weather"][0]["main"]

                            })

                            if len(forecast_data) == 5:
                                break
                    with sqlite3.connect("database/farming.db") as conn:

                        cursor = conn.cursor()

                        print(weather_data)
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print("Saving weather at:", current_time)
                        cursor.execute("""
                        INSERT INTO weather_history
                        (
                            city,
                            temperature,
                            humidity,
                            description,
                            created_at
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """, (
                            city.title(),
                            weather_data["temperature"],
                            weather_data["humidity"],
                            weather_data["description"],
                            current_time
                        ))

                        conn.commit()

                else:
                    error = "Weather data not found."

            else:
                error = "City not found."

                    
        
    return render_template(

    "weather.html",

    weather=weather_data,

    forecast=forecast_data,

    error=error,

)
