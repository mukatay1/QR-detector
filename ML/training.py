import cv2
from pyzbar import pyzbar
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

def decode_qr(image_path):
    image = cv2.imread(image_path)
    qr_codes = pyzbar.decode(image)
    return [qr_code.data.decode('utf-8') for qr_code in qr_codes]

# Путь к папке с изображениями и файл с метками
image_folder = 'C:\\Users\\Huntkey\\Desktop\\diploma\\qrs'  # Путь к папке с изображениями
labels_file = 'C:\\Users\\Huntkey\\Desktop\\diploma\\mark.csv'  # Путь к CSV файлу с метками

labels_df = pd.read_csv(labels_file)

# Извлечение содержимого QR-кодов из изображений
data = []
for index, row in labels_df.iterrows():
    image_path = os.path.join(image_folder, row['image'])
    qr_contents = decode_qr(image_path)
    if qr_contents:
        data.append({'content': qr_contents[0], 'label': row['label']})

# Создание DataFrame с содержимым QR-кодов и метками
df = pd.DataFrame(data)

# Преобразование текстового содержимого QR-кодов в числовые признаки
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['content'])
y = df['label']

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Обучение модели
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Оценка модели
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))

# Сохранение модели и векторизатора
joblib.dump(clf, '../qr_code_classifier.pkl')
joblib.dump(vectorizer, '../tfidf_vectorizer.pkl')
