from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.app import App
from kivy.core.window import Window
from screens.listUser import ListUserScreen
from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.addUser import AddUserScreen
from screens.RoleManagementScreen import RoleManagementScreen
from screens.UpdateLaunchScreen import UpdateLaunchScreen
from frontend.SessionManager import SessionManager
emoji_font_path = r"D:\seguiemj.ttf"
LabelBase.register(name='EmojiFont', fn_regular=emoji_font_path)
Window.size = (800, 600)
Window.clearcolor = (0.95, 0.95, 0.95, 1)
GUI=Builder.load_file("main.kv")
class MyApp(App):
    def build(self):
        return GUI

    def logout(self):
        session=SessionManager().get_instance()
        session.set_tokens(None,None)
        print(session.get_access_token())
        print(session.get_refresh_token())
        self.root.current = "login_screen"
    def root_to_listUsers(self):
        self.root.current = "list_users_screen"

    def root_to_addUser(self):
        self.root.current = "adduser_screen"
    def root_to_gestionRole(self):
        self.root.current = "gestion_role_screen"
    def root_to_update_launch(self):
        self.root.current="update_launch_screen"
    def root_to_lancement(self):
        self.root.current = "dashboard_screen"
if __name__ == '__main__':
    MyApp().run()