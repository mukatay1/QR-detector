from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from PIL import Image as PILImage
from kivy.uix.scrollview import ScrollView
import joblib
import os
import sys

# Загрузка обученной модели и векторизатора
clf = joblib.load('qr_code_classifier.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

def decode_qr(image_path):
    # Замена функции decode_qr на заглушку
    return ["sample QR code content"]

# Функция для предсказания метки по изображению QR-кода
def predict_qr(image_path):
    qr_contents = decode_qr(image_path)
    if qr_contents:
        content = qr_contents[0]
        X_new = vectorizer.transform([content])
        prediction = clf.predict(X_new)
        return prediction[0]
    else:
        return 'No QR code found'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        bg = Image(source='FrontApp/mainscreen.jpg', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(bg)

        btn = Button(
            text='Lets Go',
            background_color=(1, 1, 1, 0),
            color=(0x33 / 255.0, 0x33 / 255.0, 0x33 / 255.0, 1),
            font_name="Roboto-Bold",
            size_hint=(0.7, 0.07),
            pos_hint={'x': 0.15, 'y': 0.03}
        )
        btn.bind(on_press=self.goto_camera)

        with btn.canvas.before:
            Color(0x99 / 255.0, 0xDF / 255.0, 0xFB / 255.0, 1)
            self.rect = RoundedRectangle(radius=[10])

        btn.bind(pos=self.update_rect, size=self.update_rect)
        self.layout.add_widget(btn)
        self.add_widget(self.layout)

    def goto_camera(self, instance):
        self.manager.current = 'camera_screen'

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        self.camera = Camera(play=True, allow_stretch=True, keep_ratio=False)
        self.camera.size = Window.size
        self.camera.pos = (0, 0)
        self.add_widget(self.camera)

        # Нижняя панель навигации
        self.navbar_layout = FloatLayout(size_hint=(1, None), height=250, pos_hint={'x': 0, 'y': 0})
        self.nav_image = Image(source='FrontApp/navbar.png', allow_stretch=True, keep_ratio=False)
        self.navbar_layout.add_widget(self.nav_image)

        # Кнопки теперь невидимы, но функциональны
        self.btn_checker = Button(background_normal='', background_color=(0, 0, 0, 0), size_hint=(0.28, 0.5),
                                  pos_hint={'center_x': 0.2, 'center_y': 0.3})
        self.navbar_layout.add_widget(self.btn_checker)
        self.btn_history = Button(background_normal='', background_color=(0, 0, 0, 0), size_hint=(0.28, 0.5),
                                  pos_hint={'center_x': 0.8, 'center_y': 0.3})
        self.btn_history.bind(on_press=self.goto_history_screen)
        self.navbar_layout.add_widget(self.btn_history)

        # Кнопка для съемки фотографии
        self.btn_capture = Button(background_normal='', background_color=(0, 0, 0, 0), size_hint=(0.15, 0.45),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.6})
        self.btn_capture.bind(on_press=self.capture_photo)
        self.navbar_layout.add_widget(self.btn_capture)

        self.add_widget(self.navbar_layout)

    def goto_history_screen(self, instance):
        self.manager.current = 'history_screen'

    def on_window_resize(self, instance, width, height):
        self.camera.size = (width, height)
        self.navbar_layout.size = (width, 250)  # Обновление ширины и высоты навигационной панели
        self.nav_image.size = (width, 250)  # Обновление размеров изображения

    def capture_photo(self, instance):
        texture = self.camera.texture
        size = texture.size
        self.pil_image = PILImage.frombytes(mode='RGBA', size=size, data=texture.pixels)

        # Создание всплывающего окна для ввода имени фотографии
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text='Write a name of QR:'))

        self.photo_name_input = TextInput(multiline=False, size_hint_y=None, height=50)
        content.add_widget(self.photo_name_input)

        btn_save = Button(text='Save', size_hint_y=None, height=50)
        btn_save.bind(on_press=self.save_photo)
        content.add_widget(btn_save)

        self.popup = Popup(title='Save Photo', content=content, size_hint=(0.6, 0.3))
        self.popup.open()

    def save_photo(self, instance):
        photo_name = self.photo_name_input.text
        if photo_name:
            photo_path = f'{photo_name}.png'
            self.pil_image.save(photo_path)

            # Анализ фотографии
            label = predict_qr(photo_path)

            # Добавление фотографии и результата анализа в TrustedScreen
            self.manager.get_screen('trusted_screen').add_photo(photo_path, photo_name, label)
        self.popup.dismiss()

