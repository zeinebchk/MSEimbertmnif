import requests
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from frontend.Client import make_request
from frontend.SessionManager import SessionManager
from frontend.customSpinnerOption import CustomSpinnerOption


class RoleManagementScreen(Screen):
    show_modification = BooleanProperty(False)
    def __init__(self, **kwargs):
        session = SessionManager.get_instance()
        super().__init__(**kwargs)
        self.roles=[]
        self.modeles=[]
    def addRole(self):
        role = self.ids.input_role.text.strip()
        print(role)
        if not role:
            self.show_popup("attention","veuillez introduire un nom de role valide")
            return
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
        self.loadModels()
        self.ids.chaine_id.text=str(self.roles[-1]["id"])
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
            str_roles=[r["id"] for r in self.roles]
            self.ids.chaine_id.values=str_roles
        else:
            print("Erreur lors du chargement des utilisateurs :", response)

    def loadModels(self):
        response = make_request("get", "/manage_chaine_roles/get_all_models")
        if response.json()[1] == 200:
            print(response.json())
            data=response.json()[0].get("modeles")
            self.modeles=[model["nom_modele"] for model in data]
            self.ids.model_id.values=self.modeles
        else:
            print("Erreur lors du chargement des models :", response)

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
    def supprimer_chaine(self):
        chaine=self.ids.input_role.text
        if not chaine:
            self.show_popup("veuillez introduire une chaine valide")
            return
        try:
            data = {
                "id": chaine
            }
            response = make_request("delete", "/manage_chaine_roles/deletechaine", json=data)

            if response.json()[1] == 200:

                self.show_popup("Succées", "✅ chaine supprimé avec succès !")
                self.loadRoles()
            elif response.json()[1] == 409:
                self.show_popup("Attention ", " role n'existe pas  !")
                return
        except Exception as e:
            self.show_popup("Erreur", f"Erreur lors de la suppression : {str(e)}")
            print(f"❌ Exception levée : {str(e)}")

    def enregistrer(self):
        chaine=self.ids.chaine_id.text
        model=self.ids.model_id.text
        data={
            "modele": model,
            "chaine": chaine,
            "listeRegimeHoraire": [
                {
                    "regime": 42,
                    "joursSemaine": {
                        "horaireLundi": self.ids.input_heure_lundi_42.text,
                        "nbPaireLundi": self.ids.input_lundi_42.text,
                        "horaireMardi": self.ids.input_heure_mardi_42.text,
                        "nbPaireMardi": self.ids.input_mardi_42.text,
                        "horaireMercredi": self.ids.input_heure_mercredi_42.text,
                        "nbPaireMercredi": self.ids.input_mercredi_42.text,
                        "horaireJeudi": self.ids.input_heure_jeudi_42.text,
                        "nbPaireJeudi": self.ids.input_jeudi_42.text,
                        "horaireVendredi": self.ids.input_heure_vendredi_42.text,
                        "nbPaireVendredi": self.ids.input_vendredi_42.text,
                        "horaireSamedi": self.ids.input_heure_samedi_42.text,
                        "nbPaireSamedi": self.ids.input_samedi_42.text
                    }
                },
                {
                    "regime": 48,
                    "joursSemaine": {
                        "horaireLundi":self.ids.input_heure_lundi_48.text ,
                        "nbPaireLundi": self.ids.input_lundi_48.text,
                        "horaireMardi":self.ids.input_heure_mardi_48.text ,
                        "nbPaireMardi": self.ids.input_mardi_48.text,
                        "horaireMercredi": self.ids.input_heure_mercredi_48.text ,
                        "nbPaireMercredi": self.ids.input_mercredi_48.text,
                        "horaireJeudi": self.ids.input_heure_jeudi_48.text ,
                        "nbPaireJeudi": self.ids.input_jeudi_48.text,
                        "horaireVendredi": self.ids.input_heure_vendredi_48.text ,
                        "nbPaireVendredi": self.ids.input_vendredi_48.text,
                        "horaireSamedi": self.ids.input_heure_samedi_48.text ,
                        "nbPaireSamedi": self.ids.input_samedi_48.text
                    }
                }

            ]
        }
        response = make_request("post", "/manage_chaine_roles/addOrUpdatePlanification", json=data)

        if response.json()[1] == 201:

            self.show_popup("Succées", "✅ planification ajouté avec succès !")
            self.loadRoles()
        elif response.json()[1] == 409:
            self.show_popup("Attention ", " role existe deja !")

    def get_plan_by_modelAndChaine(self,chaine,modele):
        print("get plan aaaaa")
        data = {
            "chaine": chaine,
            "modele": modele
        }
        response = make_request("get", "/manage_chaine_roles/getPlanBymodelChaine", json=data)
        if response.json()[1] == 200:
            print(response.json()[0])
            data = response.json()[0].get("plan")
            if data:
                for plan in data:
                    if plan.get("regimeHoraire") == 42:
                        self.ids.input_heure_lundi_42.text = str(plan.get("horaireLundi"))
                        self.ids.input_lundi_42.text = str(plan.get("nbPaireLundi"))
                        self.ids.input_heure_mardi_42.text = str(plan.get("horaireMardi"))
                        self.ids.input_mardi_42.text = str(plan.get("nbPaireMardi"))
                        self.ids.input_heure_mercredi_42.text = str(plan.get("horaireMercredi"))
                        self.ids.input_mercredi_42.text = str(plan.get("nbPaireMercredi"))
                        self.ids.input_heure_jeudi_42.text = str(plan.get("horaireJeudi"))
                        self.ids.input_jeudi_42.text = str(plan.get("nbPaireJeudi"))
                        self.ids.input_heure_vendredi_42.text = str(plan.get("horaireVendredi"))
                        self.ids.input_vendredi_42.text = str(plan.get("nbPaireVendredi"))
                        self.ids.input_heure_samedi_42.text = str(plan.get("horaireSamedi"))
                        self.ids.input_samedi_42.text = str(plan.get("nbPaireSamedi"))
                    if plan.get("regimeHoraire") == 48:
                        self.ids.input_heure_lundi_48.text = str(plan.get("horaireLundi"))
                        self.ids.input_lundi_48.text = str(plan.get("nbPaireLundi"))
                        self.ids.input_heure_mardi_48.text = str(plan.get("horaireMardi"))
                        self.ids.input_mardi_48.text = str(plan.get("nbPaireMardi"))
                        self.ids.input_heure_mercredi_48.text = str(plan.get("horaireMercredi"))
                        self.ids.input_mercredi_48.text = str(plan.get("nbPaireMercredi"))
                        self.ids.input_heure_jeudi_48.text = str(plan.get("horaireJeudi"))
                        self.ids.input_jeudi_48.text = str(plan.get("nbPaireJeudi"))
                        self.ids.input_heure_vendredi_48.text = str(plan.get("horaireVendredi"))
                        self.ids.input_vendredi_48.text = str(plan.get("nbPaireVendredi"))
                        self.ids.input_heure_samedi_48.text = str(plan.get("horaireSamedi"))
                        self.ids.input_samedi_48.text = str(plan.get("nbPaireSamedi"))
            else:
                print("je suis dans else")
                self.ids.input_heure_lundi_42.text="7"
                self.ids.input_lundi_42.text=""
                self.ids.input_heure_mardi_42.text="7"
                self.ids.input_mardi_42.text=""
                self.ids.input_heure_mercredi_42.text ="7"
                self.ids.input_mercredi_42.text =""
                self.ids.input_heure_jeudi_42.text="7"
                self.ids.input_jeudi_42.text=""
                self.ids.input_heure_vendredi_42.text ="7"
                self.ids.input_vendredi_42.text =""
                self.ids.input_heure_samedi_42.text ="7"
                self.ids.input_samedi_42.text =""
                self.ids.input_heure_lundi_48.text="8.5"
                self.ids.input_lundi_48.text=""
                self.ids.input_heure_mardi_48.text="8.5"
                self.ids.input_mardi_48.text=""
                self.ids.input_heure_mercredi_48.text  ="8.5"
                self.ids.input_mercredi_48.text  =""
                self.ids.input_heure_jeudi_48.text="8.5"
                self.ids.input_jeudi_48.text=""
                self.ids.input_heure_vendredi_48.text ="8.5"
                self.ids.input_vendredi_48.text =""
                self.ids.input_heure_samedi_48.text ="8.5"
                self.ids.input_samedi_48.text =""

    def on_model_select(self,text):
        print(text)
        chaine = self.ids.chaine_id.text
        print(chaine)
        str_roles=[r["id"] for r in self.roles]
        if chaine in str_roles and text in self.modeles:
            print("truuuuuuuuuue")
            self.get_plan_by_modelAndChaine(chaine,text)

    def on_chaine_select(self,text):
        modele=self.ids.model_id.text
        str_roles = [r["id"] for r in self.roles]
        if text in str_roles and modele in self.modeles:
            print("aaaaaaaaaaaaaaa")
            self.get_plan_by_modelAndChaine(text, modele)
