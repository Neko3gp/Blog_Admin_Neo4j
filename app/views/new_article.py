"""Formulario modal para crear o editar un artículo.

Se abre como ventana Toplevel (no reemplaza el feed).

Al guardar usa db.ejecutar_varias en UNA transacción:
  crear:  articulo_crear      + articulo_asignar_etiquetas + articulo_asignar_categorias
  editar: articulo_actualizar + articulo_asignar_etiquetas + articulo_asignar_categorias

Así el nodo y sus relaciones N–N se guardan juntos (o nada se guarda).
"""

import uuid

import customtkinter as ctk
from tkinter import messagebox

from db import consultar, ejecutar_varias, mensaje_error


class ChecklistDesplegable(ctk.CTkFrame):
    """Botón que muestra/oculta casillas para elegir varias etiquetas o categorías."""

    def __init__(self, parent, titulo, opciones, marcadas=()):
        super().__init__(parent, fg_color="transparent")
        self.titulo = titulo
        self.visible = False
        # id_del_nodo → BooleanVar (True si la casilla está marcada)
        self.vars = {}

        self.boton = ctk.CTkButton(
            self, text=f"{titulo} ►", anchor="w",
            fg_color="#333333", hover_color="#444444", text_color="white",
            command=self.alternar
        )
        self.boton.pack(fill="x")

        self.lista = ctk.CTkScrollableFrame(self, height=120)
        for opcion in opciones:
            var = ctk.BooleanVar(value=opcion["id"] in marcadas)
            ctk.CTkCheckBox(self.lista, text=opcion["name"], variable=var).pack(
                anchor="w", padx=5, pady=2
            )
            self.vars[opcion["id"]] = var

        # En edición, si ya había selección, abre el desplegable
        if marcadas:
            self.alternar()

    def alternar(self):
        """Abre o cierra la lista de casillas."""
        self.visible = not self.visible
        if self.visible:
            self.lista.pack(fill="x", pady=(5, 0))
        else:
            self.lista.pack_forget()
        self.boton.configure(text=f"{self.titulo} {'▼' if self.visible else '►'}")

    def seleccionados(self):
        """Devuelve la lista de IDs marcados (para tag_ids / category_ids)."""
        return [id_ for id_, var in self.vars.items() if var.get()]


class NewArticleView(ctk.CTkToplevel):
    """Ventana de publicar / editar. Si `article` tiene id → modo edición."""

    def __init__(self, master, go_back_callback=None, article=None, **kwargs):
        super().__init__(master, **kwargs)
        self.go_back_callback = go_back_callback  # se llama al guardar con éxito
        self.article = article
        self.editing = article is not None and article.get("id") is not None

        self.title("Editar Artículo" if self.editing else "Publicar Nuevo Artículo")
        self.geometry("550x700")
        self.focus_force()

        # Carga catálogos necesarios para el formulario
        try:
            self.users = consultar("usuarios_listar")
            tags = consultar("etiquetas_listar")
            categorias = consultar("categorias_listar")
        except Exception as e:
            messagebox.showerror("Error de BD", mensaje_error(e))
            self.destroy()
            return

        # IDs ya asociados (solo en edición)
        marcadas_tags = article.get("tag_ids", []) if self.editing else []
        marcadas_cats = article.get("category_ids", []) if self.editing else []

        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(main, text="Título:", font=("Arial", 14, "bold")).pack(anchor="w")
        self.title_entry = ctk.CTkEntry(main, placeholder_text="Escribe el título...")
        self.title_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(main, text="Texto:", font=("Arial", 14, "bold")).pack(anchor="w")
        self.text_entry = ctk.CTkTextbox(main, height=150)
        self.text_entry.pack(fill="x", pady=(0, 15))

        # Autor = User existente (no hay login; solo se elige quién escribió)
        ctk.CTkLabel(main, text="Usuario autor:", font=("Arial", 14, "bold")).pack(anchor="w")
        self.combo_user = ctk.CTkComboBox(main, values=[u["name"] for u in self.users])
        self.combo_user.pack(fill="x", pady=(0, 15))

        self.tags = ChecklistDesplegable(main, "Etiquetas", tags, marcadas_tags)
        self.tags.pack(fill="x", pady=(10, 5))
        self.categorias = ChecklistDesplegable(main, "Categorías", categorias, marcadas_cats)
        self.categorias.pack(fill="x", pady=(10, 15))

        ctk.CTkButton(
            main,
            text="Guardar cambios" if self.editing else "Publicar Artículo",
            font=("Arial", 14, "bold"), fg_color="#28a745", hover_color="#218838",
            command=self.guardar
        ).pack(pady=20, fill="x")

        # Precarga campos si estamos editando
        if self.editing:
            self.title_entry.insert(0, article.get("title") or "")
            self.text_entry.insert("0.0", article.get("text") or "")
            autor = next((u["name"] for u in self.users if u["id"] == article.get("author_id")), None)
            if autor:
                self.combo_user.set(autor)

    def guardar(self):
        """Valida el formulario y escribe el artículo + asociaciones en una transacción."""
        titulo = self.title_entry.get().strip()
        texto = self.text_entry.get("0.0", "end").strip()
        user_id = next((u["id"] for u in self.users if u["name"] == self.combo_user.get()), None)

        if not titulo or not texto or user_id is None:
            messagebox.showerror("Error", "El título, texto y autor (existente) son obligatorios.")
            return

        datos = {"title": titulo, "text": texto, "user_id": user_id}
        if self.editing:
            article_id = self.article["id"]
            pasos = [("articulo_actualizar", {"id": article_id, **datos})]
        else:
            # ID nuevo generado en Python (UUID); la fecha la pone Neo4j con datetime()
            article_id = str(uuid.uuid4())
            pasos = [("articulo_crear", {"id": article_id, **datos})]

        # Reemplaza relaciones HAS_TAG e IN_CATEGORY por las casillas marcadas
        pasos.append(("articulo_asignar_etiquetas",
                      {"id": article_id, "tag_ids": self.tags.seleccionados()}))
        pasos.append(("articulo_asignar_categorias",
                      {"id": article_id, "category_ids": self.categorias.seleccionados()}))

        try:
            ejecutar_varias(pasos)
        except Exception as e:
            messagebox.showerror("Error de BD", mensaje_error(e))
            return

        messagebox.showinfo(
            "Éxito", "Artículo actualizado." if self.editing else "Artículo publicado correctamente."
        )
        self.destroy()
        if self.go_back_callback:
            self.go_back_callback()


def abrir_form_publicar_articulo(parent_frame, on_saved=None):
    """Atajo usado por el botón '+ Publicar artículo' del sidebar."""
    return NewArticleView(parent_frame, go_back_callback=on_saved)


def abrir_form_editar_articulo(parent_frame, article, on_saved=None):
    """Atajo usado por el botón '✎ Editar' del detalle."""
    return NewArticleView(parent_frame, go_back_callback=on_saved, article=article)
