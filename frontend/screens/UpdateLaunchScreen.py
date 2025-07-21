from datetime import datetime

import numpy as np
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle
import pandas as pd
import os

from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from sqlalchemy import Selectable

from frontend.Client import make_request


class UpdateLaunchScreen(Screen):
    show_checkboxes = BooleanProperty(False)

    status_label = ObjectProperty()
    table_grid = ObjectProperty()
    table_scroll = ObjectProperty()
    header_scroll = ObjectProperty()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.of_chaines = []
        self.df = []
        self.selected_rows = []
        self.checks = []
        self.checksChainePicure=[]
        self.type_options = ["piqure", "montage", "coupe"]
        self.selected_types = set()
        self.dropdown = None
        self.old_chaines=[]
        self.row_checkboxes = []
        self.modeles=[]
        self.selected_rows = []
        self.selected_rows_indices = []
        self.is_selecting_all = False

    def on_parent(self, *args):
        # Synchronize horizontal scrolling between header_scroll and table_scroll
        if hasattr(self, 'table_scroll') and hasattr(self, 'header_scroll'):
            self.table_scroll.bind(scroll_x=self.header_scroll.setter('scroll_x'))
            self.header_scroll.bind(scroll_x=self.table_scroll.setter('scroll_x'))
    def on_enter(self):
        annee_actuelle = datetime.now().year
        aujourd_hui = datetime.today()

        # Obtenir le numéro de semaine
        numero_semaine = aujourd_hui.isocalendar().week
        self.loadModels()

        self.ids.year_id.text= str(annee_actuelle)
        self.ids.week_id.text= str(numero_semaine)
        self.ids.year_id.values = [str(i) for i in range(2025, annee_actuelle + 11)]
        self.ids.week_id.values = [f"{i:02}" for i in range(1, 53)]
        grid_checkbox=self.ids.type_chaine
        grid_checkbox.clear_widgets()
        self.display_roles()

    def loadofs(self,data):

        response = make_request("get", "/manage_ofs/getofsChaines",json=data)
        if response.status_code == 200:
            self.df = response.json()[0].get("ofs", [])
            print(self.df)
            if self.df:
                self.populate_table()# Extraire la liste des OFs
            else:
                self.show_popup("Erreur","Aucun ordre de fabrication existe avec votre selection")
                return

    def populate_table(self):
        self.row_checkboxes = []
        self.table_grid.clear_widgets()
        self.ids.header_grid.clear_widgets()

        columns = ['selection', 'numOF', 'Pointure', 'Quantite', 'Coloris', 'Modele', 'SAIS', 'dateCreation',
                   'regimeHoraire', "parcours"]
        n_cols = len(columns)
        row_height = dp(40)

        # Définir largeurs des colonnes
        col_widths = [dp(50)] + [dp(120)] * (len(columns) - 2) + [dp(250)]
        parcours_index = columns.index("parcours")
        col_widths[parcours_index] = dp(250)
        total_width = sum(col_widths)

        # Configuration header
        header_layout = self.ids.header_grid
        header_layout.cols = n_cols
        header_layout.width = total_width
        header_layout.size_hint_x = None

        for i, col in enumerate(columns):
            header = Label(
                text=str(col),
                size_hint_x=None,
                width=col_widths[i],
                size_hint_y=None,
                height=row_height,
                font_size='14sp',
                bold=True,
                color=(0, 0, 0, 1),
                halign='center',
                valign='middle',
                padding=(dp(5), dp(5)),
            )
            header.bind(size=header.setter('text_size'))
            header_layout.add_widget(header)

        # Gestion scroll vertical
        max_visible_rows = 15
        max_height = row_height * max_visible_rows
        content_height = row_height * len(self.df)

        self.ids.table_grid.height = content_height
        self.ids.table_grid.width = total_width
        self.ids.box_table_container.height = dp(40) + min(content_height, max_height)

        for i, row in enumerate(self.df):
            row_data = []
            checkbox = CheckBox(size_hint_x=None, width=dp(50))
            checkbox.row_index = i
            checkbox.bind(active=self.on_checkbox_active)
            self.row_checkboxes.append(checkbox)

            for col in columns[1:]:
                value = row.get(col, "")
                if col == "dateCreation" and isinstance(value, str):
                    value = value.split("T")[0]
                row_data.append(str(value))

            # Ligne horizontale avec largeur fixée
            row_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=row_height,
                size_hint_x=None,
                width=total_width
            )
            row_layout.add_widget(checkbox)

            for j, value in enumerate(row_data):
                cell = Label(
                    text=value,
                    size_hint_x=None,
                    width=col_widths[j + 1],
                    height=row_height,
                    color=(0, 0, 0, 1)
                )
                row_layout.add_widget(cell)

            self.ids.table_grid.add_widget(row_layout)

    def on_checkbox_active(self, checkbox, value):
        if self.is_selecting_all:
            return
        if value:  # Si la case est cochée
            if checkbox.row_index not in self.selected_rows_indices:
                self.selected_rows_indices.append(checkbox.row_index)
        else:  # Si la case est décochée
            if checkbox.row_index in self.selected_rows_indices:
                self.selected_rows_indices.remove(checkbox.row_index)

        # Met à jour la vraie sélection de lignes à partir des indices
        self.selected_rows = [self.df[i] for i in self.selected_rows_indices]
        print("Lignes sélectionnées :", self.selected_rows)
    def search(self):
        self.show_checkboxes=False
        self.checks=[]
        self.ids.select_all_checkbox.active = False
        self.show_statistics = False
        year = self.ids.year_id.text
        week = self.ids.week_id.text
        modele= self.ids.model_id.text

        last_digit_year = year[-1]
        self.search_text = int(f"{last_digit_year}{week}")
        print(str(self.search_text))
        print(len(str(self.search_text)))
        if len(str(self.search_text)) == 3 and modele in self.modeles:
            data = {
                "numof": self.search_text,
                "annee": self.ids.year_id.text,
                "modele": self.ids.model_id.text,
            }
            self.loadofs(data)
        else:
            self.show_popup("Attention","veuillez selectionner des choix valides")
            return

    def reset_filter(self):
        data={
            "numof": self.search_text,
            "annee": self.ids.year_id.text,
            "modele": self.ids.model_id.text,
        }
        self.loadofs(data)
        if not self.df:
            self.ids.status_label.text="vous n'avez aucun ordre de fabrication a lancer pour l'instant"
        else:
            self.ids.status_label.text=""
            self.populate_table()
            self.show_table=True
            self.show_checkbox=True

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

    def loadModels(self):
        response = make_request("get", "/manage_chaine_roles/get_all_models")
        if response.json()[1] == 200:
            print(response.json())
            data=response.json()[0].get("modeles")
            self.modeles=[model["nom_modele"] for model in data]
            self.ids.model_id.values=self.modeles
        else:
            print("Erreur lors du chargement des models :", response)

    def display_roles(self):
        grid_checkbox = self.ids.type_chaine
        grid_checkbox.clear_widgets()
        roles = self.loadType_chaine()
        for role in roles:
            # Container principal pour chaque ligne
            widget = self.build_role_widget(role)
            grid_checkbox.add_widget(widget)

    def build_role_widget(self, role):
        chaines=[item["chaine"] for item in self.checks]
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(140),
            spacing=dp(5)
        )

        top_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        label = Label(
            text=role,
            size_hint_x=0.7,
            font_size='16sp',
            color=(0.1, 0.1, 0.1, 1)
        )

        # Sous-container pour CheckBox + bouton 👁
        checkbox_row = BoxLayout(
            orientation='horizontal',
            size_hint_x=0.3,
            spacing=dp(2)  # très petit espacement pour qu’ils soient proches
        )

        checkbox = CheckBox(
            size_hint_x=None,
            width=dp(30),
            active=(role in chaines),
        )

        eye_button = Button(
            text='👁',
            size_hint_x=None,
            width=dp(20),
            height=dp(20),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(0, 0, 0, 1),
            font_size='16sp',
            font_name='seguiemj.ttf'
        )
        eye_button.bind(on_release=lambda instance: self.on_eye_click(role))

        checkbox_row.add_widget(checkbox)
        checkbox_row.add_widget(eye_button)

        top_row.add_widget(label)
        top_row.add_widget(checkbox_row)

        container.add_widget(top_row)

        # Gestion de l'activation/désactivation
        def on_active(instance, value):
            self.checkbox_typeChaine(instance, value, role)

        checkbox.bind(active=on_active)

        return container

    def on_eye_click(self, role):
        self.show_popup_formulaire_regimes(
            role,self.checks[0]["regimeHoraire"],
            self.checks[0]["regimeHoraire"],
            self.df[0]["Modele"],
        )


    def get_global_plan(self,chaine,regime,modele):
        print("get plan aaaaa")
        data = {
             "modele":modele,
             "chaine":chaine,
             "regime":regime
        }
        response = make_request("get", "/manage_chaine_roles/getPlanBymodelChaineAndRegime", json=data)
        if response.json()[1] == 200:
            print(response.json()[0])
            data = response.json()[0].get("plan")
            return data
        return None
    def show_popup_formulaire_regimes(self, chaine,titre,regime,modele):
        listplan = [item for item in self.checks if item["chaine"] == chaine]
        if listplan:
            plan = listplan[0]
        else:
            plan = self.get_global_plan(chaine, regime, modele)

        popup = Popup(
            title="Formulaire Régime Horaire",
            size_hint=(0.75, 0.6),
            auto_dismiss=False
        )

        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )

        with content.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            rect = Rectangle(pos=content.pos, size=content.size)

        def update_rect(instance, value):
            rect.pos = instance.pos
            rect.size = instance.size

        content.bind(pos=update_rect, size=update_rect)

        main_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint=(1, None),
            height=dp(400)
        )

        # Titre
        main_layout.add_widget(Label(
            text=f"[b]Régime {titre}[/b]",
            markup=True,
            font_size=20,
            size_hint_y=None,
            height=dp(30),
            color=(0, 0, 0, 1),
            halign='center'
        ))

        # Header
        header = BoxLayout(orientation='horizontal', spacing=dp(3), size_hint_y=None, height=dp(25))
        header.add_widget(Label(text="Jour", size_hint_x=0.4,opacity=0))
        header.add_widget(Label(text="Heure/jour", size_hint_x=0.3,color=(0, 0, 0, 1)))
        header.add_widget(Label(text="Paires/jour", size_hint_x=0.3,color=(0, 0, 0, 1)))
        main_layout.add_widget(header)

        # Pour stocker les champs et récupérer les valeurs plus tard
        regime_inputs = {}

        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
        for jour in jours:
            row = BoxLayout(orientation='horizontal', spacing=dp(3), size_hint_y=None, height=dp(32))

            row.add_widget(Label(text=f"{jour} :", size_hint_x=0.4,color=(0, 0, 0, 1)))
            horaire_val = str(plan.get(f"horaire{jour}", "7"))  # "7" par défaut
            nbpaire_val = str(plan.get(f"nbPaire{jour}", ""))  # vide par défaut
            heure_input = TextInput(
                text=horaire_val,
                multiline=False,
                input_filter='float',
                size_hint_x=0.3,
                height=dp(28)
            )
            paire_input = TextInput(
                text=nbpaire_val,
                multiline=False,
                input_filter='int',
                size_hint_x=0.3,
                height=dp(28)
            )

            # Stocker les champs dans un dictionnaire
            regime_inputs[f"horaire{jour}"] = heure_input
            regime_inputs[f"nbPaire{jour}"] = paire_input

            row.add_widget(heure_input)
            row.add_widget(paire_input)

            main_layout.add_widget(row)

        content.add_widget(main_layout)

        # Layout boutons
        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint=(1, None),
            height=dp(50),
            padding=[dp(30), 0, dp(30), 0]
        )
        btn_layout.add_widget(Widget())

        btn_save = Button(
            text="Enregistrer",
            size_hint=(None, None),
            size=(dp(150), dp(40)),
            background_color=(0.4, 0.7, 1, 1),
            color=(1, 1, 1, 1)
        )
        btn_save.bind(on_release=lambda x: self.enregistrer(regime_inputs,chaine,regime,modele,popup))


        btn_close = Button(
            text="Fermer",
            size_hint=(None, None),
            size=(dp(120), dp(40)),
            background_color=(1, 0.4, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        btn_close.bind(on_release=popup.dismiss)
        btn_layout.add_widget(btn_close)
        btn_layout.add_widget(btn_save)
        content.add_widget(btn_layout)
        popup.content = content
        popup.open()

    def enregistrer(self,inputs,chaine,regime,modele,popup):

        data={
            "chaine":chaine,
            "regimeHoraire":regime,
            "modele":modele,
        }
        for key, input_field in inputs.items():
            data[key] = input_field.text
        for item in self.checks:
            if item["chaine"] == chaine:
                self.checks.remove(item)
        self.checks.append(data)
        print(self.checks)
        popup.dismiss()
    def checkbox_typeChaine(self, instance, value, chaine):
        if value:
            for item in self.checks:
                if item["chaine"]==chaine:
                    self.show_popup_formulaire_regimes(item["chaine"],item["regimeHoraire"],item["regimeHoraire"],item["modele"])
            self.show_popup_formulaire_regimes(chaine,self.selected_rows[0]["regimeHoraire"],self.selected_rows[0]["regimeHoraire"],self.selected_rows[0]["Modele"])
        else:
            for item in self.checks:
                if item["chaine"]==chaine:
                    self.checks.remove(item)
        print(f"Chaînes sélectionnées: {self.checks}")
    def loadType_chaine(self):
        values = []
        response = make_request("get", "/manage_chaine_roles/getAllRoles")
        if response.status_code == 200:
            data = response.json()[0].get("roles")
            for role in data:
                values.append(role["id"])
            return values
        else:
            print("Erreur lors du chargement des utilisateurs :", response)


    def verify_chaines(self,chaine):
        return chaine in self.old_chaines

    def save_ofs_typechaine(self):
        if not self.selected_rows and not self.df:
            self.show_popup("Attention","aucun ordre de fabrication a modifier ")
            return
        if self.checks:
            self.liste_for_update=[]
            if self.selected_rows:
                self.liste_for_update=self.selected_rows
            else:
                self.liste_for_update=self.df
            self.of_chaines.clear()
            print("saveeeeeeee df",self.df)
            row=self.liste_for_update[0]["parcours"]
            self.old_chaines = list(set(row.split(",")))
            for item in self.checks:
                response = make_request("post", "/manage_planification_chaine_modele/addOrUpdatePlanification",json=item)
                if response.json()[1] == 201:
                    print("response",response.json()[0])
                    id = response.json()[0]["id"]
                    regime=response.json()[0]["regimeHoraire"]
                    print("regime",regime)
                    for of in self.liste_for_update:
                        num_of = of.get("numOF")
                        parcours = of.get("parcours")
                        chaines = [ch.strip() for ch in parcours.split(",") if ch.strip()]
                        print("chainees",chaines)
                        for ch in chaines:
                            print(self.old_chaines)
                            if not self.verify_chaines(ch):
                                self.show_popup("Attention","veuillez choisir des of avec des parcours compatibles")
                                return
                        ofchaine = {
                            "idchaine": item["chaine"],
                            "numCommandeOF": num_of,
                            "idPlanification":id,
                            "regimeHoraire":item["regimeHoraire"],
                        }
                        self.of_chaines.append(ofchaine)
                    print(self.of_chaines)
            data={
                "chaines":self.old_chaines,
                "ofs_chaines": self.of_chaines
            }
            print("dataaaaaaaaaaaaaaaaaaaaaaa",data)
            response = make_request("put", "/manage_ofs/update_of_chaine", json=data)
            print("response",response)
            if response.json()[1]== 200:
                print("200000000000000000000000000000000000000")

                self.show_popup("succées","OF enregistréé avec succées")
                self.show_checkboxes=False
                self.checks=[]
                data={
                    "numof": self.search_text,
                    "annee": self.ids.year_id.text,
                    "modele": self.ids.model_id.text,
                }
                self.loadofs(data)
                if not self.df:
                    self.ids.status_label.text = "vous n'avez aucun ordre de fabrication a lancer pour l'instant"
                    self.show_table=False
                else:
                    pass
            elif response.status_code == 409:
                self.show_popup("Attention","l'affectation des chaines pour les ofs sont deja fait")
            else:
                self.show_popup("Erreur","Vous n'etes pas autorisé pour cette fonction")
        else:
            self.show_popup("attention","veuillez seectionner des nouvelles chaines ")
            return

    def select_all_rows(self, is_active):

        self.is_selecting_all = True
        self.selected_rows_indices.clear()
        self.selected_rows.clear()

        for i, checkbox in enumerate(self.row_checkboxes):
            checkbox.active = is_active
            if is_active:
                self.selected_rows_indices.append(i)

        if is_active:
            self.selected_rows = [self.df[i] for i in self.selected_rows_indices]
        else:
            self.selected_rows = []

        self.is_selecting_all = False
        print("Lignes sélectionnées (tous cochés):", self.selected_rows)

    def valider_selection(self):
        self.checks = []

        if not self.selected_rows:
            self.show_popup("Attention", "Veuillez sélectionner au moins un OF.")
            return

        print("Lignes sélectionnées :", self.selected_rows)

        row = self.selected_rows[0]["parcours"]
        self.old_chaines = list(set(row.split(",")))

        for of in self.selected_rows:
            parcours = of.get("parcours")
            chaines = [ch.strip() for ch in parcours.split(",") if ch.strip()]
            print("chainees", chaines)
            for ch in chaines:
                print(self.old_chaines)
                if not self.verify_chaines(ch):
                    self.show_popup("Attention", "Veuillez choisir des OF avec des parcours compatibles")
                    return

        numcmd = self.selected_rows[0]["numOF"]
        data = {
            "numcmd": numcmd
        }


        response = make_request("get", "/manage_planification_chaine_modele/get_planifications_par_numcmd", json=data)

        if response.json()[1] == 200:
            self.show_checkboxes = True
            self.checks = response.json()[0].get("plan", [])
            print("checks", self.checks)
            self.display_roles()
