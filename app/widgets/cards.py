"""Tarjeta de un artículo en el feed.

Muestra título, autor, fecha, snippet (si viene) y chips de categorías/tags.
Todo el bloque es clickeable → llama on_click(article) → main_gui abre el detalle.
"""

import customtkinter as ctk
from widgets.chips import make_chip
import theme


class ArticleCard(ctk.CTkFrame):
    """Una fila visual del feed (un nodo Article ya consultado)."""

    def __init__(self, parent, article, on_click=None, **kwargs):
        super().__init__(
            parent, fg_color=theme.PAGE_BG, border_color=theme.CARD_BORDER,
            border_width=1, corner_radius=8, **kwargs
        )
        self.article = article          # dict con id, title, author, date, tags, ...
        self.on_click = on_click        # normalmente main_gui._show_article_detail

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=16, pady=12)

        title_lbl = ctk.CTkLabel(
            content, text=article.get("title", "(sin título)"),
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color=theme.PAGE_FG, anchor="w", justify="left", wraplength=550
        )
        title_lbl.pack(fill="x", pady=(0, 2))

        meta = f"{article.get('author', 'Autor desconocido')} · {article.get('date', '')}"
        meta_lbl = ctk.CTkLabel(
            content, text=meta, font=ctk.CTkFont(family="Helvetica", size=11),
            text_color=theme.TEXT_MUTED, anchor="w"
        )
        meta_lbl.pack(fill="x", pady=(0, 4))

        # Widgets que deben reaccionar al clic (no solo el frame exterior)
        clickable = [self, content, title_lbl, meta_lbl]

        if article.get("snippet"):
            snippet_lbl = ctk.CTkLabel(
                content, text=article["snippet"], font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=theme.PAGE_FG, anchor="w", justify="left", wraplength=550
            )
            snippet_lbl.pack(fill="x", pady=(4, 4))
            clickable.append(snippet_lbl)

        # Chips de clasificación (solo visual; el filtro real está en el toolbar del feed)
        if article.get("categories") or article.get("tags"):
            chips_row = ctk.CTkFrame(content, fg_color="transparent")
            chips_row.pack(fill="x", pady=(4, 0))

            for cat in article.get("categories", []):
                chip = make_chip(chips_row, cat, kind="category")
                if chip:
                    chip.pack(side="left", padx=(0, 4))

            for tag in article.get("tags", []):
                chip = make_chip(chips_row, tag, kind="tag")
                if chip:
                    chip.pack(side="left", padx=(0, 4))

        # Bind de clic + cursor de “mano”
        for widget in clickable:
            widget.bind("<Button-1>", self._handle_click)
            widget.configure(cursor="hand2")

    def _handle_click(self, _event):
        """Pasa el artículo al callback de navegación."""
        if self.on_click:
            self.on_click(self.article)
