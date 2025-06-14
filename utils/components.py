username_input = """
MDTextField:
    hint_text: "Enter username"
    helper_text: "or click on forgot username"
    helper_text_mode: "on_focus"
    icon_right: "information"
    icon_right_color: app.theme_cls.primary_color
    pos_hint:{'center_x': 0.5, 'center_y': 0.55}
    hint_text_color: "black"
    size_hint_x:None
    text_color_focus: "black"
    width:500

"""

password_input = """
MDTextField:
    hint_text: "Enter password"
    helper_text: "Must be at least 8 characters"
    helper_text_mode: "on_focus"
    icon_right: "eye-off"
    icon_right_color: app.theme_cls.primary_color
    pos_hint: {'center_x': 0.5, 'center_y': 0.4}  # Position légèrement plus basse
    size_hint_x: None
    width: 500
    password: True  # Active le masquage du texte
    text_color_focus: "black"
    on_icon_right:
        self.password = False if self.password else True; \
        self.icon_right = "eye" if self.icon_right == "eye-off" else "eye-off"
"""

