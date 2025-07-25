from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
import calendar
from datetime import date


class CompactCalendar(BoxLayout):
    def __init__(self, on_date_select, **kwargs):
        super().__init__(orientation='vertical', spacing=5, **kwargs)
        self.on_date_select = on_date_select

        today = date.today()
        self.year = today.year
        self.month = today.month

        # Header : navigation année/mois
        nav = BoxLayout(size_hint_y=None, height=40, spacing=5)

        self.prev_month_btn = Button(text='<', size_hint_x=None, width=40)
        self.prev_month_btn.bind(on_release=self.prev_month)
        nav.add_widget(self.prev_month_btn)

        self.month_label = Label(text='', size_hint_x=None, width=100)
        nav.add_widget(self.month_label)

        self.next_month_btn = Button(text='>', size_hint_x=None, width=40)
        self.next_month_btn.bind(on_release=self.next_month)
        nav.add_widget(self.next_month_btn)

        self.year_spinner = Spinner(
            text=str(self.year),
            values=[str(y) for y in range(self.year - 50, self.year + 51)],
            size_hint_x=None,
            width=100)
        self.year_spinner.bind(text=self.on_year_select)
        nav.add_widget(self.year_spinner)

        self.add_widget(nav)

        # Jours de la semaine
        weekdays = GridLayout(cols=7, size_hint_y=None, height=30)
        for day in ['L', 'M', 'M', 'J', 'V', 'S', 'D']:
            weekdays.add_widget(Label(text=day))
        self.add_widget(weekdays)

        # Grille des jours
        self.days_grid = GridLayout(cols=7, spacing=2)
        self.add_widget(self.days_grid)

        self.build_days()

    def build_days(self):
        self.month_label.text = calendar.month_name[self.month]
        self.days_grid.clear_widgets()

        # Premier jour de la semaine (lundi=0 ou dimanche=6)
        first_weekday, num_days = calendar.monthrange(self.year, self.month)
        # Kivy calendar starts with Monday, calendar module Monday=0 so c’est cohérent

        # Ajouter des cases vides pour décaler le premier jour
        for _ in range(first_weekday):
            self.days_grid.add_widget(Label(text=''))

        # Ajouter les boutons des jours
        for day in range(1, num_days + 1):
            btn = Button(text=str(day), size_hint_y=None, height=40)
            btn.bind(on_release=self.select_day)
            self.days_grid.add_widget(btn)

    def select_day(self, instance):
        day = int(instance.text)
        date_str = f"{self.year:04d}-{self.month:02d}-{day:02d}"
        self.on_date_select(date_str)

    def prev_month(self, *args):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
            self.year_spinner.text = str(self.year)
        self.build_days()

    def next_month(self, *args):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
            self.year_spinner.text = str(self.year)
        self.build_days()

    def on_year_select(self, spinner, text):
        self.year = int(text)
        self.build_days()


class CalendarPopup(Popup):
    def __init__(self, on_date_select, **kwargs):
        super().__init__(title="Choisir une date", size_hint=(None, None), size=(350, 400), **kwargs)
        self.auto_dismiss = False

        self.calendar = CompactCalendar(self.on_date_selected)
        self.add_widget(self.calendar)
        self._external_callback = on_date_select

        # Bouton fermer
        btn_close = Button(text="Fermer", size_hint_y=None, height=40)
        btn_close.bind(on_release=self.dismiss)
        self.calendar.add_widget(btn_close)

    def on_date_selected(self, date_str):
        self._external_callback(date_str)
        self.dismiss()


class TestApp(App):
    def build(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button

        root = BoxLayout(orientation='horizontal', spacing=5, padding=10)
        self.date_input = TextInput(hint_text="Date (YYYY-MM-DD)", readonly=True)
        root.add_widget(self.date_input)

        btn = Button(text="📅", size_hint_x=None, width=40)
        btn.bind(on_release=self.open_calendar)
        root.add_widget(btn)
        return root

    def open_calendar(self, *args):
        popup = CalendarPopup(self.set_date)
        popup.open()

    def set_date(self, date_str):
        self.date_input.text = date_str


if __name__ == '__main__':
    TestApp().run()
