import tensorflow as tf
import pickle
import numpy as np

model = tf.keras.models.load_model(
    "models/medical_model.h5"
)

with open("models/binarizer.pkl","rb") as f:
    mlb = pickle.load(f)

with open("models/labels.pkl","rb") as f:
    labels = pickle.load(f)


def predict_symptoms(symptoms):

    vector = mlb.transform([symptoms])

    pred = model.predict(vector)[0]

    idx = np.argmax(pred)

    disease = labels[idx]

    confidence = float(pred[idx] * 100)

    return disease, confidence