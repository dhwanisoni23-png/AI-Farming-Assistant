from flask import Blueprint, render_template
import sqlite3

dashboard_bp = Blueprint("dashboard", __name__)
from datetime import datetime, timedelta

def get_overall_weekday_data(cursor, table_name):

    counts = [0] * 7

    cursor.execute(f"""
        SELECT
            CAST(strftime('%w', created_at) AS INTEGER),
            COUNT(*)
        FROM {table_name}
        GROUP BY strftime('%w', created_at)
    """)

    rows = cursor.fetchall()

    for weekday, count in rows:

        # SQLite:
        # 0 = Sunday
        # 1 = Monday
        # ...
        # 6 = Saturday

        if weekday == 0:
            counts[6] = count
        else:
            counts[weekday - 1] = count

    return counts
@dashboard_bp.route("/dashboard")
def dashboard():

    with sqlite3.connect("database/farming.db") as conn:

        cursor = conn.cursor()

        # ===========================
        # TODAY'S OVERVIEW
        # ===========================

        cursor.execute("""
        SELECT COUNT(*)
        FROM crop_history
        WHERE DATE(created_at) = DATE('now', 'localtime')
        """)
        today_crop_count = cursor.fetchone()[0]

        
        cursor.execute("""
        SELECT COUNT(*)
        FROM disease_history
        WHERE DATE(created_at) = DATE('now', 'localtime')
        """)
        today_disease_count = cursor.fetchone()[0]

        cursor.execute("""
        SELECT COUNT(*)
        FROM weather_history
        WHERE DATE(created_at) = DATE('now', 'localtime')
        """)
        today_weather_count = cursor.fetchone()[0]


        # ===========================
        # OVERALL STATISTICS
        # ===========================

        cursor.execute("SELECT COUNT(*) FROM crop_history")
        total_crop_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM disease_history")
        total_disease_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM weather_history")
        total_weather_count = cursor.fetchone()[0]


        crop_week_data = get_overall_weekday_data(cursor, "crop_history")
        disease_week_data = get_overall_weekday_data(cursor, "disease_history")
        weather_week_data = get_overall_weekday_data(cursor, "weather_history")
        # ===========================
        # RECENT ACTIVITIES
        # ===========================

        cursor.execute("""
        SELECT
            'crop' AS type,
            recommendation AS title,
            created_at
        FROM crop_history

        UNION ALL

        SELECT
            'disease',
            disease,
            created_at
        FROM disease_history

        UNION ALL

        SELECT
            'weather',
            city,
            created_at
        FROM weather_history

        ORDER BY created_at DESC
        LIMIT 2
        """)

        recent_activities = cursor.fetchall()

        formatted_activities = []

        for activity in recent_activities:

            activity_time = datetime.strptime(
                activity[2],
                "%Y-%m-%d %H:%M:%S"
            )

            diff = datetime.now() - activity_time

            if diff.days > 0:
                time_text = f"{diff.days} day ago" if diff.days == 1 else f"{diff.days} days ago"

            elif diff.seconds >= 3600:
                hrs = diff.seconds // 3600
                time_text = f"{hrs} hour ago" if hrs == 1 else f"{hrs} hours ago"

            elif diff.seconds >= 60:
                mins = diff.seconds // 60
                time_text = f"{mins} min ago"

            else:
                time_text = "Just now"

            formatted_activities.append({
                "type": activity[0],
                "title": activity[1],
                "time": time_text
            })

        recent_activities = formatted_activities

        return render_template(
            "dashboard.html",

            crop_week_data=crop_week_data,
            disease_week_data=disease_week_data,
            weather_week_data=weather_week_data,

            today_crop_count=today_crop_count,
            today_disease_count=today_disease_count,
            today_weather_count=today_weather_count,

            total_crop_count=total_crop_count,
            total_disease_count=total_disease_count,
            total_weather_count=total_weather_count,

            recent_activities=recent_activities
        )