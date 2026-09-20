"""Main Application Window for StudyForge AI Desktop GUI."""
import customtkinter as ctk
from gui.theme import init_theme, COLORS
from gui.auth_view import AuthView
from gui.sidebar import Sidebar
from gui.header import Header
from gui.dashboard_view import DashboardView
from gui.documents_view import DocumentsView
from gui.summaries_view import SummariesView
from gui.questions_view import QuestionsView
from gui.quiz_view import QuizView
from gui.flashcards_view import FlashcardsView
from gui.notebook_view import NotebookView
from gui.analytics_view import AnalyticsView
from gui.settings_view import SettingsView
from database.connection import init_db

class MainWindow(ctk.CTk):
    def __init__(self, start_authenticated: bool = False):
        super().__init__()
        
        # 1. Initialize Theme & Database
        init_theme()
        init_db()

        # 2. Window Configuration
        self.title("StudyForge AI • Desktop Learning OS")
        self.geometry("1180x760")
        self.minsize(1020, 680)
        self.configure(fg_color=(COLORS["bg_light"], COLORS["bg_dark"]))

        # Current User State
        self.current_user = None

        # Main App Layout Widgets (created upon authentication)
        self.auth_view = None
        self.sidebar = None
        self.right_container = None
        self.header = None
        self.content_area = None
        self.current_view = None

        self.page_subtitles = {
            "Dashboard": "Welcome back! Let's make today count.",
            "My Documents": "Manage course notes, textbooks, and PDF extractions.",
            "AI Summaries": "High-yield executive summaries and key concept glossaries.",
            "Question Generator": "Synthesize exam questions with options and explanations.",
            "Quiz": "Interactive multiple choice assessment with weak topic diagnostics.",
            "Flashcards": "Active recall study decks with spaced repetition ratings.",
            "My Notebook": "Personal study scratchpad and lecture notes repository.",
            "Analytics": "Performance mastery breakdown driven by real quiz attempts.",
            "Settings": "AI engine configuration, appearance themes, and diagnostics.",
        }

        if start_authenticated:
            # For direct testing
            self._on_auth_success({"name": "Tan", "username": "tan", "is_guest": False})
        else:
            # Show Landing Home Screen with Login / Register / Guest Mode
            self.show_auth_screen()

    def show_auth_screen(self):
        """Displays the home landing screen with brand logo, login, register, and guest mode."""
        # Clear main app layout if active
        if self.sidebar:
            self.sidebar.destroy()
            self.sidebar = None
        if self.right_container:
            self.right_container.destroy()
            self.right_container = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.auth_view = AuthView(self, on_auth_success=self._on_auth_success)
        self.auth_view.grid(row=0, column=0, sticky="nsew")

    def _on_auth_success(self, user: dict):
        """Transition from Landing screen to main study operations dashboard."""
        self.current_user = user

        # Remove Auth View
        if self.auth_view:
            self.auth_view.destroy()
            self.auth_view = None

        # Configure Grid for Sidebar + Content
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Mount Sidebar on left
        self.sidebar = Sidebar(self, on_navigate=self.navigate)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Mount Right Container (Header + Dynamic Content Area)
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew")
        self.right_container.grid_rowconfigure(0, weight=0)
        self.right_container.grid_rowconfigure(1, weight=1)
        self.right_container.grid_columnconfigure(0, weight=1)

        self.header = Header(
            self.right_container,
            on_theme_toggle=self._on_theme_toggle,
            on_logout=self.logout,
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.set_user_name(user.get("name", "Student"))

        self.content_area = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        # View Factories
        self.view_factories = {
            "Dashboard": lambda: DashboardView(self.content_area, navigate_fn=self.navigate),
            "My Documents": lambda: DocumentsView(self.content_area, navigate_fn=self.navigate),
            "AI Summaries": lambda: SummariesView(self.content_area, navigate_fn=self.navigate),
            "Question Generator": lambda: QuestionsView(self.content_area, navigate_fn=self.navigate),
            "Quiz": lambda: QuizView(self.content_area, navigate_fn=self.navigate, on_stats_updated=self.header.update_user_stats),
            "Flashcards": lambda: FlashcardsView(self.content_area, navigate_fn=self.navigate, on_stats_updated=self.header.update_user_stats),
            "My Notebook": lambda: NotebookView(self.content_area, navigate_fn=self.navigate),
            "Analytics": lambda: AnalyticsView(self.content_area, navigate_fn=self.navigate),
            "Settings": lambda: SettingsView(self.content_area, navigate_fn=self.navigate, on_theme_toggle=self._on_theme_toggle),
        }

        # Navigate to Dashboard
        self.navigate("Dashboard")

    def navigate(self, page_id: str):
        """Switches the active view in the content frame."""
        if not self.sidebar or not self.content_area:
            return

        if page_id not in self.view_factories:
            page_id = "Dashboard"

        self.sidebar.set_active(page_id)

        sub = self.page_subtitles.get(page_id, "")
        self.header.set_title(page_id, sub)
        self.header.update_user_stats()

        if self.current_view:
            self.current_view.destroy()

        self.current_view = self.view_factories[page_id]()
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        """Logs out the user and returns to the Home Landing Screen."""
        self.current_user = None
        self.show_auth_screen()

    def _on_theme_toggle(self, new_mode: str):
        if self.header:
            self.header.update_user_stats()

def run_app():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    run_app()
