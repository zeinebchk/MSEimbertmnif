import numpy as np
from kivy.app import App
from kivy.lang import Builder
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




class DashboardScreen(Screen):
    show_checkbox = BooleanProperty(False)
    show_ChainePecure= BooleanProperty(False)
    search_input = ObjectProperty()
    status_label = ObjectProperty()
    table_grid = ObjectProperty()
    table_scroll = ObjectProperty()
    header_scroll = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.df = pd.DataFrame()
        self.checks = []
        self.checksChainePicure=[]
    def on_parent(self, *args):
        # Synchronize horizontal scrolling between header_scroll and table_scroll
        if hasattr(self, 'table_scroll') and hasattr(self, 'header_scroll'):
            self.table_scroll.bind(scroll_x=self.header_scroll.setter('scroll_x'))
            self.header_scroll.bind(scroll_x=self.table_scroll.setter('scroll_x'))

    def import_data(self, instance):
        from plyer import filechooser

        def file_selected(selection):
            if selection:
                file_path = selection[0]

                try:
                    self.show_checkbox=True
                    new_df = pd.read_excel(file_path)
                    new_df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
                    new_df = new_df.dropna(axis=1, how='all')  # Supprime les colonnes entièrement NaN
                    new_df = new_df[new_df['EXP'].notna()]
                    # Convertir toutes les colonnes float en int
                    for col in new_df.select_dtypes(include='float').columns:
                        new_df[col] = new_df[col].fillna(0).astype(int)  # Remplir NaN avec 0 et convertir en int
                    new_df = new_df.fillna("")  # Remplir les NaN restants avec ""
                    # Convertir CDE en int, en gérant les NaN
                    new_df['CDE'] = new_df['CDE'].fillna(0).astype(int)

                    if new_df.empty:
                        self.show_checkbox = False
                        self.show_popup("Erreur", "Le fichier Excel est vide.")
                        self.status_label.text = "Échec de l'importation : fichier vide"
                        self.status_label.color = (1, 0, 0, 1)
                        return

                    # Supprimer les colonnes où toutes les valeurs sont vides ("")
                    new_df = new_df.loc[:, new_df.astype(str).ne("").any()]

                    if self.df.empty:
                        self.df = new_df
                    else:
                        common_columns = self.df.columns.intersection(new_df.columns)
                        if not common_columns.empty:
                            new_df = new_df[common_columns]
                            self.df = pd.concat([self.df[common_columns], new_df], ignore_index=True)
                        else:
                            self.show_popup("Erreur",
                                            "Les colonnes du nouveau fichier ne correspondent pas au tableau existant.")
                            self.status_label.text = "Échec de l'importation : colonnes incompatibles"
                            self.status_label.color = (1, 0, 0, 1)
                            return

                    self.df = self.df.astype(str)
                    self.populate_table()
                    self.status_label.text = f"Données importées depuis {os.path.basename(file_path)}"
                    self.status_label.color = (0, 0.5, 0, 1)

                except Exception as e:
                    self.show_popup("Erreur", f"Erreur lors de l'import:\n{str(e)}")
                    self.status_label.text = f"Erreur : {str(e)}"
                    self.status_label.color = (1, 0, 0, 1)

        filechooser.open_file(
            title="Sélectionner un fichier Excel à importer",
            filters=[["Fichiers Excel", "*.xlsx", "*.xls"], ["Tous les fichiers", "*.*"]],
            on_selection=file_selected
        )

    def populate_table(self):
        if self.df.empty:
            self.table_grid.clear_widgets()
            self.ids.header_grid.clear_widgets()
            return

        n_cols = len(self.df.columns)
        row_height = dp(40)

        # Définir la largeur des colonnes : dp(60) pour les colonnes 4 à n-2, dp(120) pour les autres
        col_widths = []
        for i in range(n_cols):
            if 4 <= i < n_cols - 1:  # Colonnes 4 à n-2 (indices 0-based)
                col_widths.append(dp(60))
            else:
                col_widths.append(dp(120))

        # Calculer la largeur totale
        total_width = sum(col_widths)

        # En-têtes
        header_layout = self.ids.header_grid
        header_layout.clear_widgets()
        header_layout.cols = n_cols
        header_layout.width = total_width
        header_layout.size_hint_x = None

        for i, col in enumerate(self.df.columns):
            header = Label(
                text=str(col),
                size_hint_x=None,
                width=col_widths[i],
                size_hint_y=None,
                height=dp(40),
                font_size='14sp',
                bold=True,
                color=(0, 0, 0, 1),
                halign='center',
                valign='middle',
                padding=(dp(5), dp(5)),
            )
            header.bind(size=header.setter('text_size'))
            # # Ajouter des bordures internes
            # with header.canvas.after:
            #     Color(rgba=(0, 0, 0, 1))  # Noir pour les bordures
            #     Line(rectangle=(header.x, header.y, header.width, header.height), width=1)
            header_layout.add_widget(header)

        # Lignes
        self.table_grid.clear_widgets()
        self.table_grid.cols = n_cols
        self.table_grid.width = total_width
        self.table_grid.size_hint_x = None
        self.table_grid.size_hint_y = None
        self.table_grid.height = row_height * (len(self.df) + 1)

        for _, row in self.df.iterrows():
            for i, col in enumerate(self.df.columns):
                cell = Label(
                    text=str(row[col]),
                    size_hint_x=None,
                    width=col_widths[i],
                    size_hint_y=None,
                    height=row_height,
                    font_size='13sp',
                    color=(0, 0, 0, 1),
                    halign='center',
                    valign='middle',
                    padding=(dp(5), dp(5)),
                )
                cell.bind(size=cell.setter('text_size'))
                # Ajouter des bordures internes
                with cell.canvas.after:
                    Color(rgba=(0, 0, 0, 1))  # Noir pour les bordures
                    Line(rectangle=(cell.x, cell.y, cell.width, cell.height), width=1)
                self.table_grid.add_widget(cell)

    def filter_main_table(self, search_text):
        search_text = search_text.lower()
        if search_text:
            filtered_df = self.df[
                self.df.apply(lambda row: any(search_text in str(val).lower() for val in row), axis=1)]
        else:
            filtered_df = self.df

        temp_df = self.df
        self.df = filtered_df
        self.populate_table()
        self.df = temp_df

        self.status_label.text = f"{len(filtered_df)} lignes affichées après filtrage"
        self.status_label.color = (0.05, 0.4, 0.75, 1)

    def search(self, instance):
        search_text = self.search_input.text

        self.filter_main_table(search_text )

    def reset_filter(self, instance):
        self.search_input.text = ''

        self.populate_table()
        self.status_label.text = "Filtre réinitialisé"
        self.status_label.color = (0.05, 0.4, 0.75, 1)

    def show_popup(self, title, message):
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message, color=(0, 0, 0, 1)))
        btn = Button(text='Fermer', size_hint_y=None, height=dp(50),
                     background_color=(0.7, 0.85, 1, 1), color=(0, 0, 0, 1))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.content = content
        popup.open()
    def checkbox_typeChaine(self, instance,value,topping):
        print(value)
        if value:
            if topping not in self.checks:
                self.checks.append(topping)
        else:
            if topping in self.checks:
                self.checks.remove(topping)
        print(f"Current checks: {self.checks}")
    # def check_chainePicure(self, instance,value,topping):
    #     if value:
    #         if topping not in self.checksChainePicure:
    #             self.checksChainePicure.append(topping)
    #     else:
    #         if topping in self.checksChainePicure:
    #             self.checksChainePicure.remove(topping)
    #     print(f"Current checks: {self.checks}")
