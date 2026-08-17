from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

disease_model = load_model("models/mobilenetv2_plant_disease_model.keras")


CLASS_NAMES = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite",
    "Tomato__Target_Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus",
    "Tomato__Tomato_mosaic_virus",
    "Tomato_healthy"
]


def predict_disease(image_path):

    img = image.load_img(image_path, target_size=(224,224))

    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = disease_model.predict(img_array, verbose=0)

    predicted_index = np.argmax(prediction)

    predicted_class = CLASS_NAMES[predicted_index]

    DISPLAY_NAMES = {
        "Pepper__bell___Bacterial_spot": "Pepper Bell Bacterial Spot",
        "Pepper__bell___healthy": "Pepper Bell Healthy",
        "Potato___Early_blight": "Potato Early Blight",
        "Potato___Late_blight": "Potato Late Blight",
        "Potato___healthy": "Potato Healthy",
        "Tomato_Bacterial_spot": "Tomato Bacterial Spot",
        "Tomato_Early_blight": "Tomato Early Blight",
        "Tomato_Late_blight": "Tomato Late Blight",
        "Tomato_Leaf_Mold": "Tomato Leaf Mold",
        "Tomato_Septoria_leaf_spot": "Tomato Septoria Leaf Spot",
        "Tomato_Spider_mites_Two_spotted_spider_mite": "Tomato Spider Mites Two Spotted Spider Mite",
        "Tomato__Target_Spot": "Tomato Target Spot",
        "Tomato__Tomato_YellowLeaf__Curl_Virus": "Tomato Yellow Leaf Curl Virus",
        "Tomato__Tomato_mosaic_virus": "Tomato Mosaic Virus",
        "Tomato_healthy": "Tomato Healthy"
    }

    disease = DISPLAY_NAMES.get(predicted_class, predicted_class)

    # Calculate confidence correctly
    confidence = float(np.max(prediction) * 100)
    confidence = round(confidence, 2)

    return disease, confidence