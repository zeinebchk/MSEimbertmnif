from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.app import App
from kivy.core.window import Window
from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.addUser import AddUserScreen
emoji_font_path = r"D:\seguiemj.ttf"
LabelBase.register(name='EmojiFont', fn_regular=emoji_font_path)
Window.size = (800, 600)
Window.clearcolor = (0.95, 0.95, 0.95, 1)
GUI=Builder.load_file("main.kv")
class MyApp(App):
    def build(self):
        # self.theme_cls.primary_palette = "Green"
        # self.theme_cls.primary_hue = "A700"
        # self.theme_cls.theme_style = "Light"
        # Création du screen manager
        # sm = MDScreenManager()
        # sm.add_widget(LoginScreen(name='login'))
        #
        # sm.add_widget(DashboardScreen(name='dashboard'))
        return GUI


if __name__ == '__main__':
    MyApp().run()