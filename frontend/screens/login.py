import requests
from kivy.utils import get_color_from_hex
# from kivymd.uix.screen import MDScreen
# from kivymd.uix.textfield import MDTextField
# from kivymd.uix.button import MDRectangleFlatButton
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from utils.components import username_input,password_input
class LoginScreen(Screen):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def on_login(self):
        login_value = self.ids.login.text
        password_value = self.ids.password.text
        print(f"Login: {login_value}, Password: {password_value}")
        url = "http://127.0.0.1:5000/auth/login"  # modifie l'URL selon ton serveur

        # Préparer les données à envoyer
        data = {
            "username": login_value,
            "password": password_value
        }

        try:
            response = requests.post(url, json=data)
            print(response.json())
            data=response.json()[0]
            print(data)
            if response.status_code == 200:
                if data.get("role")=="production":
                    self.manager.current = "dashboard_screen"
                elif data.get("role")=="userManager":
                    self.manager.current = "adduser_screen"
                print("Connexion réussie")
                print("Tokens :", data.get("token"))
            else:
                print("Échec de la connexion :", response.json().get("message"))
        except requests.exceptions.RequestException as e:
            print("Erreur de connexion au serveur :", e)