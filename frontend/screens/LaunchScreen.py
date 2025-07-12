import math

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

        # Lignes du tableau
        max_height = dp(400)
        #self.table_grid.cols = n_cols
        self.table_grid.width = total_width
        self.table_grid.size_hint_x = None
        self.table_grid.size_hint_y = None
        content_height = row_height * len(self.df)
        self.table_grid.height = min(content_height, max_height)
        self.ids.box_table_container.height = dp(40) + self.table_grid.height
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

    def on_enter(self):
        self.ids.search_input.text = ""
        self.loadofs()

        if not self.df:
            self.ids.status_label.text = "vous n'avez aucun ordre de fabrication à lancer pour l'instant"
            return

        self.ids.status_label.text = ""
        self.show_table = True
        self.show_checkbox = True
        self.populate_table()

        grid_checkbox = self.ids.type_chaine
        grid_checkbox.clear_widgets()
        roles = self.loadType_chaine()

        for role in roles:
            # Container principal pour chaque ligne
            widget = self.build_role_widget(role)
            grid_checkbox.add_widget(widget)

    def build_role_widget(self, role):
        def update_total_label(*args):
            nbChampRrempli=0
            total = 0
            for champ in jours_inputs.values():
                try:
                    val = int(champ.text)
                    if val != "":
                        nbChampRrempli += 1
                    total += val
                except ValueError:
                    pass
            label_nbSemaine_nbJourstotal.text = f"Total : {total}/{self.qte_total}"
            if nbChampRrempli == 6:
                totaljour=total / 6        # ignore si vide ou invalide
                nbsemaine =self.qte_total // total
                reste = self.qte_total % total
                val = reste / totaljour
                nbjours = int(val + 0.5)
                label_nbSemaine_nbJourstotal.text = f"Total : {total}/{self.qte_total} prend {nbsemaine} semaines et {nbjours} jours"

            elif nbChampRrempli <6 and total==self.qte_total:
                label_nbSemaine_nbJourstotal.text = f"Total : {total}/{self.qte_total} prend {nbChampRrempli} jours"
        container = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=5,
            size_hint_y=None
        )
        container.bind(minimum_height=container.setter('height'))

        # Row: Label + CheckBox
        top_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        label = Label(text=role, font_size=20, color=(0.1, 0.1, 0.1, 1))
        checkbox = CheckBox(size_hint_x=None, width=50, active=False)
        top_row.add_widget(label)
        top_row.add_widget(checkbox)

        # Objectif section visible dès le départ
        objectif_box = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=[20, 5],
            size_hint_y=None
        )
        objectif_box.bind(minimum_height=objectif_box.setter('height'))

        # Champs pour chaque jour de la semaine
        jours_inputs = {}

        for jour in ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]:
            row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
            jour_label = Label(
                text=f"{jour.capitalize()} :",
                size_hint_x=None,
                width=dp(100),
                font_size=16,
                color=(0, 0, 0, 1)
            )
            input_field = TextInput(
                hint_text="Nb paires",
                size_hint=(None, None),
                size=(dp(120), dp(40)),
                input_filter='int',
                multiline=False,
                disabled=True,  # Inactif par défaut
                opacity=0.5,  # Visuellement grisé
            )
            input_field.bind(text=update_total_label)
            jours_inputs[jour] = input_field
            row.add_widget(jour_label)
            row.add_widget(input_field)
            objectif_box.add_widget(row)
        label_nbSemaine_nbJourstotal = Label(
            text= ":",
            size_hint_x=1,  # ← prend toute la largeur dispo
            halign='left',  # ← aligne à gauche
            valign='middle',
            font_size=16,
            color=(0, 0, 0, 1),

        )
        objectif_box.add_widget(label_nbSemaine_nbJourstotal)

        # Activer/Désactiver les champs quand la checkbox change
        def on_checkbox_active(cb, val):
            existing = next((item for item in self.checks if item["chaine"] == role), None)

            if val:  # coché
                if not existing:
                    self.checks.append({
                        "chaine": role,
                        "inputs": jours_inputs
                    })
            else:  # décoché
                if existing:
                    self.checks.remove(existing)

            # Activer/Désactiver les champs
            for input_field in jours_inputs.values():
                input_field.disabled = not val
                input_field.opacity = 1 if val else 0.5

        checkbox.bind(active=on_checkbox_active)

        # Ajout dans le conteneur principal
        container.add_widget(top_row)
        container.add_widget(objectif_box)

        return container

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

    def checkbox_typeChaine(self, instance,value,topping):
        print(value)
        if value:
            if topping not in self.checks:
                self.checks.append(topping)
        else:
            if topping in self.checks:
                self.checks.remove(topping)
        print(f"Current checks: {self.checks}")

    def get_selected_rows(self):
        selected = []
        for child in self.ids.table_grid.children:
            if isinstance(child, SelectableRow) and child.is_selected():
                selected.append(child.row_data)
        return selected

    def on_row_selection_changed(self):
        selected_rows = self.get_selected_rows()
        print("Lignes sélectionnées :", selected_rows)

    def save_ofs_typechaine(self):
        resultats = []

        for item in self.checks:
            chaine = item["chaine"]
            inputs = item["inputs"]
            objectifs = {}

            for jour, champ in inputs.items():
                objectifs[jour] = champ.text

            resultats.append({
                "chaine": chaine,
                "modele":self.df[0]['Modele'],
                "qteTotal":self.qte_total,
                "objectifs": objectifs
            })
        print(resultats)
        return resultats









        self.of_chaines.clear()
        print("saveeeeeeee df",self.df)
        for of in self.df:
            num_of = of.get("numOF")
            for chaine in self.checks:
                ofchaine = {
                    "idchaine": chaine,
                    "numCommandeOF": num_of
                }
                self.of_chaines.append(ofchaine)
        print(self.of_chaines)
        response = make_request("post", "/manage_ofs/addOfs_chaines", json=self.of_chaines)
        print("response",response)
        if response.status_code== 200:
            print("200000000000000000000000000000000000000")

            self.show_popup("succées","OF enregistréé avec succées")
            self.loadofs()
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

