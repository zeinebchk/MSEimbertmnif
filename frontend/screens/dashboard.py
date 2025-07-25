from datetime import datetime

from kivy.atlas import CoreImage
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty, partial

from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
import io

from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from marshmallow.fields import String
from matplotlib.backends.backend_agg import FigureCanvasAgg


from frontend.Client import make_request


class DashboardScreen(Screen):

    show_table= BooleanProperty(False)
    search_input = ObjectProperty()
    status_label = ObjectProperty()
    table_grid = ObjectProperty()
    table_scroll = ObjectProperty()
    header_scroll = ObjectProperty()
    show_statistics=BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.of_chaines = []
        self.df = []
        self.selected_rows = []
        self.models=[]
        self.statistics=[]
        self.ofsPerChaine=[]
        self.search_text=""


    def get_maximum_date_of_ofs(self):
        response = make_request("get", "/manage_ofs/get_maximum_date_of_ofs")
        if response.status_code == 200:
            self.maxnumOfs = response.json()[0].get("maxNumberOfOfOfs")
    def on_parent(self, *args):
        # Synchronize horizontal scrolling between header_scroll and table_scroll
        if hasattr(self, 'table_scroll') and hasattr(self, 'header_scroll'):
            self.table_scroll.bind(scroll_x=self.header_scroll.setter('scroll_x'))
            self.header_scroll.bind(scroll_x=self.table_scroll.setter('scroll_x'))

    def loadofs(self):
        data={
            "numof": self.search_text
        }
        response = make_request("get", "/manage_ofs/getofs_byModele",json=data)
        if response.status_code == 200:
            self.df = response.json()[0].get("ofs", [])
            print(self.df)
            self.populate_table()# Extraire la liste des OFs
        if not self.df:
            return
    def populate_table(self):
        self.table_grid.clear_widgets()
        self.ids.header_grid.clear_widgets()
        print( "populaaaaaate")


        # Ordre explicite des colonnes
        columns = [ "Modele","total_quantite","Coloris","SAIS","dateCreation", "total_ofs"  ]
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
        self.show_statistics = False
        self.models=[]
        self.statistics=[]
        self.ofsPerChaine=[]
        self.ids.model_id.text = "Choisir un modele"
        year=self.ids.year_id.text
        week=self.ids.week_id.text
        last_digit_year = year[-1]
        self.search_text =int(f"{last_digit_year}{week}")
        print(str(self.search_text))
        print(len(str(self.search_text)))

        if len(str(self.search_text)) ==3:
            data = {
                "numof": self.search_text
            }
            response = make_request("get", "/manage_ofs/getofs_byModele", json=data)
            if response.status_code == 200:
                self.show_table=True
                self.df = response.json()[0].get("ofs", [])
                if self.df:
                    self.show_table=True
                    for model in self.df:
                        self.models.append((model["Modele"]))
                        self.models=list(set(self.models))
                    self.ids.model_id.values=self.models
                    print(self.df)
                    self.loadStatistics()
                    self.populate_table()
                else:
                    self.show_popup("Erreur", "Vous n'avez pas des modeles lancé dans cette date")
                    return
                    # Extraire la liste des OFs
            if not self.df:
                return
        else:
            self.show_popup("Attention","veuillez choisir un numero valide" )
            return
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
        annee_actuelle = datetime.now().year

        self.show_table=False
        self.show_statistics=False
        self.ids.year_id.values=[str(i) for i in range(2025,annee_actuelle+11)]
        self.ids.week_id.values=[f"{i:02}" for i in range(1, 53)]
        self.get_maximum_date_of_ofs()
        if self.maxnumOfs!=None:
            str_num = str(self.maxnumOfs)
            num_week=str_num[1:3]
            print("num weeeeek",num_week)
            anne_extract=str(annee_actuelle)[:3]

            self.ids.year_id.text=f"{anne_extract}{str_num[0]}"
            self.ids.week_id.text=num_week
            self.search()




    def get_selected_rows(self):
        selected = []
        for child in self.ids.table_grid.children:
            if isinstance(child, SelectableRow) and child.is_selected():
                selected.append(child.row_data)
        return selected

    def on_row_selection_changed(self):
        selected_rows = self.get_selected_rows()
        print("Lignes sélectionnées :", selected_rows)

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

    def afficher_pie_chart(self, data):
        self.ids.pie_chart_container.clear_widgets()
        for item in data:
            modele = item["modele"]
            values = [item["nb_done"], item["nb_inProgress"], item["nb_waiting"]]
            labels = ["Terminés", "En cours", "En attente"]
            colors = ["#2ecc71", "#f1c40f", "#e74c3c"]
            explode = (0.1, 0, 0)
            fig, ax = plt.subplots(figsize=(5, 5))
            fig.patch.set_alpha(0)  # fond transparent de la figure
            ax.patch.set_alpha(0)
            ax.pie(values, labels=labels,textprops={'fontsize': 14} , autopct='%1.1f%%', colors=colors, startangle=90, explode=explode, shadow=True)
            ax.set_title(modele, fontsize=20,color="#34495e")
            chart = FigureCanvasKivyAgg(fig)
            chart.size_hint_x = None
            chart.width = 450
            self.ids.pie_chart_container.add_widget(chart)

    def bar_chart(self, values):
        self.ids.bar_chart_container.clear_widgets()
        categories = ['En attente', 'En cours', 'Terminé']
        colors=["#e9c46a","#2a9d8f","#264653"]
        fig, ax = plt.subplots(figsize=(7,6))
        fig.patch.set_alpha(0)  # fond transparent figure
        ax.patch.set_alpha(0)  # fond transparent axes

        bars = ax.barh(categories, values, color=colors)

        # Ajouter valeur devant chaque barre
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.3, bar.get_y() + bar.get_height() / 2, str(int(width)),
                    va='center', ha='left', fontsize=18, color='black')

        # Enlever cadre & axes x
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(True)
        ax.set_yticklabels(categories, fontsize=18)
        fig.subplots_adjust(right=0.85)
        fig.suptitle("Statistiques des OFS", fontsize=24, color="#34495e", y=1)

        chart = FigureCanvasKivyAgg(fig)
        chart.size_hint_y = None
        chart.height = 350
        self.ids.bar_chart_container.add_widget(chart)

    def spinner_selected(self,text):
        print(text)

        for stat in self.statistics:
            if stat["modele"] == text:
                self.show_statistics = True
                self.bar_chart([stat["nb_waiting"],stat["nb_inProgress"],stat["nb_done"]])
                self.loadofsPerModeleAndPerChaine(text)
                break
    def loadofsPerModeleAndPerChaine(self, modele):
        self.ofsPerChaine=[]
        data = {
            "numof": self.search_text,
            "modele":modele
        }
        response = make_request("get", "/manage_ofs/getAllofsGroupbyChainewithStatistic", json=data)
        if response.status_code == 200:
            self.ofsPerChaine = response.json()[0].get("statistics",[])
            self.populate_table_ofs_and_chart(self.ofsPerChaine)
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

