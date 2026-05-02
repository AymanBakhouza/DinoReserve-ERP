"""Ventana de acceso premium estilo comando futurista."""
import tkinter as tk
from tkinter import messagebox, ttk

from controllers.auth_controller import AuthController
from utils.constants import (
    APP_NAME,
    APP_VERSION,
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_BG_CARD,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    FONT_NORMAL,
    FONT_SUBTITLE,
)
from utils.assets import find_background, load_photo_image
from utils.exceptions import AuthenticationError, DinoReserveError
from views.styles import configure_styles
from views.ui_kit import brand_footer, load_brand_logo


class LoginView(tk.Tk):
    """Ventana inicial. En éxito instancia el Dashboard."""

    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} — Acceso")
        self.geometry("1280x760")
        self.minsize(1120, 680)
        self.configure(bg=COLOR_BG)
        configure_styles(self)

        self._auth = AuthController()
        self._user = None
        self._pwd_visible = False
        self._bg_img = None
        self._left_brand_canvas: tk.Canvas | None = None
        self._brand_redraw_job = None

        self._build_ui()
        self._center()

    # ------------------------------------------------------------
    def _center(self):
        self.update_idletasks()
        w, h = 1280, 760
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ------------------------------------------------------------
    def _build_ui(self):
        outer = ttk.Frame(self, padding=0)
        outer.pack(expand=True, fill="both")
        outer.columnconfigure(0, weight=4)
        outer.columnconfigure(1, weight=3)
        outer.rowconfigure(0, weight=1)

        left = tk.Frame(outer, bg=COLOR_BG, highlightthickness=0, bd=0)
        left.grid(row=0, column=0, sticky="nsew")
        self._build_left_brand(left)

        right = tk.Frame(outer, bg=COLOR_BG, highlightthickness=0, bd=0)
        right.grid(row=0, column=1, sticky="nsew")
        self._build_right_login(right)

    def _build_left_brand(self, parent):
        canvas = tk.Canvas(parent, bg=COLOR_BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self._left_brand_canvas = canvas
        self._logo_img = load_brand_logo(148, 148)
        canvas.bind("<Configure>", self._on_left_brand_resize)

    def _on_left_brand_resize(self, event):
        if event.width < 40 or event.height < 40:
            return
        if self._brand_redraw_job:
            self.after_cancel(self._brand_redraw_job)
        self._brand_redraw_job = self.after(
            40, lambda w=event.width, h=event.height: self._render_left_brand(w, h)
        )

    def _render_left_brand(self, width: int, height: int):
        canvas = self._left_brand_canvas
        if not canvas or not canvas.winfo_exists():
            return
        canvas.delete("all")
        self._draw_hud_background(canvas, width, height)
        bg_path = find_background("bg_login.png")
        self._bg_img = load_photo_image(bg_path, width=width, height=height) if bg_path else None
        if self._bg_img:
            canvas.create_image(width // 2, height // 2, image=self._bg_img)
            canvas.create_rectangle(0, 0, width, height, fill=COLOR_BG, stipple="gray75", outline="")
        pad = max(28, int(width * 0.06))
        canvas.create_rectangle(pad, pad, width - pad, height - pad, outline="#2F6543", width=1)
        canvas.create_line(pad, pad, min(width - pad, pad + 260), pad, fill=COLOR_PRIMARY, width=3)
        canvas.create_line(width - pad - 280, height - pad, width - pad, height - pad, fill=COLOR_ACCENT, width=3)

        if self._logo_img:
            logo_x = pad + 8
            logo_y = pad + 8
            canvas.create_image(logo_x, logo_y, image=self._logo_img, anchor="nw")

        title_x = pad + 24
        title_y = max(230, int(height * 0.36))
        title_size = max(34, min(56, int(width * 0.068)))
        subtitle_size = max(13, min(19, int(width * 0.024)))
        body_size = max(10, min(14, int(width * 0.017)))
        tag_size = max(8, min(10, int(width * 0.013)))

        canvas.create_text(
            title_x,
            title_y,
            text="DinoReserve",
            anchor="nw",
            fill=COLOR_TEXT,
            font=("Segoe UI", title_size, "bold"),
        )
        canvas.create_text(
            title_x,
            title_y + title_size + 18,
            text="Reserva Jurásica Inteligente",
            anchor="nw",
            fill=COLOR_PRIMARY,
            font=("Consolas", subtitle_size, "bold"),
        )
        line_y = title_y + title_size + subtitle_size + 34
        canvas.create_rectangle(title_x, line_y, min(width - pad - 30, title_x + 420), line_y + 3, fill=COLOR_ACCENT, outline="")
        canvas.create_text(
            title_x,
            line_y + 18,
            text="Control de biomas, seguridad, inventario y ventas\ndesde una consola predictiva de nueva generación.",
            anchor="nw",
            fill=COLOR_TEXT_MUTED,
            font=("Segoe UI", body_size),
            width=max(260, width - (title_x + pad + 40)),
        )
        canvas.create_text(
            title_x,
            line_y + 84,
            text="BIO-RED · MALLA DE SEGURIDAD · RUTAS DE SUMINISTRO · NÚCLEO DE INGRESOS",
            anchor="nw",
            fill=COLOR_SUCCESS,
            font=("Consolas", tag_size, "bold"),
        )

    def _draw_hud_background(self, canvas: tk.Canvas, width: int, height: int):
        for i, color in enumerate(["#06110B", "#09180F", "#0B1C12", "#102719"]):
            y1 = int((height / 4) * i)
            y2 = int((height / 4) * (i + 1))
            canvas.create_rectangle(0, y1, width, y2, fill=color, outline="")
        for x in range(-height, width, 34):
            canvas.create_line(x, 0, x + height, height, fill="#173A27")
        for y in range(0, height, 34):
            canvas.create_line(0, y, width, y, fill="#143322")
        radar_x = int(width * 0.68)
        radar_y = int(height * 0.24)
        r_outer = max(70, int(min(width, height) * 0.12))
        r_inner = int(r_outer * 0.74)
        canvas.create_oval(radar_x - r_outer, radar_y - r_outer, radar_x + r_outer, radar_y + r_outer, outline=COLOR_PRIMARY, width=2)
        canvas.create_oval(radar_x - r_inner, radar_y - r_inner, radar_x + r_inner, radar_y + r_inner, outline=COLOR_ACCENT, width=1)
        canvas.create_line(radar_x - r_outer - 20, radar_y, radar_x + r_outer + 20, radar_y, fill="#2F6543")
        canvas.create_line(radar_x, radar_y - r_outer - 20, radar_x, radar_y + r_outer + 20, fill="#2F6543")
        status_y = int(height * 0.74)
        canvas.create_rectangle(60, status_y, min(width - 60, 600), status_y + 4, fill=COLOR_PRIMARY, outline="")
        canvas.create_text(68, status_y + 10, text="BIO-RED EN LÍNEA", anchor="nw", fill=COLOR_PRIMARY, font=("Consolas", 10, "bold"))

    def _build_right_login(self, parent):
        wrap = tk.Frame(parent, bg=COLOR_BG, padx=42, pady=42)
        wrap.pack(fill="both", expand=True)
        tk.Frame(wrap, bg=COLOR_ACCENT, height=3).pack(fill="x", pady=(0, 18))
        card = tk.Frame(wrap, bg=COLOR_BG_CARD, bd=0, highlightthickness=1, highlightbackground="#2F6543")
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text="ACCESO DE COMANDO",
            bg=COLOR_BG_CARD,
            fg=COLOR_PRIMARY,
            font=("Consolas", 12, "bold"),
        ).pack(anchor="w", padx=30, pady=(28, 6))
        tk.Label(
            card,
            text="Autentícate para entrar al centro de control del parque.",
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT,
            font=("Segoe UI", 14, "bold"),
            wraplength=520,
            justify="left",
        ).pack(anchor="w", padx=30, pady=(0, 18))
        tk.Frame(card, bg="#2F6543", height=1).pack(fill="x", padx=30, pady=(0, 22))

        # Usuario
        tk.Label(card, text="Usuario", bg=COLOR_BG_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=30)
        self._user_var = tk.StringVar(value="admin")
        user_entry = ttk.Entry(card, textvariable=self._user_var, font=("Segoe UI", 16, "bold"))
        user_entry.pack(fill="x", padx=30, pady=(6, 18), ipady=8)

        # Contraseña
        tk.Label(card, text="Contraseña", bg=COLOR_BG_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=30)
        self._pwd_var = tk.StringVar(value="admin123")
        pwd_row = ttk.Frame(card)
        pwd_row.pack(fill="x", padx=30, pady=(6, 16))
        self._pwd_entry = ttk.Entry(pwd_row, textvariable=self._pwd_var, show="•", font=("Segoe UI", 16, "bold"))
        self._pwd_entry.pack(side="left", fill="x", expand=True, ipady=6)
        ttk.Button(pwd_row, text="Ver", width=7, style="Success.TButton",
                   command=self._toggle_password).pack(side="left", padx=(8, 0))
        pwd_entry = self._pwd_entry
        pwd_entry.bind("<Return>", lambda _e: self._handle_login())

        status_line = tk.Frame(card, bg=COLOR_BG_CARD)
        status_line.pack(fill="x", padx=30, pady=(4, 16))
        tk.Label(
            status_line,
            text="ESTADO · CREDENCIAL BIOMÉTRICA LISTA · BIO-RED ESTABLE",
            bg=COLOR_BG_CARD,
            fg=COLOR_SUCCESS,
            font=("Consolas", 9, "bold"),
        ).pack(anchor="w")

        ttk.Button(card, text="Entrar al centro de comando", style="Accent.TButton", command=self._handle_login).pack(fill="x", padx=30, pady=(0, 10), ipady=6)
        ttk.Button(
            card,
            text="Crear cuenta nueva",
            style="Ghost.TButton",
            command=self._open_register_dialog,
        ).pack(fill="x", padx=30, pady=(0, 16), ipady=5)
        demo = tk.Frame(card, bg="#0B1C12", highlightthickness=1, highlightbackground="#2F6543")
        demo.pack(fill="x", padx=30, pady=(0, 14))
        tk.Label(
            demo,
            text="ACCESO DEMO:  admin / admin123   ·   operador / operador123",
            bg="#0B1C12",
            fg=COLOR_TEXT,
            font=("Consolas", 10, "bold"),
        ).pack(anchor="w", padx=12, pady=12)

        footer = tk.Frame(wrap, bg=COLOR_BG)
        footer.pack(side="bottom", fill="x", pady=(8, 0))
        brand_footer(footer).pack()
        tk.Label(
            footer,
            text=f"v{APP_VERSION}  ·  © DinoReserve",
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_BG,
            font=("Segoe UI", 9),
        ).pack(pady=(4, 0))

        user_entry.focus_set()

    def _toggle_password(self):
        self._pwd_visible = not self._pwd_visible
        self._pwd_entry.configure(show="" if self._pwd_visible else "•")

    def _open_register_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Crear cuenta")
        dialog.configure(bg=COLOR_BG)
        dialog.geometry("480x520")
        dialog.minsize(440, 500)
        dialog.transient(self)
        dialog.grab_set()

        card = tk.Frame(dialog, bg=COLOR_BG_CARD, highlightthickness=1, highlightbackground=COLOR_PRIMARY)
        card.pack(fill="both", expand=True, padx=24, pady=24)
        tk.Frame(card, bg=COLOR_ACCENT, height=3).pack(fill="x")

        tk.Label(
            card,
            text="NUEVO ACCESO",
            bg=COLOR_BG_CARD,
            fg=COLOR_PRIMARY,
            font=("Consolas", 12, "bold"),
        ).pack(anchor="w", padx=24, pady=(22, 6))
        tk.Label(
            card,
            text="Crea credenciales para un operador del parque.",
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT,
            font=("Segoe UI", 13, "bold"),
            wraplength=390,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 18))

        user_var = tk.StringVar()
        pwd_var = tk.StringVar()
        confirm_var = tk.StringVar()
        role_label_var = tk.StringVar(value="Operador")
        roles = {"Administrador": "admin", "Operador": "operador"}

        def field(label: str, variable: tk.StringVar, show: str | None = None):
            tk.Label(
                card,
                text=label,
                bg=COLOR_BG_CARD,
                fg=COLOR_TEXT_MUTED,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w", padx=24)
            entry = ttk.Entry(card, textvariable=variable, show=show or "", font=("Segoe UI", 12, "bold"))
            entry.pack(fill="x", padx=24, pady=(5, 14), ipady=5)
            return entry

        first_entry = field("Usuario", user_var)
        field("Contraseña", pwd_var, show="•")
        field("Confirmar contraseña", confirm_var, show="•")

        tk.Label(
            card,
            text="Rol",
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_MUTED,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=24)
        role_combo = ttk.Combobox(
            card,
            textvariable=role_label_var,
            values=list(roles.keys()),
            state="readonly",
            font=("Segoe UI", 11, "bold"),
        )
        role_combo.pack(fill="x", padx=24, pady=(5, 18), ipady=4)

        def submit():
            role = roles.get(role_label_var.get(), "operador")
            try:
                user = self._auth.register(
                    user_var.get().strip(),
                    pwd_var.get(),
                    confirm_var.get(),
                    role,
                )
            except DinoReserveError as exc:
                messagebox.showerror("No se pudo crear la cuenta", exc.message, parent=dialog)
                return
            except Exception as exc:
                messagebox.showerror("Error inesperado", str(exc), parent=dialog)
                return

            self._user_var.set(user["username"])
            self._pwd_var.set(pwd_var.get())
            messagebox.showinfo("Cuenta creada", "La cuenta está lista para iniciar sesión.", parent=dialog)
            dialog.destroy()

        buttons = tk.Frame(card, bg=COLOR_BG_CARD)
        buttons.pack(fill="x", padx=24, pady=(0, 20))
        ttk.Button(buttons, text="Crear cuenta", style="Accent.TButton", command=submit).pack(side="left", fill="x", expand=True)
        ttk.Button(buttons, text="Cancelar", command=dialog.destroy).pack(side="left", padx=(10, 0))

        first_entry.focus_set()
        dialog.bind("<Return>", lambda _e: submit())
        dialog.wait_window()

    # ------------------------------------------------------------
    def _handle_login(self):
        username = self._user_var.get().strip()
        password = self._pwd_var.get()
        try:
            user = self._auth.login(username, password)
        except AuthenticationError as exc:
            messagebox.showerror("Error de acceso", exc.message, parent=self)
            return
        except Exception as exc:  # último recurso
            messagebox.showerror("Error inesperado", str(exc), parent=self)
            return

        self._user = user
        self.destroy()  # cierra login y devuelve control a main.py
