from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import Screen
LabelBase.register(name="EmojiFont", fn_regular=r"D:\seguiemj.ttf")

Window.size = (600, 750)

class AddUserScreen(Screen):
    def ajouter_ouvrier(self):
        nom = self.ids.nom_ouvrier.text.strip()
        prenom = self.ids.prenom_ouvrier.text.strip()
        matricule = self.ids.matricule_ouvrier.text.strip()
        if nom and prenom and matricule:
            try:
                self.ids.message.text = "✅ Ouvrier ajouté avec succès !"
                self.ids.nom_ouvrier.text = ""
                self.ids.prenom_ouvrier.text = ""
                self.ids.matricule_ouvrier.text = ""
            except Exception as e:
                self.ids.message.text = f"❌ Erreur : {str(e)}"
        else:
            self.ids.message.text = "⚠️ Remplis tous les champs pour l'ouvrier."

    def ajouter_utilisateur(self):
        nom = self.ids.nom_utilisateur.text.strip()
        motdepasse = self.ids.motdepasse_utilisateur.text.strip()
        role = self.ids.role_utilisateur.text.strip()
        if nom and motdepasse and role:
            try:
                self.ids.message.text = "✅ Utilisateur ajouté avec succès !"
                self.ids.nom_utilisateur.text = ""
                self.ids.motdepasse_utilisateur.text = ""
                self.ids.role_utilisateur.text = "👑 Sélectionner un rôle"
            except Exception as e:
                self.ids.message.text = f"❌ Erreur : {str(e)}"
        else:
            self.ids.message.text = "⚠️ Remplis tous les champs pour l'utilisateur."

