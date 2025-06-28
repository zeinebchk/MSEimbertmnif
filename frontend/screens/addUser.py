from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import Screen
from frontend.Client import make_request
LabelBase.register(name="EmojiFont", fn_regular=r"D:\seguiemj.ttf")

Window.size = (600, 750)

class AddUserScreen(Screen):

    def on_enter(self):
        roles=self.loadRoles()
        self.ids.role_utilisateur.values=roles
    def loadRoles(self):
        values=["production","gestion des utilisateurs","control"]
        print("loadUsers")
        response = make_request("get", "/manage_chaine_roles/getAllRoles")
        if response.status_code == 200:
            print(response.json())
            data = response.json()[0].get("roles")
            for role in data:
                values.append(role["id"])
            print("roles",values)
            return values
        else:
            print("Erreur lors du chargement des utilisateurs :", response)
    def ajouter_ouvrier(self):
        firstName = self.ids.nom_ouvrier.text.strip()
        lastName = self.ids.prenom_ouvrier.text.strip()
        matricule = self.ids.matricule_ouvrier.text.strip()
        # if firstName == "" or lastName == "" or matricule == "":
        #     self.show_popup("attention","veuiller remplir tous les champs")
        #     return
        if firstName and lastName and matricule:
            try:
                data = {
                    "MATR": matricule,
                    "NOM": firstName,
                    "PRENOM": lastName,
                }
                response = make_request("post", "/manage_users/addWorker", json=data)

                if response.json()[1] == 200:
                    self.ids.message.text = "✅ Ouvrier ajouté avec succès !"
                    self.ids.nom_ouvrier.text = ""
                    self.ids.prenom_ouvrier.text = ""
                    self.ids.matricule_ouvrier.text = ""
                    self.show_popup("Succées", "✅ Utilisateur ajouté avec succès !")
                elif response.json()[1] == 409:
                    self.show_popup("Attention ", " Utilisateur existe deja !")

            except Exception as e:
                self.ids.message.text = f"❌ Erreur : {str(e)}"
        else:
            self.ids.message.text = "⚠️ Remplis tous les champs pour l'ouvrier."

    def ajouter_utilisateur(self):
        username = self.ids.nom_utilisateur.text.strip()
        password = self.ids.motdepasse_utilisateur.text.strip()
        role = self.ids.role_utilisateur.text.strip()
        print(role)
        if not username:
            self.ids.username_error.text = "Veuillez entrer un nom d'utilisateur"
        else:
            self.ids.username_error.text = ""

        if not password:
            self.ids.password_error.text = "Veuillez entrer un mot de passe pour l'utilisateur"
        else:
            self.ids.password_error.text = ""
        if role == "Sélectionner un rôle":
            self.ids.message.text = "Veuillez selectionner un role"
        else:
            self.ids.message.text = ""

        if username and password and role!="Sélectionner un rôle":
            try:
                data={
                    "username":username,
                    "password":password,
                    "role":role,
                    "authorized":1,
                }
                response=make_request("post","/manage_users/addUser",json=data)

                if response.json()[1] == 200:
                    self.ids.message.text = "✅ Utilisateur ajouté avec succès !"
                    self.ids.nom_utilisateur.text = ""
                    self.ids.motdepasse_utilisateur.text = ""
                    self.show_popup("Succées","✅ Utilisateur ajouté avec succès !")
                elif response.json()[1] == 409:
                    self.show_popup("Attention "," Utilisateur existe deja !")
            except Exception as e:
                self.show_popup("Erreur", f"Erreur lors de l'ajout : {str(e)}")
                print(f"❌ Exception levée : {str(e)}")

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
    def root_to_listUsers(self):
        self.manager.current = "list_users_screen"