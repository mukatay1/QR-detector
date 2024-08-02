import joblib
import cv2
from pyzbar import pyzbar
from training import decode_qr
import os

# Загрузка обученной модели и векторизатора
clf = joblib.load('../qr_code_classifier.pkl')
vectorizer = joblib.load('../tfidf_vectorizer.pkl')

def predict_qr(image_path):
    qr_contents = decode_qr(image_path)
    if qr_contents:
        content = qr_contents[0]
        X_new = vectorizer.transform([content])
        prediction = clf.predict(X_new)
        return prediction[0]
    else:
        return 'No QR code found'

new_image_folder = 'C:\\Users\\Huntkey\\Desktop\\diploma\\dataTEST'  # Путь к папке с новыми изображениями

results = []
for image_file in os.listdir(new_image_folder):
    image_path = os.path.join(new_image_folder, image_file)
    label = predict_qr(image_path)
    results.append({'image': image_file, 'label': label})

for result in results:
    print(f"Image: {result['image']} - Label: {result['label']}")
