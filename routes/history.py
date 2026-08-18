from flask import Blueprint, render_template, redirect, url_for, request
import sqlite3
from datetime import datetime

history_bp = Blueprint("history", __name__)


@history_bp.route("/history")
def history():

    # ======================================
    # GET FILTER VALUES
    # ======================================

    search = request.args.get("search", "").strip().lower()
    prediction_type = request.args.get("type", "all")
    selected_date = request.args.get("date", "")

    history_data = []

    with sqlite3.connect("database/farming.db") as conn:

        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # ======================================
        # CROP HISTORY
        # ======================================

        cursor.execute("""
            SELECT
                id,
                recommendation,
                temperature,
                humidity,
                rainfall,
                NULL AS confidence,
                created_at
            FROM crop_history
        """)

        crop_rows = cursor.fetchall()

        for row in crop_rows:

            history_data.append({

                "type": "Crop Recommendation",

                "icon": "🌾",

                "id": row["id"],

                "title": row["recommendation"],

                "subtitle":
                    f"Temp: {row['temperature']}°C | "
                    f"Humidity: {row['humidity']}% | "
                    f"Rainfall: {row['rainfall']} mm",

               "confidence": (
                    f"{row['confidence']:.2f}%"
                    if row["confidence"] is not None
                    else "-"
                ),
               "raw_date": row["created_at"],

                "date": datetime.strptime(
                    row["created_at"],
                    "%Y-%m-%d %H:%M:%S"
                ).strftime("%d %b %Y • %I:%M %p"),

                "color": "success"

            })

        # ======================================
        # DISEASE HISTORY
        # ======================================

        cursor.execute("""
            SELECT
                id,
                image_name,
                disease,
                confidence,
                created_at
            FROM disease_history
        """)

        disease_rows = cursor.fetchall()

        for row in disease_rows:

            history_data.append({

                "type": "Disease Detection",

                "icon": "🍃",

                "id": row["id"],

                "title": row["disease"],

                "subtitle": row["image_name"],

                "confidence": f"{row['confidence']}%",

                "raw_date": row["created_at"],

                "date": datetime.strptime(
                    row["created_at"],
                    "%Y-%m-%d %H:%M:%S"
                ).strftime("%d %b %Y • %I:%M %p"),

                "color": "danger"

            })

        # ======================================
        # WEATHER HISTORY
        # ======================================

        cursor.execute("""
            SELECT
                id,
                city,
                temperature,
                humidity,
                description,
                created_at
            FROM weather_history
        """)

        weather_rows = cursor.fetchall()

        for row in weather_rows:

            history_data.append({

                "type": "Weather Forecast",

                "icon": "🌦",

                "id": row["id"],

                "title": row["city"],

                "subtitle": f"{row['temperature']}°C • {row['description']}",

                "confidence": f"{row['humidity']}%",

                "raw_date": row["created_at"],

                "date": datetime.strptime(
                    row["created_at"],
                    "%Y-%m-%d %H:%M:%S"
                ).strftime("%d %b %Y • %I:%M %p"),

                "color": "primary"

            })

    # ======================================
    # SEARCH + FILTER
    # ======================================

    filtered_history = []

    for item in history_data:

        # ---------- Search ----------
        if search:

            search_text = (
                item["title"] + " " +
                item["subtitle"] + " " +
                item["type"]
            ).lower()

            if search not in search_text:
                continue

        # ---------- Type ----------

        if prediction_type == "crop" and item["type"] != "Crop Recommendation":
            continue

        if prediction_type == "disease" and item["type"] != "Disease Detection":
            continue

        if prediction_type == "weather" and item["type"] != "Weather Forecast":
            continue

        # ---------- Date ----------

        if selected_date:

            try:

                record_date = datetime.strptime(
                    item["raw_date"],
                    "%Y-%m-%d %H:%M:%S"
                ).strftime("%Y-%m-%d")

                if record_date != selected_date:
                    continue

            except:
                continue

        filtered_history.append(item)

    # ======================================
    # SORT LATEST FIRST
    # ======================================

    filtered_history.sort(

        key=lambda x: datetime.strptime(
            x["raw_date"],
            "%Y-%m-%d %H:%M:%S"
        ),

        reverse=True

    )

    # ======================================
    # RENDER PAGE
    # ======================================

    return render_template(

        "history.html",

        history_data=filtered_history,

        total_predictions=len(filtered_history),

        crop_count=sum(
            1 for x in filtered_history
            if x["type"] == "Crop Recommendation"
        ),

        disease_count=sum(
            1 for x in filtered_history
            if x["type"] == "Disease Detection"
        ),

        weather_count=sum(
            1 for x in filtered_history
            if x["type"] == "Weather Forecast"
        )

    )


# ======================================
# DELETE HISTORY
# ======================================

@history_bp.route("/delete_history/<history_type>/<int:record_id>")
def delete_history(history_type, record_id):

    with sqlite3.connect("database/farming.db") as conn:

        cursor = conn.cursor()

        if history_type == "crop":

            cursor.execute(
                "DELETE FROM crop_history WHERE id=?",
                (record_id,)
            )

        elif history_type == "disease":

            cursor.execute(
                "DELETE FROM disease_history WHERE id=?",
                (record_id,)
            )

        elif history_type == "weather":

            cursor.execute(
                "DELETE FROM weather_history WHERE id=?",
                (record_id,)
            )

        conn.commit()

    return redirect(url_for("history.history"))