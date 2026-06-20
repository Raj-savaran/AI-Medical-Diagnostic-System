from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

model = load_model("models/xray_model.keras")

def predict_xray(img_path):

    img = image.load_img(
        img_path,
        color_mode="grayscale",
        target_size=(28,28)
    )

    img = image.img_to_array(img)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    pred = float(model.predict(img, verbose=0)[0][0])

    if pred > 0.5:
        disease = "Positive"
        confidence = pred * 100
    else:
        disease = "Negative"
        confidence = (1 - pred) * 100

    return disease, confidence