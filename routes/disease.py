from flask import Blueprint,render_template,request
from werkzeug.utils import secure_filename
import os
import sqlite3
from services.disease_service import predict_disease
from utils.disease_info import DISEASE_INFO
from datetime import datetime

disease_bp = Blueprint("disease",__name__)


@disease_bp.route("/disease")
def disease():

    return render_template("disease.html")


@disease_bp.route("/predict_disease",methods=["POST"])
def disease_prediction():

    try:

        file=request.files.get("leaf_image")

        if file is None or file.filename=="":

            return render_template(
                "disease.html",
                error="Please upload a leaf image."
            )

        os.makedirs("static/uploads",exist_ok=True)

        filename=secure_filename(file.filename)

        save_path=os.path.join("static","uploads",filename)

        file.save(save_path)

        image_path="uploads/"+filename

        disease,confidence=predict_disease(save_path)
        print("Disease from service:", repr(disease))
        print("Available key:", repr(list(DISEASE_INFO.keys())))
        confidence = float(confidence)
        display_name = disease
    
        with sqlite3.connect("database/farming.db") as conn:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO disease_history
            (
                image_name,
                disease,
                confidence,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """, (
                    filename,
                    disease,
                    confidence,
                    current_time
                )
            )

            conn.commit()


        disease_info=DISEASE_INFO.get(
            display_name,
            {
                "description":"Information not available.",
                "symptoms":[],
                "treatment":[],
                "prevention":[],
                "fertilizer":"N/A",
                "water":"N/A",
                "severity":"Unknown"
            }
        )
        return render_template(
            "disease.html",
            disease_prediction=display_name,
            disease_confidence=round(confidence, 2),
            disease_info=disease_info,                
            image_path=image_path
        )

    except Exception as e:

        raise e