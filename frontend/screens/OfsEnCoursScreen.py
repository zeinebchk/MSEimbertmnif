from datetime import datetime

from kivy.app import App
from kivy.atlas import CoreImage
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty, partial

from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
import io
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from frontend.calendar_popup import SimpleCalendarPopup, CalendarPopup

from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from marshmallow.fields import String
from matplotlib.backends.backend_agg import FigureCanvasAgg


from frontend.Client import make_request


class OfsEnCoursScreen(Screen):

    show_table= BooleanProperty(False)
    search_input = ObjectProperty()
    status_label = ObjectProperty()
    table_grid = ObjectProperty()
    table_scroll = ObjectProperty()
    header_scroll = ObjectProperty()
    show_statistics=BooleanProperty(False)
    show_modification_section=BooleanProperty(False)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.of_chaines = []
        self.df = []
        self.selected_rows = []
        self.models=[]
        self.statistics=[]
        self.ofsPerChaine=[]
        self.search_text=""
        self.numOFselectionne=0
        self.filter_inputs = {}  # Pour stocker les champs de recherche
        self.original_df = []  # Pour conserver les données non filtrées
        self.selected_rows=[]
        self.modeleforFiltered=""

    def get_maximum_date_of_ofs(self):
        response = make_request("get", "/manage_ofs/get_maximum_date_of_ofs")
        if response.status_code == 200:
            self.maxnumOfs = response.json()[0].get("maxNumberOfOfOfs")
    def on_parent(self, *args):
        # Synchronize horizontal scrolling between header_scroll and table_scroll
        if hasattr(self, 'table_scroll') and hasattr(self, 'header_scroll'):
            self.table_scroll.bind(scroll_x=self.header_scroll.setter('scroll_x'))
            self.header_scroll.bind(scroll_x=self.table_scroll.setter('scroll_x'))

    def loadofs(self, modele):
        self.df=[]
        self.original_df=[]
        data = {
            "modele": modele
        }
        response = make_request("get", "/manage_ofs/get_all_ofs_by_modele", json=data)
        if response.status_code == 200:
            self.original_df = response.json()[0].get("ofsbyModeles", [])  # Stocker les données originales
            self.df = self.original_df.copy()
            self.original_df = self.df.copy()# Copie pour le filtrage
            print(self.original_df)
            self.populate_table()
        if not self.df:
            return

    def populate_table(self):
        self.table_grid.clear_widgets()
        self.ids.header_grid.clear_widgets()
        print("populaaaaaate")

        # Ordre explicite des colonnes
        columns = ["inventaire", "atelierPiqure", "Modele", "Coloris", "DF", "numOF", "dateCreation",
                   "Quantite", "Pointure", "entre_Coupe", "sortie_Coupe",
                   "entre_Piqure", "sortie_Piqure", "entre_Montage", "sortie_Montage",
                   "export", "magasin", "nbre", "colisNonEmb", "observation"]
        n_cols = len(columns)
        row_height = dp(40)

        # Largeur des colonnes
        col_widths = [dp(120)] * n_cols
        total_width = sum(col_widths)

        # En-têtes avec champs de recherche
        header_layout = self.ids.header_grid
        header_layout.cols = n_cols
        header_layout.width = total_width
        header_layout.size_hint_x = None
        header_layout.clear_widgets()

        self.filter_inputs = {}  # Dictionnaire pour stocker les champs de recherche

        for i, col in enumerate(columns):
            # Créer un BoxLayout vertical pour chaque colonne (titre + champ de recherche)
            col_box = BoxLayout(orientation='vertical', size_hint_x=None, width=col_widths[i])

            # Titre de la colonne
            header = Label(
                text=str(col),
                size_hint_y=None,
                height=row_height / 2,
                font_size='12sp',
                bold=True,
                color=(0, 0, 0, 1),
                halign='center',
                valign='middle',
                padding=(dp(5), dp(5)),
            )
            header.bind(size=header.setter('text_size'))

            # Champ de recherche
            filter_input = TextInput(
                hint_text=f"Filtrer {col}",
                size_hint_y=None,
                height=row_height / 2,
                font_size='10sp',
                multiline=False
            )
            filter_input.bind(text=self.on_filter_change)

            col_box.add_widget(header)
            col_box.add_widget(filter_input)
            header_layout.add_widget(col_box)

            self.filter_inputs[col] = filter_input  # Stocker la référence

        # Stocker les données originales pour le filtrage
        self.original_df = self.df.copy()

        # Lignes du tableau
        self.update_table_rows()

    def on_filter_change(self, instance, value):
        filtered_data = self.original_df.copy()

        # Appliquer tous les filtres
        for col, input_widget in self.filter_inputs.items():
            filter_text = input_widget.text.lower()
            if filter_text:
                filtered_data = [row for row in filtered_data
                                 if filter_text in str(row.get(col, "")).lower()]

        self.df = filtered_data
        self.update_table_rows()

    def update_table_rows(self):
        self.table_grid.clear_widgets()

        columns = list(self.filter_inputs.keys())
        n_cols = len(columns)
        row_height = dp(40)
        col_widths = [dp(120)] * n_cols
        max_height = dp(400)

        self.table_grid.cols = 1  # chaque ligne = 1 SelectableRow (horizontal layout)
        self.table_grid.size_hint_x = None
        self.table_grid.size_hint_y = None
        self.table_grid.width = sum(col_widths)
        content_height = row_height * len(self.df)
        self.table_grid.height = min(content_height, max_height)
        self.ids.box_table_container.height = dp(120) + self.table_grid.height

        self.rows = []  # liste des SelectableRow ajoutées

        for row in self.df:
            row_data = []
            for col in columns:
                value = row.get(col, "")
                if col == "dateCreation" and isinstance(value, str):
                    value = value.split("T")[0]
                row_data.append(str(value))

            # Crée une ligne sélectionnable avec tous les champs en Label
            row_widget = SelectableRow(row_data, col_widths, screen=self,
                                       on_selection_change=self.on_row_selection_changed)
            self.table_grid.add_widget(row_widget)
            self.rows.append(row_widget)


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
        self.show_table=True
        self.ids.numOF_input.text=""
        self.numOFselectionne=0
        self.show_modification_section=False
        self.loadofs("DCDP500 STRETCH BISQUE")
        self.ids.inventaire_input.text=""
        self.ids.export_input.text=""
        self.ids.magasin_input.text=""
        self.ids.nbre_input.text=""
        self.ids.df_input.text=""
        self.ids.observation_input.text=""
    def afficherTextFields(self):
        self.show_modification_section=True
        self.ids.numOF_input.text=self.numOFselectionne
        self.ids.inventaire_input.text = self.selected_rows[0]
        self.ids.export_input.text = self.selected_rows[15]
        self.ids.magasin_input.text = self.selected_rows[16]
        self.ids.nbre_input.text = self.selected_rows[17]
        self.ids.df_input.text = self.selected_rows[4]
        self.ids.observation_input.text = self.selected_rows[19]

    def open_calendar(self):
        def set_date(date_str):
            self.ids.df_input.text = date_str

        popup = CalendarPopup(on_date_select=set_date)
        popup.open()


    def est_entier(self,valeur):
        try:
            int(valeur)
            return True
        except ValueError:
            return False
    def valider_modifications(self):
        nbre=self.ids.nbre_input.text
        if nbre!="" and not self.est_entier(nbre):
            self.show_popup("attention","ecrire un nombre valide")
            return
        data={
            "numof": self.numOFselectionne,
            "inventaire":self.ids.inventaire_input.text,
            "export":self.ids.export_input.text,
            "magasin":self.ids.magasin_input.text,
            "nbre":self.ids.nbre_input.text,
            "DF":self.ids.df_input.text,
            "observation":self.ids.observation_input.text,
        }
        response = make_request("put", "/manage_ofs/update_of", json=data)
        if response.status_code == 200:
            self.show_popup("Succées","l'of a été mise à jour ")
            self.loadofs("DCDP500 STRETCH BISQUE")
            self.show_modification_section=False
            self.numOFselectionne=0
            self.ids.numOF_input.text=""
        else:
            self.show_popup("Attention","Vous n'etes pas autorisé pour cette fonction")
            return


    def get_selected_rows(self):
        selected = {}
        for child in self.ids.table_grid.children:
            if isinstance(child, SelectableRow) and child.is_selected():
                selected=child.row_data
        return selected

    def on_row_selection_changed(self):
        print("ligne")
        self.selected_rows = self.get_selected_rows()

        print("Lignes sélectionnées :", self.selected_rows)
        self.numOFselectionne=self.selected_rows[5]
        print(self.numOFselectionne)


    def loadStatistics(self):
        self.statistics=[]
        data = {
            "numof": self.search_text,
            "models":self.models
        }
        response = make_request("get", "/manage_ofs/getStaticticPerModele", json=data)
        if response.status_code == 200:
            self.statistics = response.json()[0].get("statistics", [])
            self.afficher_pie_chart(self.statistics)

    def spinner_selected(self,text):
        print(text)
        self.modeleforFiltered=text
        self.loadofs(text)

    def loadofsPerModeleAndPerChaine(self, modele):
        self.ofsPerChaine=[]
        data = {
            "numof": self.search_text,
            "modele":modele
        }
        response = make_request("get", "/manage_ofs/getAllofsGroupbyChainewithStatistic", json=data)
        if response.status_code == 200:
            self.ofsPerChaine = response.json()[0].get("statistics",[])

             # Extraire la liste des OFs



    def populate_table_ofs_and_chart(self, data):
        container = self.ids.tableau_graphique_container
        container.clear_widgets()

        for item in data:
            ofs_list = item['ofs']

            # 1. Titre de la chaîne
            title = Label(
                text=f"[b]Chaîne : {item['idChaine']}[/b]",
                markup=True,
                font_size='18sp',
                size_hint_y=None,
                height=dp(20),
                halign='left',
                valign='middle',
                color=(0.1, 0.3, 0.5, 1),
            )
            title.bind(size=title.setter('text_size'))
            container.add_widget(title)

            # 2. Spinner de filtre
            spinner = Spinner(
                text="Filtrer les OFs",
                values=["Tous", "En attente", "En cours", "Terminés"],
                size_hint=(None, None),
                size=(200, dp(35)),
                font_size=14,
                color=(0, 0, 0, 1),
                background_color=(1, 1, 1, 1),
                background_normal='',
            )
            spinner.chaine_id = item["idChaine"]
            spinner.bind(text=self.on_spinner_select)
            container.add_widget(spinner)

            # 3. Ligne : tableau + diagramme
            row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(300))
            row.chaine_id = item['idChaine']

            # 4. Scrollable Tableau
            table_scroll = ScrollView(size_hint_x=0.7, size_hint_y=1)

            columns = ["numOF", "Pointure", "Quantité", "État", "Date lancement", "Date fin", "Ouvriers"]
            tableau = GridLayout(cols=len(columns), spacing=dp(5), size_hint_y=None)
            tableau.bind(minimum_height=tableau.setter("height"))
            row.tableau = tableau

            # En-têtes
            for col in columns:
                header = Label(
                    text=f"[b]{col}[/b]",
                    markup=True,
                    color=(0.2, 0.2, 0.2, 1),
                    size_hint_y=None,
                    height=dp(30)
                )
                tableau.add_widget(header)

            # Données OFs
            for idx, of in enumerate(ofs_list):
                bg_color = (1, 1, 1, 1) if idx % 2 == 0 else (0.95, 0.95, 0.95, 1)
                fields_map = {
                    "numOF": of.get("numCommandeOF") or of.get("numOF") or "-",
                    "Pointure": of.get("Pointure", "-"),
                    "Quantité": of.get("Quantite", "-"),
                    "État": of.get("etat", "-"),
                    "Date lancement": of.get("dateLancement_of_chaine", "-"),
                    "Date fin": of.get("dateFin", "-"),
                    "Ouvriers": of.get("ouvriers", "-"),
                }

                for key in columns:
                    label = Label(
                        text=str(fields_map[key]),
                        color=(0.1, 0.3, 0.5, 1),
                        size_hint_y=None,
                        height=dp(30)
                    )
                    with label.canvas.before:
                        Color(*bg_color)
                        rect = Rectangle(pos=label.pos, size=label.size)
                    label.bind(pos=partial(self.update_rect_pos, rect))
                    label.bind(size=partial(self.update_rect_size, rect))
                    tableau.add_widget(label)

            table_scroll.add_widget(tableau)

            # 5. Diagramme matplotlib
            values = [item["nb_en_attente"], item["nb_en_cours"], item["nb_termine"]]
            labels = ["En attente", "En cours", "Terminés"]
            colors = ["#e9c46a", "#2a9d8f", "#264653"]
            explode = (0.1, 0, 0)

            fig, ax = plt.subplots(figsize=(5, 5))
            fig.patch.set_alpha(0)
            ax.patch.set_alpha(0)
            ax.pie(values, labels=labels, textprops={'fontsize': 14}, autopct='%1.1f%%',
                   colors=colors, startangle=90, explode=explode, shadow=True)

            chart = FigureCanvasKivyAgg(fig)
            chart.size_hint_x = None
            chart.width = 450

            # 6. Ajout au layout
            row.add_widget(table_scroll)
            row.add_widget(chart)

            container.add_widget(row)

            # 7. Espacement
            container.add_widget(Widget(size_hint_y=None, height=dp(20)))

    def update_rect_pos(self, rect, instance, value):
        rect.pos = value

    def update_rect_size(self, rect, instance, value):
        rect.size = value

    def on_spinner_select(self, spinner, selected_value):
        chaine_id = getattr(spinner, 'chaine_id', None)
        if not chaine_id:
            return
        container = self.ids.tableau_graphique_container

        for child in container.children:
            # Chaque row est un BoxLayout qui contient le tableau
            if hasattr(child, 'chaine_id') and child.chaine_id == chaine_id:
                tableau = getattr(child, 'tableau', None)
                if tableau:
                    self.filtrer_tableau(tableau, chaine_id, selected_value)
                break

    def filtrer_tableau(self, tableau, chaine_id, filtre):
        # Trouver la chaîne et ses OFs
        chaine_for_filter = {}
        ofs_for_filter = []
        for chaine in self.ofsPerChaine:
            if chaine["idChaine"] == chaine_id:
                chaine_for_filter = chaine
                ofs_for_filter = chaine["ofs"]

        # Appliquer le filtre
        if filtre == "Tous":
            filtrés = ofs_for_filter
        elif filtre == "En cours":
            filtrés = [of for of in ofs_for_filter if of['etat'] == 'enCours']
        elif filtre == "Terminés":
            filtrés = [of for of in ofs_for_filter if of['etat'] == 'termine']
        elif filtre == "En attente":
            filtrés = [of for of in ofs_for_filter if of['etat'] == 'enAttente']

        columns = ["numOF", "Pointure", "Quantité", "État", "Date lancement", "Date fin", "Ouvriers"]

        # Vider le tableau
        tableau.clear_widgets()
        tableau.bind(minimum_height=tableau.setter("height"))

        # Réafficher les en-têtes
        for col in columns:
            header = Label(
                text=f"[b]{col}[/b]",
                markup=True,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_y=None,
                height=dp(30)
            )
            tableau.add_widget(header)

        # Ajouter les OFs filtrés
        for idx, of in enumerate(filtrés):
            bg_color = (1, 1, 1, 1) if idx % 2 == 0 else (0.95, 0.95, 0.95, 1)
            fields_map = {
                "numOF": of.get("numCommandeOF") or of.get("numOF") or "-",
                "Pointure": of.get("Pointure", "-"),
                "Quantité": of.get("Quantite", "-"),
                "État": of.get("etat", "-"),
                "Date lancement": of.get("dateLancement_of_chaine", "-"),
                "Date fin": of.get("dateFin", "-"),
                "Ouvriers": of.get("ouvriers", "-"),
            }

            for key in columns:
                label = Label(
                    text=str(fields_map[key]),
                    color=(0.1, 0.3, 0.5, 1),
                    size_hint_y=None,
                    height=dp(30)
                )
                with label.canvas.before:
                    Color(*bg_color)
                    rect = Rectangle(pos=label.pos, size=label.size)
                label.bind(pos=partial(self.update_rect_pos, rect))
                label.bind(size=partial(self.update_rect_size, rect))
                tableau.add_widget(label)

    def deselect_all_rows_except(self, selected_row):
        for row in self.table_grid.children:
            if isinstance(row, SelectableRow) and row != selected_row:
                row.deselect()

    def reinitialiser_formulaire(self):
        self.loadofs(self.modeleforFiltered)
        self.show_table = True
        self.ids.numOF_input.text = ""
        self.numOFselectionne = 0
        self.show_modification_section = False
        self.loadofs("DCDP500 STRETCH BISQUE")
        self.ids.inventaire_input.text = ""
        self.ids.export_input.text = ""
        self.ids.magasin_input.text = ""
        self.ids.nbre_input.text = ""
        self.ids.df_input.text = ""
        self.ids.observation_input.text = ""



from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp


class SelectableRow(BoxLayout):
    def __init__(self, row_data, col_widths, screen=None, on_selection_change=None, **kwargs):

        super().__init__(**kwargs)
        self.screen = screen
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
            if not self.selected:
                self.selected = True
                self.bg_color.rgba = (0.6, 0.8, 1, 1)  # Bleu clair

                if self.screen:
                    self.screen.deselect_all_rows_except(self)
                if self.on_selection_change:
                    self.on_selection_change()
            return True
        return super().on_touch_down(touch)

    def is_selected(self):
        return self.selected

    def deselect(self):
        self.selected = False
        self.bg_color.rgba = (1, 1, 1, 1)
