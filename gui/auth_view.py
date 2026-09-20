"""Home Landing, Authentication & Guest Mode View for StudyForge AI."""
import customtkinter as ctk
from gui.theme import COLORS, FONTS
from database.models import UserModel

class AuthView(ctk.CTkFrame):
    def __init__(self, master, on_auth_success, **kwargs):
        super().__init__(
            master,
            fg_color=(COLORS["bg_light"], COLORS["bg_dark"]),
            corner_radius=0,
            **kwargs
        )
        self.on_auth_success = on_auth_success

        # Center Container (Two-column layout)
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # -------------------------------------------------------------
        # Left Column: Brand, Logo, & Product Value Proposition
        # -------------------------------------------------------------
        self.brand_frame = ctk.CTkFrame(
            self.center_frame,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=20,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
            width=420,
            height=560,
        )
        self.brand_frame.pack(side="left", padx=(0, 24), pady=20)
        self.brand_frame.pack_propagate(False)

        # Brand Logo Badge
        self.logo_badge = ctk.CTkLabel(
            self.brand_frame,
            text="⚡",
            font=("Segoe UI", 32),
            width=68,
            height=68,
            fg_color=COLORS["primary"],
            text_color="white",
            corner_radius=18,
        )
        self.logo_badge.pack(anchor="w", padx=28, pady=(32, 12))

        # Brand Title & Tagline
        self.brand_title = ctk.CTkLabel(
            self.brand_frame,
            text="StudyForge AI",
            font=("Segoe UI", 26, "bold"),
            text_color=(COLORS["text_dark"], COLORS["text_light"]),
        )
        self.brand_title.pack(anchor="w", padx=28, pady=(0, 4))

        self.brand_tagline = ctk.CTkLabel(
            self.brand_frame,
            text="Your Intelligent Academic & Exam OS",
            font=FONTS["body_bold"],
            text_color=COLORS["primary"],
        )
        self.brand_tagline.pack(anchor="w", padx=28, pady=(0, 16))

        self.brand_desc = ctk.CTkLabel(
            self.brand_frame,
            text="Transform course textbooks and dense lecture notes into executive summaries, practice quizzes, and 3D flashcards with real-time learning diagnostics.",
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
            wraplength=360,
            justify="left",
        )
        self.brand_desc.pack(anchor="w", padx=28, pady=(0, 20))

        # Feature Highlights
        features = [
            ("📚", "PDF & Document Extractions", "Upload notes and extract clean text."),
            ("📑", "AI Summaries & Cram Notes", "High-yield takeaways & concept glossaries."),
            ("📝", "Adaptive Exam Quizzes", "Auto-grading with diagnostic weak topics."),
            ("🗂️", "3D Active Recall Flashcards", "Spaced repetition confidence ratings."),
        ]

        for icon, feat_title, feat_sub in features:
            f_row = ctk.CTkFrame(self.brand_frame, fg_color="transparent")
            f_row.pack(fill="x", padx=28, pady=5)

            icon_lbl = ctk.CTkLabel(
                f_row,
                text=icon,
                font=FONTS["header"],
                width=32,
                height=32,
                fg_color=(COLORS["primary_light"], "#1e3a8a"),
                corner_radius=8,
            )
            icon_lbl.pack(side="left", padx=(0, 12))

            t_box = ctk.CTkFrame(f_row, fg_color="transparent")
            t_box.pack(side="left", fill="x")

            lbl_t = ctk.CTkLabel(t_box, text=feat_title, font=FONTS["body_bold"], text_color=(COLORS["text_dark"], COLORS["text_light"]))
            lbl_t.pack(anchor="w")

            lbl_s = ctk.CTkLabel(t_box, text=feat_sub, font=FONTS["caption"], text_color=COLORS["text_muted"])
            lbl_s.pack(anchor="w")

        # -------------------------------------------------------------
        # Right Column: Login, Register, & Guest Mode Card
        # -------------------------------------------------------------
        self.auth_card = ctk.CTkFrame(
            self.center_frame,
            fg_color=(COLORS["card_light"], COLORS["card_dark"]),
            corner_radius=20,
            border_width=1,
            border_color=(COLORS["border_light"], COLORS["border_dark"]),
            width=440,
            height=560,
        )
        self.auth_card.pack(side="right", padx=(0, 0), pady=20)
        self.auth_card.pack_propagate(False)

        # Tab Segmented Button (Sign In / Register)
        self.mode_var = ctk.StringVar(value="Sign In")
        self.mode_selector = ctk.CTkSegmentedButton(
            self.auth_card,
            values=["Sign In", "Create Account"],
            variable=self.mode_var,
            font=FONTS["body_bold"],
            height=38,
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            command=self._on_mode_change,
        )
        self.mode_selector.pack(fill="x", padx=32, pady=(28, 16))

        # Dynamic Form Container
        self.form_container = ctk.CTkFrame(self.auth_card, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, padx=32, pady=0)

        # Message Label for Errors / Feedback
        self.msg_label = ctk.CTkLabel(
            self.auth_card,
            text="",
            font=FONTS["small"],
            text_color=COLORS["danger"],
            wraplength=370,
        )
        self.msg_label.pack(fill="x", padx=32, pady=(4, 6))

        # Guest Mode Divider & Button
        self.divider_row = ctk.CTkFrame(self.auth_card, fg_color="transparent")
        self.divider_row.pack(fill="x", padx=32, pady=(4, 10))

        self.div_line = ctk.CTkLabel(
            self.divider_row,
            text="────────  OR  ────────",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"],
        )
        self.div_line.pack(expand=True)

        self.guest_btn = ctk.CTkButton(
            self.auth_card,
            text="🚀  Continue as Guest (1-Click Instant Access)",
            font=FONTS["body_bold"],
            height=44,
            corner_radius=12,
            fg_color=(COLORS["primary_light"], "#1e3a8a"),
            text_color=(COLORS["primary"], "#93c5fd"),
            hover_color=(COLORS["primary_border"], "#1e40af"),
            command=self._handle_guest_login,
        )
        self.guest_btn.pack(fill="x", padx=32, pady=(0, 24))

        # Render initial form (Sign In)
        self._render_login_form()

    def _on_mode_change(self, mode: str):
        self.msg_label.configure(text="")
        if mode == "Sign In":
            self._render_login_form()
        else:
            self._render_register_form()

    def _render_login_form(self):
        for w in self.form_container.winfo_children():
            w.destroy()

        lbl_user = ctk.CTkLabel(self.form_container, text="Username or Email:", font=FONTS["small"], text_color=COLORS["text_muted"])
        lbl_user.pack(anchor="w", pady=(4, 2))

        self.login_user_entry = ctk.CTkEntry(
            self.form_container,
            placeholder_text="e.g. tan or tan@studyforge.ai",
            height=38,
            font=FONTS["body"],
        )
        self.login_user_entry.pack(fill="x", pady=(0, 10))

        lbl_pwd = ctk.CTkLabel(self.form_container, text="Password:", font=FONTS["small"], text_color=COLORS["text_muted"])
        lbl_pwd.pack(anchor="w", pady=(0, 2))

        self.login_pwd_entry = ctk.CTkEntry(
            self.form_container,
            placeholder_text="Enter your password",
            height=38,
            font=FONTS["body"],
            show="•",
        )
        self.login_pwd_entry.pack(fill="x", pady=(0, 14))

        # Enter key triggers sign in
        self.login_pwd_entry.bind("<Return>", lambda e: self._handle_signin())

        self.signin_btn = ctk.CTkButton(
            self.form_container,
            text="Sign In",
            font=FONTS["body_bold"],
            height=42,
            corner_radius=12,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._handle_signin,
        )
        self.signin_btn.pack(fill="x", pady=(4, 8))

        hint_lbl = ctk.CTkLabel(
            self.form_container,
            text="Default account: tan  |  password: password123",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"],
        )
        hint_lbl.pack()

    def _render_register_form(self):
        for w in self.form_container.winfo_children():
            w.destroy()

        lbl_name = ctk.CTkLabel(self.form_container, text="Full Name:", font=FONTS["caption"], text_color=COLORS["text_muted"])
        lbl_name.pack(anchor="w", pady=(0, 1))

        self.reg_name_entry = ctk.CTkEntry(self.form_container, placeholder_text="e.g. Dinesh Kumar", height=34, font=FONTS["small"])
        self.reg_name_entry.pack(fill="x", pady=(0, 6))

        lbl_user = ctk.CTkLabel(self.form_container, text="Username:", font=FONTS["caption"], text_color=COLORS["text_muted"])
        lbl_user.pack(anchor="w", pady=(0, 1))

        self.reg_user_entry = ctk.CTkEntry(self.form_container, placeholder_text="e.g. deardk14", height=34, font=FONTS["small"])
        self.reg_user_entry.pack(fill="x", pady=(0, 6))

        lbl_email = ctk.CTkLabel(self.form_container, text="Email Address:", font=FONTS["caption"], text_color=COLORS["text_muted"])
        lbl_email.pack(anchor="w", pady=(0, 1))

        self.reg_email_entry = ctk.CTkEntry(self.form_container, placeholder_text="e.g. dk@example.com", height=34, font=FONTS["small"])
        self.reg_email_entry.pack(fill="x", pady=(0, 6))

        lbl_pwd = ctk.CTkLabel(self.form_container, text="Password:", font=FONTS["caption"], text_color=COLORS["text_muted"])
        lbl_pwd.pack(anchor="w", pady=(0, 1))

        self.reg_pwd_entry = ctk.CTkEntry(self.form_container, placeholder_text="Create password (min 4 chars)", height=34, font=FONTS["small"], show="•")
        self.reg_pwd_entry.pack(fill="x", pady=(0, 10))

        self.register_btn = ctk.CTkButton(
            self.form_container,
            text="Create Account & Start Learning",
            font=FONTS["body_bold"],
            height=38,
            corner_radius=12,
            fg_color="#059669",
            hover_color="#047857",
            command=self._handle_register,
        )
        self.register_btn.pack(fill="x", pady=(4, 0))

    def _handle_signin(self):
        ident = self.login_user_entry.get().strip()
        pwd = self.login_pwd_entry.get().strip()

        if not ident:
            self.msg_label.configure(text="Please enter your username or email.", text_color=COLORS["danger"])
            return
        if not pwd:
            self.msg_label.configure(text="Please enter your password.", text_color=COLORS["danger"])
            return

        res = UserModel.authenticate(ident, pwd)
        if res.get("success"):
            user = res["user"]
            user["is_guest"] = False
            self.on_auth_success(user)
        else:
            self.msg_label.configure(text=f"❌ {res.get('error', 'Sign in failed')}", text_color=COLORS["danger"])

    def _handle_register(self):
        name = self.reg_name_entry.get().strip()
        user = self.reg_user_entry.get().strip()
        email = self.reg_email_entry.get().strip()
        pwd = self.reg_pwd_entry.get().strip()

        if not name:
            self.msg_label.configure(text="Please enter your full name.", text_color=COLORS["danger"])
            return
        if not user:
            self.msg_label.configure(text="Please choose a username.", text_color=COLORS["danger"])
            return
        if not email or "@" not in email:
            self.msg_label.configure(text="Please enter a valid email address.", text_color=COLORS["danger"])
            return
        if len(pwd) < 4:
            self.msg_label.configure(text="Password must be at least 4 characters long.", text_color=COLORS["danger"])
            return

        res = UserModel.create_user(name, user, email, pwd)
        if res.get("success"):
            user_data = {
                "id": res["user_id"],
                "name": name,
                "username": user,
                "email": email,
                "is_guest": False,
            }
            self.on_auth_success(user_data)
        else:
            self.msg_label.configure(text=f"❌ {res.get('error')}", text_color=COLORS["danger"])

    def _handle_guest_login(self):
        guest_user = {
            "id": 0,
            "name": "Guest Student",
            "username": "guest",
            "email": "guest@studyforge.local",
            "is_guest": True,
        }
        self.on_auth_success(guest_user)
