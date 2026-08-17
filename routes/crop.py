from flask import Blueprint, render_template, request
from services.crop_service import predict_crop
from utils.crop_info import CROP_INFO
import sqlite3
from datetime import datetime

crop_bp = Blueprint("crop", __name__)


@crop_bp.route("/crop")
def crop():
    return render_template("crop.html")


@crop_bp.route("/predict", methods=["POST"])
def predict():

    try:
    

        N = float(request.form["N"])
        P = float(request.form["P"])
        K = float(request.form["K"])
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        ph = float(request.form["ph"])
        rainfall = float(request.form["rainfall"])

        prediction, confidence = predict_crop(
            N,
            P,
            K,
            temperature,
            humidity,
            ph,
            rainfall,
        )

        info = CROP_INFO.get(prediction.lower(), {})
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect("database/farming.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO crop_history
        (
            nitrogen,
            phosphorus,
            potassium,
            temperature,
            humidity,
            ph,
            rainfall,
            recommendation,
            confidence,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,(
                N,
                P,
                K,
                temperature,
                humidity,
                ph,
                rainfall,
                prediction,
                confidence,
                current_time
            )
        )

        conn.commit()
        conn.close()

        return render_template(
            "crop.html",
            prediction=prediction,
            confidence=confidence,
            info=info
        )

    except Exception:

        return render_template(
            "crop.html",
            error="Something went wrong. Please check your inputs and try again."
        )