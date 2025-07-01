from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image as CoreImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io

class BarChart(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.plot_chart()

    def plot_chart(self):
        # Libellés + valeurs
        categories = ['En attente', 'En cours', 'Terminé']
        values = [10, 5, 2]

        # 🔍 Figure plus large
        fig, ax = plt.subplots(figsize=(7, 3.5))
        bars = ax.barh(categories, values, color='steelblue')

        # ✨ Ajouter la valeur devant chaque barre
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + 0.5,  # 🔄 décalage plus visible
                bar.get_y() + bar.get_height() / 2,
                str(int(width)),
                va='center', ha='left', fontsize=12, color='black'
            )

        # ❌ Enlever axes + cadre
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(True)

        # ❗ Important : laisser de la marge à droite
        fig.subplots_adjust(right=0.85)

        # Convertir l’image en texture pour Kivy
        buf = io.BytesIO()
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(buf)
        buf.seek(0)

        image = CoreImage(buf, ext="png").texture
        self.add_widget(Image(texture=image))


class ChartApp(App):
    def build(self):
        return BarChart()


if __name__ == '__main__':
    ChartApp().run()
