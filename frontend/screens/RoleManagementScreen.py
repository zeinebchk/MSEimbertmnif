import requests
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from frontend.Client import make_request
from frontend.SessionManager import SessionManager


class RoleManagementScreen(Screen):
    show_modification = BooleanProperty(False)
    def __init__(self, **kwargs):
        session = SessionManager.get_instance()
        super().__init__(**kwargs)
        self.roles=[]

    def addRole(self):
        role = self.ids.input_role.text.strip()
        print(role)
        if not role:
            self.show_popup("attention","veuillez introduire un nom de role valide")
        try:
            data = {
               "id":role
            }
            response = make_request("post", "/manage_chaine_roles/addchaineOrRole", json=data)

            if response.json()[1] == 200:

                self.show_popup("Succées", "✅ role ajouté avec succès !")
                self.loadRoles()
            elif response.json()[1] == 409:
                self.show_popup("Attention ", " role existe deja !")
        except Exception as e:
            self.show_popup("Erreur", f"Erreur lors de l'ajout : {str(e)}")
            print(f"❌ Exception levée : {str(e)}")

    def on_enter(self):
        self.loadRoles()

    def display_roles(self,roles):

        self.ids.table_grid.clear_widgets()
        headers = ["ID"]
        for header in headers:
            self.ids.table_grid.add_widget(Label(
                text=header,
                bold=True,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_y=None,
                height=dp(35)
            ))
        for role in roles:
            self.ids.table_grid.add_widget(
                Label(text=str(role["id"]), size_hint_y=None, height=dp(30), color=(0, 0, 0, 1)))
    def loadRoles(self):
        response = make_request("get", "/manage_chaine_roles/getAllRoles")
        if response.status_code == 200:
            print(response.json())
            data=response.json()[0].get("roles")
            self.roles=data
            print(data)
            self.display_roles(self.roles)
        else:
            print("Erreur lors du chargement des utilisateurs :", response)


    def updateUser(self):
        id=self.ids.input_user.text
        username=self.ids.mod_username.text
        role=self.ids.mod_role.text
        password=self.ids.new_password.text
        if password=="":
            data={
                "id":id,
                "username":username,
                "role":role}
        else:
            data = {
                "id": id,
                "username": username,
                "role": role,
                "pwd": password}

        response=make_request("put","/manage_users/updateUser",json=data)
        if response.json()[1] == 201:
            self.show_popup("Succées","utilisateur modifié avec succées")
            self.ids.mod_username.text=""
            self.ids.mod_role.text="selectionner un role"
            self.ids.input_user.text=""
            self.loadUsers()
            return
        elif response.json()[1] == 401:
            self.show_popup("Attention","Vous n'etes pas autorisé pour faire cette fonction")
            return
        elif response.json()[1] == 404:
            self.show_popup("Attention", "utilisateur n'existe pas dans la base")
            return


    def afficher_detail_user(self):
        id=self.ids.input_role.text
        if id!="":
            self.show_modification=True
            data={"id":id}
            response=make_request("get","/",json=data)
            print(response)
            if response.json()[1] == 200:
                data=response.json()[0].get("user")
                self.ids.mod_username.text=data.get("username")
                self.ids.mod_role.text=data.get("role")
            elif response.json()[1] == 401:
                self.show_popup("Attention","Vous n'etes pas autorisé pour faire cette fonction")
                return
            elif response.json()[1] == 404:
                self.show_popup("Attention", "utilisateur n'existe pas dans la base")
                return

    def chercher_par_nom(self):
        search_text=self.ids.search_input.text
        print(search_text)
        for user in self.users:
            if user["username"] == search_text:
                self.users = [user]

                self.display_users(self.users)
        print("chercher par nom",self.users)

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
