import joblib

model = joblib.load("models/crop_recommendation_model.pkl")


def predict_crop(N, P, K, temperature, humidity, ph, rainfall):

    features = [[N, P, K, temperature, humidity, ph, rainfall]]

    prediction = model.predict(features)[0]

    confidence = (
        max(model.predict_proba(features)[0]) * 100
    )

    return prediction, round(confidence, 2)