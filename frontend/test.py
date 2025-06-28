from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_gardenmatplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt

class PieChartApp(App):
    def build(self):
        layout = BoxLayout()

        # Création du graphique
        fig, ax = plt.subplots()
        labels = ['Terminé', 'En cours', 'Restant']
        sizes = [100, 50, 30]
        colors = ['#4CAF50', '#FFC107', '#F44336']
        explode = (0.1, 0, 0)

        ax.pie(sizes, labels=labels, autopct='%1.1f%%',
               startangle=90, colors=colors, explode=explode, shadow=True)
        ax.axis('equal')
        ax.set_title("État de production")

        # Embed matplotlib figure in Kivy
        canvas = FigureCanvasKivyAgg(fig)
        layout.add_widget(canvas)

        return layout

PieChartApp().run()