class ImageButton(ButtonBehavior, Image):
    pass

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        layout = FloatLayout()

        # Фон экрана
        bg = Image(source='FrontApp/background.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(bg)

        # Кнопка "Scam" с изображением
        btn_scam = ImageButton(
            source='FrontApp/scambutton.png',
            size_hint=(0.4, 0.2),
            pos_hint={'center_x': 0.5, 'top': 0.77}
        )
        btn_scam.bind(on_press=self.goto_scam_screen)
        layout.add_widget(btn_scam)

        # Кнопка "Normal" с изображением, переименованная в "Trusted"
        btn_trusted = ImageButton(
            source='FrontApp/trustedbutton.png',
            size_hint=(0.4, 0.2),
            pos_hint={'center_x': 0.5, 'top': 0.5}
        )
        btn_trusted.bind(on_press=self.goto_trusted_screen)
        layout.add_widget(btn_trusted)

        # Нижняя панель навигации
        navbar_layout = FloatLayout(size_hint=(1, None), height=250, pos_hint={'x': 0, 'y': 0})
        nav_image = Image(source='FrontApp/navbar2.png', allow_stretch=True, keep_ratio=False)
        navbar_layout.add_widget(nav_image)

        # Кнопка 'btn_checker', ведет на CameraScreen
        btn_checker = Button(background_normal='', background_color=(0, 0, 0, 0), size_hint=(0.28, 0.5),
                             pos_hint={'center_x': 0.2, 'center_y': 0.3})
        btn_checker.bind(on_press=self.goto_camera_screen)
        navbar_layout.add_widget(btn_checker)

        layout.add_widget(navbar_layout)
        self.add_widget(layout)

    def goto_camera_screen(self, instance):
        self.manager.current = 'camera_screen'

    def goto_trusted_screen(self, instance):
        self.manager.current = 'trusted_screen'

    def goto_scam_screen(self, instance):
        self.manager.current = 'scam_screen'

class TrustedScreen(Screen):
    def __init__(self, **kwargs):
        super(TrustedScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()

        # Фон для экрана Trusted
        bg = Image(source='FrontApp/background.jpg', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(bg)

        # Сетка для фотографий
        self.grid_layout = GridLayout(cols=3, spacing=10, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        self.scroll_view = ScrollView(size_hint=(1, 0.8), pos_hint={'x': 0, 'y': 0.2})
        self.scroll_view.add_widget(self.grid_layout)
        self.layout.add_widget(self.scroll_view)

        # Нижняя панель навигации
        navbar_layout = FloatLayout(size_hint=(1, None), height=250, pos_hint={'x': 0, 'y': 0})
        nav_image = Image(source='FrontApp/navbar2.png', allow_stretch=True, keep_ratio=False)
        navbar_layout.add_widget(nav_image)

        # Кнопка 'btn_checker', ведет на CameraScreen
        btn_checker = Button(background_normal='', background_color=(0, 0, 0, 0), size_hint=(0.28, 0.5),
                             pos_hint={'center_x': 0.2, 'center_y': 0.3})
        btn_checker.bind(on_press=self.goto_camera_screen)
        navbar_layout.add_widget(btn_checker)

        self.layout.add_widget(navbar_layout)
        self.add_widget(self.layout)

    def goto_camera_screen(self, instance):
        self.manager.current = 'camera_screen'

    def add_photo(self, photo_path, photo_name, label):
        photo_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=250)
        photo_image = Image(source=photo_path, size_hint_y=None, height=200)
        photo_label = Label(text=f"{photo_name}\n{label}", size_hint_y=None, height=50)

        photo_layout.add_widget(photo_image)
        photo_layout.add_widget(photo_label)

        self.grid_layout.add_widget(photo_layout)

class ScamScreen(Screen):
    def __init__(self, **kwargs):
        super(ScamScreen, self).__init__(**kwargs)
        layout = FloatLayout()

        # Фон для экрана Scam
        bg = Image(source='FrontApp/background.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(bg)

        # Нижняя панель навигации
        navbar_layout = FloatLayout(size_hint=(1, None), height=250, pos_hint={'x': 0, 'y': 0})
        nav_image = Image(source='FrontApp/navbar2.png', allow_stretch=True, keep_ratio=False)
        navbar_layout.add_widget(nav_image)

        # Кнопка 'btn_checker', ведет на CameraScreen
        btn_checker = Button(background_normal='', background_color=(0, 0, 0, 0), size_hint=(0.28, 0.5),
                             pos_hint={'center_x': 0.2, 'center_y': 0.3})
        btn_checker.bind(on_press=self.goto_camera_screen)
        navbar_layout.add_widget(btn_checker)

        layout.add_widget(navbar_layout)
        self.add_widget(layout)

    def goto_camera_screen(self, instance):
        self.manager.current = 'camera_screen'

class MainApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main_screen'))
        sm.add_widget(CameraScreen(name='camera_screen'))
        sm.add_widget(HistoryScreen(name='history_screen'))
        sm.add_widget(TrustedScreen(name='trusted_screen'))
        sm.add_widget(ScamScreen(name='scam_screen'))
        return sm

    def on_start(self):
        Window.size = (360, 800)  # Установка размера окна при запуске

if __name__ == '__main__':
    MainApp().run()
