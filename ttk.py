from kivy.app import App
from kivy.lang import Builder
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Line
import pandas as pd
import numpy as np
from plyer import filechooser
import os
from kivy.uix.screenmanager import ScreenManager, Screen

KV = """
<DashboardScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1  # Light grey background
        Rectangle:
            pos: self.pos
            size: self.size

    search_input: search_input
    status_label: status_label
    table_grid: table_grid
    table_scroll: table_scroll
    header_scroll: header_scroll

    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        bar_width: dp(10)
        scroll_type: ['bars', 'content']
        effect_cls: 'ScrollEffect'

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(15)
            spacing: dp(10)

            # Header
            BoxLayout:
                size_hint_y: None
                height: dp(50)
                padding: dp(10)
                spacing: dp(10)
                canvas.before:
                    Color:
                        rgba: 0.2, 0.5, 0.8, 1  # Light blue
                    Rectangle:
                        pos: self.pos
                        size: self.size

                Label:
                    text: "📊 Tableau de bord - En attente"
                    font_name: 'EmojiFont'
                    color: 1, 1, 1, 1
                    bold: True
                    font_size: '20sp'
                    halign: 'left'
                    valign: 'middle'
                    size_hint_x: 1
                    text_size: self.size

            # Main content
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(15)
                padding: dp(15)

                # Search form
                BoxLayout:
                    size_hint_y: None
                    height: dp(50)
                    spacing: dp(10)

                    TextInput:
                        id: search_input
                        hint_text: '🔍 Rechercher...'
                        font_name: 'EmojiFont'
                        size_hint_x: 0.5
                        multiline: False
                        font_size: 18
                        foreground_color: 0, 0, 0, 1
                        cursor_color: 0, 0, 0, 1
                        background_normal: ''
                        background_color: 0.95, 0.95, 0.95, 1
                        padding: dp(5)

                    Button:
                        text: "🔎 Rechercher"
                        font_name: 'EmojiFont'
                        size_hint_x: 0.15
                        height: dp(50)
                        background_normal: ''
                        background_color: 0.7, 0.85, 1, 1
                        color: 0, 0, 0, 1
                        font_size: '14sp'
                        on_press: root.search(self)

                    Button:
                        text: '🔄 Réinitialiser'
                        font_name: 'EmojiFont'
                        size_hint_x: 0.15
                        background_normal: ''
                        background_color: 1, 0.7, 0.7, 1
                        color: 0, 0, 0, 1
                        font_size: '14sp'
                        on_press: root.reset_filter(self)

                # Import button
                Button:
                    text: '📂 Importer un fichier Excel'
                    font_name: 'EmojiFont'
                    size_hint_y: None
                    height: dp(50)
                    background_normal: ''
                    background_color: 1, 0.85, 0.4, 1
                    color: 0, 0, 0, 1
                    font_size: '16sp'
                    on_press: root.import_data(self)
                    canvas.before:
                        Color:
                            rgba: 0.5, 0.5, 0.5, 1
                        Line:
                            rectangle: (self.x, self.y, self.width, self.height)
                            width: 1

                # Status label
                Label:
                    id: status_label
                    text: 'ℹ️ Statut : Prêt'
                    font_name: 'EmojiFont'
                    size_hint_y: None
                    height: dp(30)
                    color: 0.2, 0.2, 0.2, 1
                    font_size: '14sp'

                # Data table
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_x: 1
                    size_hint_y: None
                    height: dp(400)
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Line:
                            rectangle: (self.x, self.y, self.width, self.height)
                            width: 1

                    ScrollView:
                        id: header_scroll
                        do_scroll_x: True
                        do_scroll_y: False
                        bar_width: dp(10)
                        size_hint_y: None
                        height: dp(40)

                        GridLayout:
                            id: header_grid
                            size_hint_y: None
                            height: dp(40)
                            size_hint_x: None
                            width: self.minimum_width
                            cols: 1
                            spacing: dp(1)
                            padding: dp(1)

                    ScrollView:
                        id: table_scroll
                        do_scroll_x: True
                        do_scroll_y: True
                        bar_width: dp(10)

                        GridLayout:
                            id: table_grid
                            size_hint_y: None
                            height: self.minimum_height
                            size_hint_x: None
                            width: self.minimum_width
                            spacing: dp(1)
                            padding: dp(1)
                            cols: 1

                # Lancer Coupe button
                Button:
                    text: '✂️ Lancer Coupe'
                    font_name: 'EmojiFont'
                    size_hint_y: None
                    height: dp(50)
                    background_normal: ''
                    background_color: 0.2, 0.5, 0.8, 1
                    color: 1, 1, 1, 1
                    font_size: '16sp'
                    on_press: root.lancer_coupe(self)

class CustomPopup(Popup):
    pass
"""

