from kivy.uix.screenmanager import Screen

from frontend.SessionManager import SessionManager


class ListUserScreen(Screen):
    def __init__(self, **kwargs):
        session = SessionManager.get_instance()
        super().__init__(**kwargs)
        self.loadUsers();
    def loadUsers(self):

    def chercher(self):
        session = SessionManager.get_instance()
        login_value = self.ids.login.text
        password_value = self.ids.password.text

        print(f"Login: {login_value}, Password: {password_value}")
        if not login_value:
            self.ids.login_error.text = "Veuillez entrer un nom d'utilisateur"
        else:
            self.ids.login_error.text = ""

        if not password_value:
            self.ids.password_error.text = "Veuillez entrer votre mot de passe"
        else:
            self.ids.password_error.text = ""
        if login_value != "" and password_value != "":
            url = "http://127.0.0.1:5000/auth/login"  # modifie l'URL selon ton serveur

            # Préparer les données à envoyer
            data = {
                "username": login_value,
                "password": password_value
            }

            try:
                response = requests.post(url, json=data)

                print("ffffff", response.json())

                print(data)
                if response.status_code == 200:
                    data = response.json()[0]
                    session.set_tokens(data.get("access_token"), data.get("refresh_token"))

                    if data.get("role") == "production":
                        self.manager.current = "dashboard_screen"
                    elif data.get("role") == "userManager":
                        self.manager.current = "adduser_screen"
                    elif data.get("role") == "Technicien picure2 🛠":
                        self.manager.current = "adduser_screen"
                else:
                    self.show_popup("Erreur de connexion", "login ou mot de passe est incorrect")
                    print("Échec de la connexion :", response.json().get("message"))
            except requests.exceptions.RequestException as e:
                self.show_popup("Erreur de connexion", "login ou mot de passe est incorrect")
                print("Erreur de connexion au serveur :", e)

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            size_hint=(0.6, 0.3),
            auto_dismiss=False
        )

        # Créer le contenu avec fond coloré
        content = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10),
        )

        # Ajouter un fond clair avec Canvas.before
        with content.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # couleur de fond très claire
            rect = Rectangle(pos=content.pos, size=content.size)

        # Mettre à jour la taille et la position du rectangle si le layout change
        def update_rect(instance, value):
            rect.pos = instance.pos
            rect.size = instance.size

        content.bind(pos=update_rect, size=update_rect)

        # Message en blanc
        label = Label(
            text=message,
            color=(0, 0, 0, 0.88),  # blanc
            font_size='16sp'
        )
        content.add_widget(label)

        # Bouton 'Fermer' en blanc
        btn = Button(
            text='Fermer',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.4, 0.7, 1, 1),  # bleu clair
            color=(1, 1, 1, 1),  # texte blanc
        )
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)

        popup.content = content
        popup.open()
    def root_to_addUser(self):
        self.manager.current = "adduser_screen"
