"""Feed de artículos. Lee con la consulta `articulos_listar` (filtros por categoría y etiqueta).
Create: botón en main_gui → new_article.py. Update/Delete: article_detail.py."""

import customtkinter as ctk

import theme
from db import consultar, formatear_fecha, mensaje_error
from widgets.cards import ArticleCard
from widgets.combo import make_combo


class FeedView(ctk.CTkFrame):
    def __init__(self, parent, on_open_article):
        super().__init__(parent, fg_color=theme.CONTENT_BG)
        self.on_open_article = on_open_article

        self._build_toolbar()
        self.scroll_area = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=theme.SCROLLBAR_FG,
            scrollbar_button_hover_color=theme.SCROLLBAR_HOVER
        )
        self.scroll_area.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.reload()

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=16, pady=(14, 8))

        controls = ctk.CTkFrame(toolbar, fg_color="transparent")
        controls.pack(side="right")

        ctk.CTkLabel(controls, text="Ordenar:", text_color=theme.CONTENT_FG).pack(side="left", padx=(0, 4))
        self.combo_orden = make_combo(
            controls, width=180, command=self.reload,
            values=["Más reciente primero", "Más antiguo primero"],
        )
        self.combo_orden.set("Más reciente primero")
        self.combo_orden.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(controls, text="Categoría:", text_color=theme.CONTENT_FG).pack(side="left", padx=(0, 4))
        self.combo_categoria = make_combo(controls, command=self.reload)
        self.combo_categoria.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(controls, text="Tag:", text_color=theme.CONTENT_FG).pack(side="left", padx=(0, 4))
        self.combo_tag = make_combo(controls, command=self.reload)
        self.combo_tag.pack(side="left", padx=(0, 12))

        self._cargar_filtros()

    def _cargar_filtros(self):
        try:
            categorias = [c["name"] for c in consultar("categorias_listar")]
            etiquetas = [t["name"] for t in consultar("etiquetas_listar")]
        except Exception:
            categorias, etiquetas = [], []  # reload() mostrará el error de conexión

        self.combo_categoria.configure(values=["Todas"] + categorias)
        self.combo_categoria.set("Todas")
        self.combo_tag.configure(values=["Todos"] + etiquetas)
        self.combo_tag.set("Todos")

    def reload(self, _valor=None):
        """Vuelve a consultar Neo4j con los filtros elegidos y dibuja las tarjetas."""
        for widget in self.scroll_area.winfo_children():
            widget.destroy()

        categoria = self.combo_categoria.get()
        etiqueta = self.combo_tag.get()
        try:
            articulos = consultar(
                "articulos_listar",
                categoria=None if categoria in ("", "Todas") else categoria,
                etiqueta=None if etiqueta in ("", "Todos") else etiqueta,
            )
        except Exception as e:
            self._render_placeholder(f"No se pudo leer de Neo4j.\n{mensaje_error(e)}")
            return

        if self.combo_orden.get() == "Más antiguo primero":
            articulos.reverse()  # la consulta ya viene ordenada del más reciente al más antiguo

        if not articulos:
            self._render_placeholder("No hay artículos que mostrar todavía.")
            return

        for articulo in articulos:
            articulo["date"] = formatear_fecha(articulo["date"])
            ArticleCard(self.scroll_area, articulo, on_click=self.on_open_article).pack(
                fill="x", pady=6
            )

    def _render_placeholder(self, mensaje):
        ctk.CTkLabel(
            self.scroll_area, text=mensaje,
            font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"),
            text_color=theme.TEXT_MUTED, pady=40
        ).pack(fill="x")