class DashboardScreen(Screen):
    search_input = ObjectProperty()
    status_label = ObjectProperty()
    table_grid = ObjectProperty()
    table_scroll = ObjectProperty()
    header_scroll = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.df = pd.DataFrame()
        self.selected_rows = []
        self.col_widths = []

    def on_parent(self, *args):
        if hasattr(self, 'table_scroll') and hasattr(self, 'header_scroll'):
            self.table_scroll.bind(scroll_x=self.header_scroll.setter('scroll_x'))
            self.header_scroll.bind(scroll_x=self.table_scroll.setter('scroll_x'))

    def import_data(self, instance):
        def file_selected(selection):
            if selection:
                file_path = selection[0]
                try:
                    new_df = pd.read_excel(file_path)
                    new_df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
                    new_df = new_df.dropna(axis=1, how='all')
                    new_df = new_df[new_df['EXP'].notna()]
                    for col in new_df.select_dtypes(include='float').columns:
                        new_df[col] = new_df[col].fillna(0).astype(int)
                    new_df = new_df.fillna("")
                    new_df['CDE'] = new_df['CDE'].fillna(0).astype(int)
                    new_df = new_df.loc[:, new_df.astype(str).ne("").any()]
                    # Filter for "En attente" status (assuming a 'Status' column)
                    if 'Status' in new_df.columns:
                        new_df = new_df[new_df['Status'].str.lower() == 'en attente']
                    else:
                        self.show_popup("Erreur", "La colonne 'Status' est absente.")
                        return
                    self.df = new_df.astype(str)
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
        self.table_grid.clear_widgets()
        self.ids.header_grid.clear_widgets()
        self.selected_rows = []
        if self.df.empty:
            return

        n_cols = len(self.df.columns) + 1  # +1 for checkbox column
        row_height = dp(40)
        self.col_widths = [dp(50)]  # Checkbox column width
        for i in range(len(self.df.columns)):
            self.col_widths.append(dp(120) if i < 4 or i >= len(self.df.columns) - 1 else dp(60))
        total_width = sum(self.col_widths)

        # Headers
        header_layout = self.ids.header_grid
        header_layout.cols = n_cols
        header_layout.width = total_width
        header_layout.size_hint_x = None
        header_layout.add_widget(Label(
            text="Sélection",
            size_hint_x=None,
            width=self.col_widths[0],
            height=dp(40),
            font_size='14sp',
            bold=True,
            color=(0, 0, 0, 1),
            halign='center',
            valign='middle',
            padding=(dp(5), dp(5))
        ))
        for i, col in enumerate(self.df.columns):
            header = Label(
                text=str(col),
                size_hint_x=None,
                width=self.col_widths[i + 1],
                height=dp(40),
                font_size='14sp',
                bold=True,
                color=(0, 0, 0, 1),
                halign='center',
                valign='middle',
                padding=(dp(5), dp(5))
            )
            header.bind(size=header.setter('text_size'))
            header_layout.add_widget(header)

        # Rows
        self.table_grid.cols = n_cols
        self.table_grid.width = total_width
        self.table_grid.size_hint_x = None
        self.table_grid.height = row_height * (len(self.df) + 1)
        for idx, row in self.df.iterrows():
            # Checkbox
            chk = CheckBox(
                size_hint_x=None,
                width=self.col_widths[0],
                size_hint_y=None,
                height=row_height,
                color=(0.49, 0.48, 0.49, 1),
                active_color=(0.2, 0.5, 0.8, 1)
            )
            chk.bind(active=lambda instance, value, i=idx: self.toggle_row(instance, value, i))
            self.table_grid.add_widget(chk)
            # Data cells
            for i, col in enumerate(self.df.columns):
                cell = Label(
                    text=str(row[col]),
                    size_hint_x=None,
                    width=self.col_widths[i + 1],
                    height=row_height,
                    font_size='13sp',
                    color=(0, 0, 0, 1),
                    halign='center',
                    valign='middle',
                    padding=(dp(5), dp(5))
                )
                cell.bind(size=cell.setter('text_size'))
                with cell.canvas.after:
                    Color(rgba=(0, 0, 0, 1))
                    Line(rectangle=(cell.x, cell.y, cell.width, cell.height), width=1)
                self.table_grid.add_widget(cell)

    def toggle_row(self, instance, value, index):
        if value and index not in self.selected_rows:
            self.selected_rows.append(index)
        elif not value and index in self.selected_rows:
            self.selected_rows.remove(index)
        self.status_label.text = f"{len(self.selected_rows)} lignes sélectionnées"
        self.status_label.color = (0.05, 0.4, 0.75, 1)

    def search(self, instance):
        search_text = self.search_input.text.lower()
        if search_text:
            filtered_df = self.df[
                self.df.apply(lambda row: any(search_text in str(val).lower() for val in row), axis=1)
            ]
            temp_df = self.df
            self.df = filtered_df
            self.populate_table()
            self.df = temp_df
            self.status_label.text = f"{len(filtered_df)} lignes affichées après filtrage"
        else:
            self.populate_table()
            self.status_label.text = "Filtre appliqué"
        self.status_label.color = (0.05, 0.4, 0.75, 1)

    def reset_filter(self, instance):
        self.search_input.text = ''
        self.populate_table()
        self.status_label.text = "Filtre réinitialisé"
        self.status_label.color = (0.05, 0.4, 0.75, 1)

    def lancer_coupe(self, instance):
        if not self.selected_rows:
            self.show_popup("Avertissement", "Aucune ligne sélectionnée.")
            return
        # Example action: Display selected rows' CDE values
        selected_cdes = self.df.iloc[self.selected_rows]['CDE'].tolist()
        self.show_popup("Succès", f"Lancement coupe pour CDEs: {', '.join(map(str, selected_cdes))}")
        self.status_label.text = f"Coupe lancée pour {len(self.selected_rows)} lignes"
        self.status_label.color = (0, 0.5, 0, 1)
        # Clear selections after processing
        self.selected_rows = []
        self.populate_table()

    def show_popup(self, title, message):
        popup = CustomPopup(title=title, size_hint=(0.8, 0.4))
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))  # Fixed the quote
        content.add_widget(Label(text=message, color=(0, 0, 0, 1)))  # Also fixed color to (0, 0, 0, 1) for consistency
        btn = Button(
            text="Fermer",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.7, 0.85, 1, 1),
            color=(0, 0, 0, 1)
        )
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.content = content
        popup.open()
class CustomPopup(Popup):
    pass
class NewKivyTableApp(App):
    def build(self):
        Builder.load_string(KV)
        return DashboardScreen()
if __name__ == '__main__':
    NewKivyTableApp().run()