from kivy.uix.spinner import SpinnerOption, Spinner
from kivy.uix.dropdown import DropDown

class CustomSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.9, 0.9, 1, 1)
        self.color = (0, 0, 0, 1)

class CustomSpinner(Spinner):
    option_cls = CustomSpinnerOption