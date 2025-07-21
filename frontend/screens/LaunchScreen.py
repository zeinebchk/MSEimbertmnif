import math
from gc import disable

import numpy as np
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import Color, Line
import pandas as pd
import os
from kivy.animation import Animation
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from sqlalchemy import Selectable

from frontend.Client import make_request


class LaunchScreen(Screen):
    show_checkbox = BooleanProperty(False)
    show_table= BooleanProperty(False)
    search_input = ObjectProperty()
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
        self.planification=[]
        self.qte_total=0

    def on_parent(self, *args):
        # Synchronize horizontal scrolling between header_scroll and table_scroll
        if hasattr(self, 'table_scroll') and hasattr(self, 'header_scroll'):
            self.table_scroll.bind(scroll_x=self.header_scroll.setter('scroll_x'))
            self.header_scroll.bind(scroll_x=self.table_scroll.setter('scroll_x'))

    def calcul_qte_total(self,data):
        self.qte_total=0
        for i in data:
            self.qte_total += i["Quantite"]
        self.ids.qte_total_label.text=str(self.qte_total)+" paires au total"

    def loadofs(self):
        response = make_request("get", "/manage_ofs/getAllLatestOfs")
        if response.status_code == 200:
            self.df = response.json()[0].get("ofs", [])
            print(self.df)
            self.calcul_qte_total(self.df)
            self.populate_table()# Extraire la liste des OFs
        if not self.df:
            return
    def populate_table(self):
        self.table_grid.clear_widgets()
        self.ids.header_grid.clear_widgets()
        print( "populaaaaaate")


        # Ordre explicite des colonnes
        columns = ['numOF', 'Pointure', 'Quantite', 'Coloris', 'Modele', 'SAIS', 'dateLancement','dateCreation','etat']
        n_cols = len(columns)
        row_height = dp(40)

        # Largeur des colonnes
        col_widths = [dp(120)] * n_cols
        total_width = sum(col_widths)

        # En-têtes
        header_layout = self.ids.header_grid
        header_layout.cols = n_cols
        header_layout.width = total_width
        header_layout.size_hint_x = None
        header_layout.clear_widgets()

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

        max_visible_rows = 15
        row_height = dp(40)
        max_height = max_visible_rows * row_height

        content_height = row_height * len(self.df)

        # Limiter la hauteur visible du ScrollView (scroll activé si dépasse)
        self.ids.table_grid.height = content_height
        self.ids.box_table_container.height = dp(40) + min(content_height, max_height)
        # Lignes du tableau
        # max_height = dp(460)
        # #self.table_grid.cols = n_cols
        # self.table_grid.width = total_width
        # self.table_grid.size_hint_x = None
        # self.table_grid.size_hint_y = None
        # content_height = row_height * len(self.df)
        # self.table_grid.height = min(content_height, max_height)
        # self.ids.box_table_container.height = dp(40) + content_height
        for row in self.df:
            row_data = []
            for col in columns:
                value = row.get(col, "")
                if col == "dateLancement" and isinstance(value, str):
                    value = value.split("T")[0]  # enlever l'heure si présente
                row_data.append(str(value))  # toujours convertir en string

            # Créer une ligne sélectionnable
            row_widget = SelectableRow(row_data, col_widths,on_selection_change=self.on_row_selection_changed)
            self.table_grid.add_widget(row_widget)

    def search(self):
        grid_checkbox = self.ids.type_chaine
        grid_checkbox.clear_widgets()
        search_text = self.ids.search_input.text.lower()
        selected_column = self.ids.column_spinner.text

        if search_text and selected_column in ["dateLancement", "numOF", "Modele", "Coloris", "SAIS","Pointure"]:
            self.df = [
                item for item in self.df
                if str(item.get(selected_column, "")).lower().startswith(search_text)
            ]
            self.calcul_qte_total(self.df)

            self.populate_table()
            self.ids.search_input.text = ""
            self.status_label.text = f"{len(self.df)} lignes affichées après filtrage"
            self.status_label.color = (0.05, 0.4, 0.75, 1)
            print("filtered data:", self.df)
            roles = self.loadType_chaine()

            for role in roles:
                # Container principal pour chaque ligne
                widget = self.build_role_widget(role)
                grid_checkbox.add_widget(widget)
        else:
            self.show_popup("Attention", "Veuillez entrer un texte valide et choisir une colonne.")

    def reset_filter(self):
        self.loadofs()
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

    def show_popup_formulaire_regimes(self, chaine, regime, modele,titre):
        listplan=[item for item in self.checks if item["chaine"] == chaine]
        if listplan:
            plan=listplan[0]
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
            "regime":regime,
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

    def on_enter(self):
        self.ids.search_input.text = ""
        self.ids.regimeHoraire_id.text="42h"
        self.loadofs()

        if not self.df:
            self.ids.status_label.text = "vous n'avez aucun ordre de fabrication à lancer pour l'instant"
            return

        self.ids.status_label.text = ""
        self.show_table = True
        self.show_checkbox = True
        self.populate_table()
        self.display_roles()

    def display_roles(self):
        grid_checkbox = self.ids.type_chaine
        grid_checkbox.clear_widgets()
        roles = self.loadType_chaine()
        for role in roles:
            # Container principal pour chaque ligne
            widget = self.build_role_widget(role)
            grid_checkbox.add_widget(widget)

    def build_role_widget(self, role):
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
            width=dp(30)
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
        regime = self.ids.regimeHoraire_id.text
        if regime == "42h":
            self.show_popup_formulaire_regimes(role, regime, self.df[0]["Modele"], "42h")
        else:
            self.show_popup_formulaire_regimes(role, regime, self.df[0]["Modele"], "48h")

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
    def checkbox_typeChaine(self, instance, value, chaine):
        if value:
            regime=self.ids.regimeHoraire_id.text
            if chaine not in self.checks:
                if regime == "42h":
                    self.show_popup_formulaire_regimes(chaine,regime,self.df[0]["Modele"],"42h")
                else:
                    self.show_popup_formulaire_regimes(chaine,regime,self.df[0]["Modele"],"48h")
        else:
            for item in self.checks:
                if item["chaine"]==chaine:
                    self.checks.remove(item)
        print(f"Chaînes sélectionnées: {self.checks}")

    def get_selected_rows(self):
        selected = []
        for child in self.ids.table_grid.children:
            if isinstance(child, SelectableRow) and child.is_selected():
                selected.append(child.row_data)
        return selected

    def on_row_selection_changed(self):
        selected_rows = self.get_selected_rows()
        print("Lignes sélectionnées :", selected_rows)
    def getPlanBymodelChaineAndRegime(self,model,chaine,regimehoraire):
        data={
            "modele": model,
            "chaine": chaine,
            "regime": regimehoraire
        }
        response = make_request("get", "/manage_chaine_roles/getPlanBymodelChaineAndRegime", json=data)
        print("response", response)
        if response.json()[1] == 404:
            return None
        elif response.json()[1] == 200:
            return response.json()[0]
    def save_ofs_typechaine(self):
        self.of_chaines.clear()
        print("saveeeeeeee df",self.df)
        regime_horaire=self.ids.regimeHoraire_id.text
        for item in self.checks:
            response = make_request("post", "/manage_planification_chaine_modele/addOrUpdatePlanification", json=item)
            if response.json()[1] == 201:
                id = response.json()[0]["id"]
                for of in self.df:
                    num_of = of.get("numOF")
                    ofchaine = {
                    "regimeHoraire": regime_horaire,
                    "modele":of.get("Modele"),
                    "idchaine": item["chaine"],
                    "numCommandeOF": num_of,
                    "idPlanification":id
                    }
                    self.of_chaines.append(ofchaine)
            print(self.of_chaines)

        response = make_request("post", "/manage_ofs/addOfs_chaines", json=self.of_chaines)
        print("response",response)
        if response.status_code== 200:
            print("200000000000000000000000000000000000000")
            self.display_roles()
            self.show_popup("succées","OF enregistréé avec succées")
            self.loadofs()
            self.checks=[]
            if not self.df:
                self.ids.status_label.text = "vous n'avez aucun ordre de fabrication a lancer pour l'instant"
                self.show_table=False
            else:
                self.ids.status_label.text = ""
                self.show_table = True
                self.show_checkbox = True
                self.populate_table()
                self.ids.search_input.text = ""
        elif response.status_code == 409:
            self.show_popup("Attention","l'affectation des chaines pour les ofs sont deja fait")
        else:
            self.show_popup("Erreur","Vous n'etes pas autorisé pour cette fonction")






from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp


class SelectableRow(BoxLayout):
    def __init__(self, row_data, col_widths,on_selection_change=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        self.size_hint_x = None
        self.width = sum(col_widths)
        self.selected = False
        self.row_data = row_data
        self.on_selection_change = on_selection_change

        # Dessiner la couleur de fond
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Ajout des colonnes (labels)
        for i, val in enumerate(row_data):
            label = Label(
                text=str(val),
                size_hint_x=None,
                width=col_widths[i],
                size_hint_y=None,
                height=dp(40),
                halign='center',
                valign='middle',
                font_size='13sp',
                color=(0, 0, 0, 1),
                padding=(dp(5), dp(5))
            )
            label.bind(size=label.setter('text_size'))
            self.add_widget(label)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.selected = not self.selected
            self.bg_color.rgba = (0.6, 0.8, 1, 1) if self.selected else (1, 1, 1, 1)
            if self.on_selection_change:
                self.on_selection_change()
            return True
        return super().on_touch_down(touch)

    def is_selected(self):
        return self.selected

