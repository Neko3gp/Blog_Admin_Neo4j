"""Factory de ComboBox de solo lectura con los colores de theme.py.

Se usa en filtros del feed, selector de autor al comentar, etc.
state="readonly" evita que el usuario escriba texto libre.
"""

import customtkinter as ctk

import theme


def make_combo(parent, width=140, **kwargs):
    """Devuelve un CTkComboBox ya estilizado. kwargs extra van al constructor."""
    return ctk.CTkComboBox(
        parent, state="readonly", width=width,
        fg_color=theme.ENTRY_BG, border_color=theme.ENTRY_BORDER,
        text_color=theme.ENTRY_FG, dropdown_fg_color=theme.DROPDOWN_BG,
        dropdown_text_color=theme.DROPDOWN_TEXT,
        button_color=theme.ENTRY_BORDER, button_hover_color=theme.BTN_SECONDARY_HOVER,
        **kwargs
    )
