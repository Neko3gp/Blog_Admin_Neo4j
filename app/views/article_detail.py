"""Detalle de artículo + comentarios.
  Artículo: editar (new_article.py) y eliminar (consulta `articulo_eliminar`, borra también sus comentarios)
  Comentarios: consultas comentarios_listar / comentario_crear / comentario_actualizar / comentario_eliminar
  No usar self._root (sombra el método de Tkinter).
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

import theme
from db import consultar, ejecutar, formatear_fecha, mensaje_error
from views.new_article import abrir_form_editar_articulo
from widgets.combo import make_combo


class ArticleDetailView(ctk.CTkFrame):
    def __init__(self, parent, article, on_back, on_article_changed=None):
        super().__init__(parent, fg_color=theme.PAGE_BG)
        self.article = dict(article)  # el feed ya trae título, texto, autor, etiquetas, etc.
        self.on_back = on_back
        self.on_article_changed = on_article_changed or on_back
        self._toplevel = self.winfo_toplevel()

        self._build_header()
        self._build_body_and_comments()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 4))

        ctk.CTkButton(
            header, text="← Volver al feed", command=self.on_back,
            fg_color="transparent", text_color=theme.SIDEBAR_SELECTED_TEXT,
            hover_color=theme.SIDEBAR_HOVER_BG,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            width=120, anchor="w"
        ).pack(anchor="w", pady=(0, 10))

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            actions, text="✎ Editar", width=100,
            fg_color="#ffc107", hover_color="#e0a800", text_color="black",
            command=self._editar_articulo
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            actions, text="✖ Eliminar", width=100,
            fg_color="#dc3545", hover_color="#c82333",
            command=self._eliminar_articulo
        ).pack(side="left")

        ctk.CTkLabel(
            header, text=self.article.get("title", ""),
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=theme.PAGE_FG, anchor="w", wraplength=640, justify="left"
        ).pack(fill="x")

        meta = f"{self.article.get('author', '')} · {self.article.get('date', '')}"
        ctk.CTkLabel(
            header, text=meta, font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=theme.TEXT_MUTED, anchor="w"
        ).pack(fill="x", pady=(2, 0))

    def _build_body_and_comments(self):
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=theme.SCROLLBAR_FG,
            scrollbar_button_hover_color=theme.SCROLLBAR_HOVER
        )
        self.scroll.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        texto = self.article.get("text")
        ctk.CTkLabel(
            self.scroll,
            text=texto or "(sin texto)",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=theme.PAGE_FG if texto else theme.TEXT_PLACEHOLDER,
            anchor="w", justify="left", wraplength=700
        ).pack(fill="x", padx=5, pady=(10, 20))

        ctk.CTkFrame(self.scroll, fg_color=theme.CARD_BORDER, height=1).pack(
            fill="x", padx=5, pady=(0, 20)
        )

        ctk.CTkLabel(
            self.scroll, text="Comentarios",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=theme.PAGE_FG, anchor="w"
        ).pack(fill="x", padx=5, pady=(0, 15))

        self.comments_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.comments_container.pack(fill="x", padx=5)
        self._render_comments()

        ctk.CTkFrame(self.scroll, fg_color=theme.CARD_BORDER, height=1).pack(
            fill="x", padx=5, pady=20
        )
        self._build_comment_form(self.scroll)

    def _editar_articulo(self):
        abrir_form_editar_articulo(
            self._toplevel,
            self.article,
            on_saved=self.on_article_changed,
        )

    def _eliminar_articulo(self):
        titulo = self.article.get("title", "")
        confirm = messagebox.askyesno(
            "Confirmar",
            f"¿Seguro que deseas eliminar el artículo '{titulo}'?\n"
            "También se eliminarán sus comentarios.",
        )
        if not confirm:
            return
        try:
            ejecutar("articulo_eliminar", id=self.article["id"])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el artículo.\n{mensaje_error(e)}")
            return
        messagebox.showinfo("Listo", "Artículo eliminado.")
        self.on_back()

    def _render_comments(self):
        for widget in self.comments_container.winfo_children():
            widget.destroy()

        try:
            comentarios = consultar("comentarios_listar", article_id=self.article["id"])
        except Exception as e:
            comentarios = None
            mensaje = f"No se pudieron leer los comentarios.\n{mensaje_error(e)}"

        if not comentarios:
            ctk.CTkLabel(
                self.comments_container,
                text="Todavía no hay comentarios." if comentarios == [] else mensaje,
                font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"),
                text_color=theme.TEXT_PLACEHOLDER, anchor="w"
            ).pack(fill="x", pady=10)
            return

        for comentario in comentarios:
            item = ctk.CTkFrame(self.comments_container, fg_color=theme.PANEL_BG, corner_radius=10)
            item.pack(fill="x", pady=6)

            top = ctk.CTkFrame(item, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(10, 2))

            meta = f"{comentario['author']} · {formatear_fecha(comentario['date'])}"
            ctk.CTkLabel(
                top, text=meta,
                font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
                text_color=theme.TEXT_MUTED, anchor="w"
            ).pack(side="left", fill="x", expand=True)

            ctk.CTkButton(
                top, text="✖", width=28, height=24,
                fg_color="#dc3545", hover_color="#c82333",
                command=lambda c=comentario: self._eliminar_comentario(c)
            ).pack(side="right", padx=(4, 0))

            ctk.CTkButton(
                top, text="✎", width=28, height=24,
                fg_color="#ffc107", hover_color="#e0a800", text_color="black",
                command=lambda c=comentario: self._editar_comentario(c)
            ).pack(side="right")

            ctk.CTkLabel(
                item, text=comentario["content"], font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=theme.PANEL_FG, anchor="w", justify="left", wraplength=650
            ).pack(fill="x", padx=15, pady=(0, 10))

    def _editar_comentario(self, comentario):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar comentario")
        dialog.geometry("420x220")
        dialog.transient(self._toplevel)
        dialog.grab_set()
        dialog.focus_force()

        ctk.CTkLabel(dialog, text="Nuevo contenido:", anchor="w").pack(
            fill="x", padx=16, pady=(16, 6)
        )
        box = ctk.CTkTextbox(dialog, height=100)
        box.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        box.insert("1.0", comentario["content"] or "")

        def guardar():
            nuevo = box.get("1.0", tk.END).strip()
            if not nuevo:
                messagebox.showwarning("Falta información", "El comentario no puede estar vacío.")
                return
            try:
                ejecutar("comentario_actualizar", id=comentario["id"], content=nuevo)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar.\n{mensaje_error(e)}")
                return
            dialog.destroy()
            self._render_comments()

        ctk.CTkButton(dialog, text="Guardar", command=guardar).pack(pady=(0, 16))

    def _eliminar_comentario(self, comentario):
        contenido = comentario["content"] or ""
        preview = contenido[:60] + ("…" if len(contenido) > 60 else "")
        confirm = messagebox.askyesno(
            "Confirmar", f"¿Seguro que deseas eliminar este comentario?\n\n«{preview}»"
        )
        if not confirm:
            return
        try:
            ejecutar("comentario_eliminar", id=comentario["id"])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar.\n{mensaje_error(e)}")
            return
        self._render_comments()

    def _build_comment_form(self, parent):
        form_container = ctk.CTkFrame(parent, fg_color="transparent")
        form_container.pack(fill="x", padx=5, pady=(0, 20))

        user_row = ctk.CTkFrame(form_container, fg_color="transparent")
        user_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            user_row, text="Usuario:", text_color=theme.PAGE_FG,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold")
        ).pack(side="left", padx=(0, 10))

        combo_usuario = make_combo(user_row, width=260)
        try:
            usuarios = consultar("usuarios_listar")
        except Exception:
            usuarios = []
        usuarios_by_name = {u["name"]: u["id"] for u in usuarios}
        if usuarios:
            combo_usuario.configure(values=list(usuarios_by_name))
            combo_usuario.set(usuarios[0]["name"])
        combo_usuario.pack(side="left")

        ctk.CTkLabel(
            form_container, text="Agregar comentario:",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            text_color=theme.PAGE_FG, anchor="w"
        ).pack(fill="x", pady=(5, 5))

        texto_comentario = ctk.CTkTextbox(
            form_container, height=80, fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER, border_width=1, text_color=theme.ENTRY_FG
        )
        texto_comentario.pack(fill="x", pady=(0, 12))

        def enviar():
            contenido = texto_comentario.get("1.0", tk.END).strip()
            user_id = usuarios_by_name.get(combo_usuario.get())
            if not contenido or user_id is None:
                messagebox.showwarning(
                    "Falta información", "Usuario y comentario son obligatorios."
                )
                return
            try:
                ejecutar(
                    "comentario_crear",
                    content=contenido, user_id=user_id, article_id=self.article["id"],
                )
            except Exception as e:
                messagebox.showerror("Error de Base de Datos", mensaje_error(e))
                return

            texto_comentario.delete("1.0", tk.END)
            self._render_comments()

        ctk.CTkButton(
            form_container, text="Comentar", command=enviar,
            fg_color=theme.SIDEBAR_SELECTED_BG, hover_color=theme.SIDEBAR_HOVER_BG,
            text_color=theme.SIDEBAR_SELECTED_TEXT,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            corner_radius=6, width=120
        ).pack(anchor="e")
