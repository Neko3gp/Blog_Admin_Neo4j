"""Pantalla Usuarios: listar y registrar.

Consultas: usuarios_listar (leer) y usuario_crear (crear).
La interfaz NO edita ni elimina usuarios (alcance deliberado del proyecto).
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

import theme
from db import consultar, ejecutar, mensaje_error


class UsersView(ctk.CTkFrame):
    """Lista a la izquierda + formulario 'Nuevo usuario' a la derecha."""

    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.PAGE_BG)

        ctk.CTkLabel(
            self, text="Usuarios",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=theme.PAGE_FG
        ).pack(anchor="w", padx=20, pady=(20, 10))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Columna izquierda: listado scrolleable
        list_col = ctk.CTkFrame(body, fg_color="transparent")
        list_col.pack(side="left", fill="both", expand=True)

        self.scroll = ctk.CTkScrollableFrame(
            list_col, fg_color="transparent",
            scrollbar_button_color=theme.SCROLLBAR_FG,
            scrollbar_button_hover_color=theme.SCROLLBAR_HOVER
        )
        self.scroll.pack(fill="both", expand=True)

        # Columna derecha: formulario de alta
        form_col = ctk.CTkFrame(
            body, fg_color=theme.PANEL_BG, border_color=theme.PANEL_BORDER,
            border_width=1, corner_radius=10
        )
        form_col.pack(side="right", fill="y", padx=(16, 0), ipadx=16, ipady=16)

        self._build_form(form_col)
        self.reload()

    def _build_form(self, parent):
        """Campos nombre/email y botón Guardar → usuario_crear."""
        ctk.CTkLabel(
            parent, text="Nuevo usuario",
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color=theme.PANEL_FG
        ).pack(anchor="w", padx=16, pady=(16, 10))

        entradas = {}
        for clave, etiqueta in (("name", "Nombre:"), ("email", "Email:")):
            ctk.CTkLabel(
                parent, text=etiqueta, text_color=theme.PANEL_FG,
                font=ctk.CTkFont(family="Helvetica", size=13)
            ).pack(anchor="w", padx=16, pady=(10, 0))

            entradas[clave] = ctk.CTkEntry(
                parent, width=220, fg_color=theme.ENTRY_BG,
                border_color=theme.ENTRY_BORDER, text_color=theme.ENTRY_FG
            )
            entradas[clave].pack(padx=16, pady=(0, 10))

        def guardar():
            nombre = entradas["name"].get().strip()
            email = entradas["email"].get().strip()
            if not nombre or not email:
                messagebox.showwarning("Falta información", "Nombre y email son obligatorios.")
                return
            try:
                # Si el email ya existe, Neo4j lanza ConstraintError (mensaje_error lo traduce)
                ejecutar("usuario_crear", name=nombre, email=email)
            except Exception as e:
                messagebox.showerror("Error", mensaje_error(e))
                return
            for entrada in entradas.values():
                entrada.delete(0, tk.END)
            self.reload()
            messagebox.showinfo("Listo", "Usuario creado.")

        ctk.CTkButton(
            parent, text="Guardar", command=guardar,
            fg_color=theme.BTN_SECONDARY_BG, hover_color=theme.BTN_SECONDARY_HOVER,
            text_color=theme.BTN_SECONDARY_FG, border_width=1,
            border_color=theme.BTN_SECONDARY_BORDER, corner_radius=6
        ).pack(pady=20)

    def _mensaje(self, texto):
        """Placeholder cuando la lista está vacía o hubo error de conexión."""
        ctk.CTkLabel(
            self.scroll, text=texto,
            font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"),
            text_color=theme.TEXT_PLACEHOLDER
        ).pack(anchor="w", pady=10)

    def reload(self):
        """Vuelve a pedir usuarios_listar y redibuja las filas."""
        for widget in self.scroll.winfo_children():
            widget.destroy()

        try:
            usuarios = consultar("usuarios_listar")
        except Exception as e:
            self._mensaje(f"No se pudo leer de Neo4j.\n{mensaje_error(e)}")
            return

        if not usuarios:
            self._mensaje("Todavía no hay usuarios.")
            return

        for usuario in usuarios:
            item = ctk.CTkFrame(self.scroll, fg_color=theme.ENTRY_BG, corner_radius=6)
            item.pack(fill="x", pady=4)

            ctk.CTkLabel(
                item, text=usuario["name"],
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=theme.PANEL_FG
            ).pack(fill="x", padx=12, pady=(8, 0), anchor="w")

            ctk.CTkLabel(
                item, text=usuario["email"],
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=theme.TEXT_MUTED
            ).pack(fill="x", padx=12, pady=(0, 8), anchor="w")
