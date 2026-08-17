import os
import sqlite3

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)


contact_bp = Blueprint("contact", __name__)

DATABASE_PATH = "database/farming.db"


# ============================================================
# PUBLIC CONTACT PAGE
# ============================================================

@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        # Basic validation
        if not name or not email or not subject or not message:

            flash(
                "Please fill in all fields.",
                "error"
            )

            return redirect(
                url_for("contact.contact")
            )

        try:

            connection = sqlite3.connect(
                DATABASE_PATH
            )

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO feedback
                (name, email, subject, message)
                VALUES (?, ?, ?, ?)
            """, (
                name,
                email,
                subject,
                message
            ))

            connection.commit()
            connection.close()

            flash(
                "Thank you! Your feedback has been submitted successfully.",
                "success"
            )

        except sqlite3.Error as error:

            print("Database Error:", error)

            flash(
                "Something went wrong while submitting your feedback.",
                "error"
            )

        return redirect(
            url_for("contact.contact")
        )

    return render_template("contact.html")


# ============================================================
# PUBLIC STAR RATING
# ============================================================

@contact_bp.route("/contact/rating", methods=["POST"])
def submit_rating():

    rating = request.form.get(
        "rating",
        ""
    ).strip()

    try:

        rating = int(rating)

    except (ValueError, TypeError):

        flash(
            "Please select a valid rating.",
            "error"
        )

        return redirect(
            url_for("contact.contact")
        )

    # Rating must be between 1 and 5
    if rating < 1 or rating > 5:

        flash(
            "Please select a rating between 1 and 5.",
            "error"
        )

        return redirect(
            url_for("contact.contact")
        )

    try:

        connection = sqlite3.connect(
            DATABASE_PATH
        )

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO ratings (rating)
            VALUES (?)
        """, (rating,))

        connection.commit()
        connection.close()

        flash(
            "Thank you for rating AI Farming Assistant!",
            "success"
        )

    except sqlite3.Error as error:

        print("Database Error:", error)

        flash(
            "Something went wrong while saving your rating.",
            "error"
        )

    return redirect(
        url_for("contact.contact")
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@contact_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    # Already logged in
    if session.get("admin_authenticated"):

        return redirect(
            url_for("contact.admin_feedback")
        )

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        admin_password = os.getenv(
            "ADMIN_PASSWORD"
        )

        if admin_password and password == admin_password:

            session["admin_authenticated"] = True

            return redirect(
                url_for("contact.admin_feedback")
            )

        flash(
            "Incorrect password.",
            "error"
        )

    return render_template(
        "admin_login.html"
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@contact_bp.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin_authenticated",
        None
    )

    return redirect(
        url_for("contact.admin_login")
    )


# ============================================================
# ADMIN FEEDBACK DASHBOARD
# ============================================================

@contact_bp.route("/admin/feedback")
def admin_feedback():

    # 🔐 PROTECTION
    if not session.get("admin_authenticated"):

        return redirect(
            url_for("contact.admin_login")
        )


    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()


    # --------------------------------------------------------
    # ALL FEEDBACK
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            subject,
            message,
            datetime(created_at, '+5 hours', '+30 minutes') AS created_at
        FROM feedback
        ORDER BY id DESC
    """)

    feedback = cursor.fetchall()


    # --------------------------------------------------------
    # ALL RATINGS
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            rating,
            datetime(created_at, '+5 hours', '+30 minutes') AS created_at
        FROM ratings
        ORDER BY id DESC
    """)

    ratings = cursor.fetchall()


    # --------------------------------------------------------
    # TOTAL RATINGS
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM ratings
    """)

    total_ratings = cursor.fetchone()[0]


    # --------------------------------------------------------
    # AVERAGE RATING
    # --------------------------------------------------------

    cursor.execute("""
        SELECT AVG(rating)
        FROM ratings
    """)

    average_rating = cursor.fetchone()[0]

    if average_rating is None:

        average_rating = 0


    # --------------------------------------------------------
    # RATING DISTRIBUTION
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            rating,
            COUNT(*) AS count
        FROM ratings
        GROUP BY rating
        ORDER BY rating DESC
    """)

    rating_distribution = cursor.fetchall()


    connection.close()


    return render_template(
        "admin_feedback.html",
        feedback=feedback,
        ratings=ratings,
        total_ratings=total_ratings,
        average_rating=round(
            average_rating,
            1
        ),
        rating_distribution=rating_distribution
    )