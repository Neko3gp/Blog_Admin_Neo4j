"""Categorías y Etiquetas: misma UI, distintas consultas Cypher.

Consultas:
  categorias_listar / categoria_crear / categoria_actualizar / categoria_eliminar
  etiquetas_listar  / etiqueta_crear  / etiqueta_actualizar  / etiqueta_eliminar

CategoriesView y TagsView solo pasan el título y los nombres de consulta
al panel genérico _TaxonomyPanel (evita duplicar código).
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import re
import unicodedata

import theme
from db import consultar, ejecutar, mensaje_error


def generar_slug(texto):
    """Convierte el nombre a un slug de URL: 'Bases de Datos' → 'bases-de-datos'.

    Quita acentos, pasa a minúsculas y reemplaza espacios por guiones.
    """
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.lower().strip()
    return re.sub(r'[-\s]+', '-', re.sub(r'[^a-z0-9\s-]', '', texto))


class _TaxonomyPanel(ctk.CTkFrame):
    """Panel reutilizable: lista + formulario de alta + editar/eliminar por fila."""

    def __init__(self, parent, titulo, q_listar, q_crear, q_actualizar, q_eliminar):
        super().__init__(parent, fg_color="transparent")
        # Nombres de consultas en consultas.cypher (inyectados por CategoriesView/TagsView)
        self.q_listar = q_listar
        self.q_crear = q_crear
        self.q_actualizar = q_actualizar
        self.q_eliminar = q_eliminar
        self.titulo = titulo  # "Categoría" o "Etiqueta" (para mensajes)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, pady=10)

        # Izquierda: listado
        list_col = ctk.CTkFrame(body, fg_color="transparent")
        list_col.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.scroll = ctk.CTkScrollableFrame(
            list_col, fg_color="transparent",
            scrollbar_button_color=theme.SCROLLBAR_FG,
            scrollbar_button_hover_color=theme.SCROLLBAR_HOVER
        )
        self.scroll.pack(fill="both", expand=True)

        # Derecha: alta (solo pide nombre; el url/slug se genera solo)
        form_col = ctk.CTkFrame(
            body, fg_color=theme.PANEL_BG, border_color=theme.PANEL_BORDER,
            border_width=1, corner_radius=10, width=320
        )
        form_col.pack_propagate(False)
        form_col.pack(side="right", fill="y", ipadx=10, ipady=10)

        ctk.CTkLabel(
            form_col, text=f"Nueva {self.titulo.lower()}",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=theme.PANEL_FG
        ).pack(anchor="w", padx=16, pady=(16, 10))

        ctk.CTkLabel(
            form_col, text="Nombre:", text_color=theme.PANEL_FG,
            font=ctk.CTkFont(family="Helvetica", size=13)
        ).pack(anchor="w", padx=16, pady=(10, 0))

        self.entry_nombre = ctk.CTkEntry(
            form_col, fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER, text_color=theme.ENTRY_FG
        )
        self.entry_nombre.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkButton(
            form_col, text="Guardar", command=self.guardar,
            fg_color=theme.BTN_SECONDARY_BG, hover_color=theme.BTN_SECONDARY_HOVER,
            text_color=theme.BTN_SECONDARY_FG, border_width=1,
            border_color=theme.BTN_SECONDARY_BORDER, corner_radius=6
        ).pack(pady=25, padx=16, fill="x")

        self.reload()

    def guardar(self):
        """Crea el nodo con name + url (slug). El nombre debe ser único."""
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta información", "El nombre es obligatorio.")
            return

        try:
            ejecutar(self.q_crear, name=nombre, url=generar_slug(nombre))
        except Exception as e:
            messagebox.showerror("Error", mensaje_error(e))
            return

        self.entry_nombre.delete(0, tk.END)
        self.reload()
        messagebox.showinfo("Listo", f"{self.titulo} creada exitosamente.")

    def _mensaje(self, texto):
        frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        frame.pack(fill="both", expand=True, pady=60)
        ctk.CTkLabel(
            frame, text=texto,
            font=ctk.CTkFont(family="Segoe UI", size=14, slant="italic"),
            text_color=theme.TEXT_PLACEHOLDER
        ).pack()

    def reload(self):
        """Lista nodos y pinta cada fila con botones ✎ / ✖."""
        for widget in self.scroll.winfo_children():
            widget.destroy()

        try:
            filas = consultar(self.q_listar)
        except Exception as e:
            self._mensaje(f"No se pudo leer de Neo4j.\n{mensaje_error(e)}")
            return

        if not filas:
            self._mensaje(f"No hay {self.titulo.lower()}s registradas en la base de datos.")
            return

        for fila in filas:
            item = ctk.CTkFrame(self.scroll, fg_color=theme.ENTRY_BG, corner_radius=6)
            item.pack(fill="x", pady=4, padx=2)

            info_frame = ctk.CTkFrame(item, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(
                info_frame, text=fila["name"],
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=theme.PANEL_FG
            ).pack(fill="x", padx=15, pady=(10, 0), anchor="w")

            if fila["url"]:
                ctk.CTkLabel(
                    info_frame, text=fila["url"],
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color=theme.TEXT_MUTED
                ).pack(fill="x", padx=15, pady=(0, 10), anchor="w")
            else:
                ctk.CTkFrame(info_frame, fg_color="transparent", height=10).pack()

            ctk.CTkButton(
                item, text="✖", width=30, fg_color="#dc3545", hover_color="#c82333",
                command=lambda f=fila: self.eliminar(f["id"], f["name"])
            ).pack(side="right", padx=(2, 15))

            ctk.CTkButton(
                item, text="✎", width=30, fg_color="#ffc107", hover_color="#e0a800", text_color="black",
                command=lambda f=fila: self.editar(f["id"], f["name"])
            ).pack(side="right", padx=2)

    def editar(self, item_id, nombre_actual):
        """Pide nuevo nombre y regenera el slug."""
        dialog = ctk.CTkInputDialog(text=f"Nuevo nombre para '{nombre_actual}':", title="Editar")
        nuevo_nombre = dialog.get_input()

        if nuevo_nombre and nuevo_nombre.strip() != nombre_actual:
            nuevo_nombre = nuevo_nombre.strip()
            try:
                ejecutar(
                    self.q_actualizar,
                    id=item_id, name=nuevo_nombre, url=generar_slug(nuevo_nombre),
                )
                self.reload()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {mensaje_error(e)}")

    def eliminar(self, item_id, nombre):
        """DETACH DELETE: quita el nodo y sus relaciones con artículos (los artículos quedan)."""
        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar '{nombre}'?"):
            try:
                ejecutar(self.q_eliminar, id=item_id)
                self.reload()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {mensaje_error(e)}")


class _TaxonomyView(ctk.CTkFrame):
    """Envuelve el panel con el título de página (Categorías / Etiquetas)."""

    def __init__(self, parent, titulo_pagina, titulo, consultas):
        super().__init__(parent, fg_color=theme.PAGE_BG)

        ctk.CTkLabel(
            self, text=titulo_pagina,
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=theme.PAGE_FG
        ).pack(anchor="w", padx=20, pady=(20, 10))

        _TaxonomyPanel(self, titulo, *consultas).pack(
            fill="both", expand=True, padx=20, pady=(0, 20)
        )


class CategoriesView(_TaxonomyView):
    """Pantalla Categorías: opera sobre nodos :Category."""

    def __init__(self, parent):
        super().__init__(
            parent, "Categorías", "Categoría",
            ("categorias_listar", "categoria_crear", "categoria_actualizar", "categoria_eliminar"),
        )


class TagsView(_TaxonomyView):
    """Pantalla Etiquetas: opera sobre nodos :Tag."""

    def __init__(self, parent):
        super().__init__(
            parent, "Etiquetas", "Etiqueta",
            ("etiquetas_listar", "etiqueta_crear", "etiqueta_actualizar", "etiqueta_eliminar"),
        )
