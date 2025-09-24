# views.py
# Contains all the UI classes and widgets.

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGridLayout, QFrame, QScrollArea, QSizePolicy, QSpacerItem,
    QStackedWidget, QDialog, QMessageBox, QTabWidget, QFormLayout, QDateEdit,
    QCalendarWidget, QProgressBar
)
from PyQt6.QtGui import QPixmap, QIcon, QFont, QFontDatabase, QColor
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# Global style sheet for consistent theming
STYLE_SHEET = """
QWidget {
    font-family: 'Inter', sans-serif;
    background-color: #F0F4F8; /* Light Blue-Gray */
    color: #334155; /* Dark Slate Blue */
}
QFrame#main_frame {
    background-color: #F8FAFC;
    border-radius: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
#header_frame {
    background-color: #DBEAFE; /* Calming Blue */
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
}
QLabel#title_label {
    font-size: 36px;
    font-weight: 700;
    color: #1E293B; /* Darker Slate Blue */
    padding: 10px;
}
QLabel#subtitle_label {
    font-size: 18px;
    color: #475569;
    padding: 0 10px 10px 10px;
}
QLineEdit, QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px;
    font-size: 14px;
}
QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #3B82F6; /* Brighter Blue for focus */
}
QPushButton {
    background-color: #F97316; /* Warm Orange */
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 600;
    padding: 12px 24px;
    border-radius: 12px;
    border: none;
    transition: background-color 0.3s ease;
}
QPushButton:hover {
    background-color: #EA580C; /* Darker Orange on hover */
}
QPushButton:pressed {
    background-color: #C2410C; /* Even darker on press */
}
QPushButton#secondary_btn {
    background-color: #64748B;
}
QPushButton#secondary_btn:hover {
    background-color: #4B5563;
}
QDialog {
    background-color: #F8FAFC;
    border-radius: 16px;
}
QMessageBox {
    background-color: #F8FAFC;
}
QProgressBar {
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    text-align: center;
    background-color: #E2E8F0;
}
QProgressBar::chunk {
    background-color: #F97316;
    border-radius: 6px;
}
QToolTip {
    border: 1px solid #1E293B;
    background-color: #1E293B;
    color: #E2E8F0;
    padding: 5px;
    border-radius: 6px;
    font-size: 12px;
}
#pet_card, #service_card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
#pet_card:hover, #service_card:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
"""

class PetCard(QFrame):
    """A clickable card widget for displaying a pet."""
    def __init__(self, pet_data, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setObjectName("pet_card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(200, 250)
        self.pet_data = pet_data

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Image Placeholder
        image_label = QLabel()
        image_label.setPixmap(self.get_image(pet_data['image_path']).scaled(200, 150, Qt.AspectRatioMode.KeepAspectFit))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setObjectName("pet_image")
        image_label.setAccessibleName(f"Photo of {pet_data['name']}")
        layout.addWidget(image_label)

        # Pet Info
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(10, 5, 10, 5)

        name_label = QLabel(f"<b>{pet_data['name']}</b>")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(name_label)
        
        breed_label = QLabel(f"<small>{pet_data['breed']}</small>")
        breed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(breed_label)
        
        layout.addWidget(info_widget)
        
        self.setLayout(layout)
        self.setToolTip(f"<b>{pet_data['name']}</b><br><small>Age: {pet_data['age']} years</small><br><small>Breed: {pet_data['breed']}</small><br><br>{pet_data['description']}")

    def get_image(self, path):
        """Loads an image or returns a placeholder."""
        try:
            pixmap = QPixmap(f"assets/{path}")
            if not pixmap.isNull():
                return pixmap
        except Exception as e:
            pass
        # Fallback to a placeholder
        placeholder = QPixmap(200, 150)
        placeholder.fill(QColor("#E2E8F0"))
        # Add a simple dog/cat icon
        # Placeholder for qtawesome or custom icon
        return placeholder

class ServiceCard(QFrame):
    """A clickable card widget for a service."""
    def __init__(self, service_data, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setObjectName("service_card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(200, 250)
        self.service_data = service_data

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Service Name
        name_label = QLabel(f"<b>{service_data['name']}</b>")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Service Description
        desc_label = QLabel(service_data['description'])
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # Price
        price_label = QLabel(f"<br><b>${service_data['price']:.2f}</b>")
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(price_label)

        layout.addStretch()
        self.setLayout(layout)

class Breadcrumbs(QFrame):
    """Custom widget for breadcrumb navigation."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)
        self.setObjectName("breadcrumbs")
        self.steps = []
    
    def set_steps(self, steps):
        """Sets the breadcrumb steps."""
        # Clear existing buttons
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        self.steps = steps
        for i, step in enumerate(steps):
            btn = QPushButton(step)
            btn.setObjectName("breadcrumb_btn")
            btn.setFlat(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.layout.addWidget(btn)
            if i < len(steps) - 1:
                arrow = QLabel(" > ")
                self.layout.addWidget(arrow)

class MainView(QMainWindow):
    """The main window of the application, managing all sub-views."""
    
    # Signals for communicating with the controller
    navigate_to_pet_details = pyqtSignal(int)
    navigate_to_service_details = pyqtSignal(int)
    search_triggered = pyqtSignal(str)
    filter_triggered = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OnlyPets - Pet Adoption & Services")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(STYLE_SHEET)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create all views
        self.home_view = self.create_home_view()
        self.pet_list_view = self.create_pet_list_view()
        self.service_list_view = self.create_service_list_view()
        self.user_dashboard_view = self.create_user_dashboard_view()
        
        self.stacked_widget.addWidget(self.home_view)
        self.stacked_widget.addWidget(self.pet_list_view)
        self.stacked_widget.addWidget(self.service_list_view)
        self.stacked_widget.addWidget(self.user_dashboard_view)

        self.setup_ui()
        self.show_home_view()
        
    def setup_ui(self):
        """Sets up the main layout and widgets."""
        self.main_frame = QFrame()
        self.main_frame.setObjectName("main_frame")
        self.main_layout = QVBoxLayout(self.main_frame)
        
        # Header Frame
        header_frame = QFrame()
        header_frame.setObjectName("header_frame")
        header_layout = QVBoxLayout(header_frame)
        self.title_label = QLabel("OnlyPets")
        self.title_label.setObjectName("title_label")
        self.subtitle_label = QLabel("Your one-stop shop for pet adoption and care.")
        self.subtitle_label.setObjectName("subtitle_label")
        header_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Top bar with login/logout
        self.top_bar = QFrame()
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.user_label = QLabel("Guest")
        self.auth_button = QPushButton("Login / Signup")
        self.auth_button.setObjectName("secondary_btn")
        self.top_bar_layout.addWidget(self.user_label)
        self.top_bar_layout.addStretch()
        self.top_bar_layout.addWidget(self.auth_button)
        
        # Breadcrumbs and progress bar
        self.progress_frame = QFrame()
        self.progress_layout = QVBoxLayout(self.progress_frame)
        self.breadcrumbs = Breadcrumbs()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_layout.addWidget(self.breadcrumbs)
        self.progress_layout.addWidget(self.progress_bar)
        
        self.main_layout.addWidget(self.top_bar)
        self.main_layout.addWidget(self.progress_frame)
        self.main_layout.addWidget(self.stacked_widget)
        self.setCentralWidget(self.main_frame)

    def create_home_view(self):
        """Creates the main home dashboard view."""
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        
        # Sections for Pets and Services
        self.pets_section = self.create_section("Adopt a Pet", "See All Pets")
        self.services_section = self.create_section("Book Services", "See All Services")
        
        layout.addWidget(self.pets_section)
        layout.addWidget(self.services_section)
        layout.addStretch()
        
        return home_widget

    def create_user_dashboard_view(self):
        """Creates the personalized user dashboard view."""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        
        self.welcome_label = QLabel("Welcome, User!")
        self.welcome_label.setFont(QFont("Inter", 24, QFont.Bold))
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.welcome_label)
        
        self.adoptions_section = self.create_user_section("Your Adopted Pets")
        self.bookings_section = self.create_user_section("Your Service Bookings")
        
        layout.addWidget(self.adoptions_section)
        layout.addWidget(self.bookings_section)
        layout.addStretch()
        
        return dashboard_widget

    def create_user_section(self, title):
        """Helper to create a section for the user dashboard."""
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        
        section_label = QLabel(f"<h3>{title}</h3>")
        frame_layout.addWidget(section_label)
        
        grid = QGridLayout()
        # Placeholder grid, populated by controller
        frame_layout.addLayout(grid)
        return frame

    def create_section(self, title, button_text):
        """Helper to create a browsable section for the home view."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f"<h2>{title}</h2>"))
        header_layout.addStretch()
        view_all_btn = QPushButton(button_text)
        view_all_btn.setObjectName("secondary_btn")
        header_layout.addWidget(view_all_btn)
        layout.addLayout(header_layout)

        # Placeholder grid, will be populated by controller
        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(grid_widget)
        
        return frame
    
    def create_pet_list_view(self):
        """Creates the full pet browsing view."""
        pet_list_widget = QWidget()
        layout = QVBoxLayout(pet_list_widget)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for a pet...")
        self.search_btn = QPushButton("Search")
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        # Scroll area for pet cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.pet_grid_widget = QWidget()
        self.pet_grid_layout = QGridLayout(self.pet_grid_widget)
        self.pet_grid_layout.setSpacing(20)
        self.pet_grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        scroll_area.setWidget(self.pet_grid_widget)
        layout.addWidget(scroll_area)
        
        return pet_list_widget

    def create_service_list_view(self):
        """Creates the full service browsing view."""
        service_list_widget = QWidget()
        layout = QVBoxLayout(service_list_widget)

        self.service_search_input = QLineEdit()
        self.service_search_input.setPlaceholderText("Search for a service...")
        self.service_search_btn = QPushButton("Search")

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.service_search_input)
        search_layout.addWidget(self.service_search_btn)
        layout.addLayout(search_layout)

        # Scroll area for service cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.service_grid_widget = QWidget()
        self.service_grid_layout = QGridLayout(self.service_grid_widget)
        self.service_grid_layout.setSpacing(20)
        self.service_grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        scroll_area.setWidget(self.service_grid_widget)
        layout.addWidget(scroll_area)

        return service_list_widget
    
    def clear_grid_layout(self, layout):
        """Helper to clear a grid layout."""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                    
    def show_home_view(self):
        """Displays the home view."""
        self.stacked_widget.setCurrentWidget(self.home_view)
        
    def show_pet_list_view(self):
        """Displays the pet list view."""
        self.stacked_widget.setCurrentWidget(self.pet_list_view)
        
    def show_service_list_view(self):
        """Displays the service list view."""
        self.stacked_widget.setCurrentWidget(self.service_list_view)
        
    def show_user_dashboard(self, username):
        """Displays the personalized user dashboard."""
        self.welcome_label.setText(f"Welcome, {username}!")
        self.stacked_widget.setCurrentWidget(self.user_dashboard_view)

    def display_pets(self, pet_data_list):
        """Populates the pet grid with cards."""
        self.clear_grid_layout(self.pet_grid_layout)
        col_count = 4
        for i, pet_data in enumerate(pet_data_list):
            card = PetCard(pet_data)
            self.pet_grid_layout.addWidget(card, i // col_count, i % col_count)

    def display_services(self, service_data_list):
        """Populates the service grid with cards."""
        self.clear_grid_layout(self.service_grid_layout)
        col_count = 4
        for i, service_data in enumerate(service_data_list):
            card = ServiceCard(service_data)
            self.service_grid_layout.addWidget(card, i // col_count, i % col_count)

class AuthDialog(QDialog):
    """Modal dialog for user authentication (login/signup)."""
    
    login_attempt = pyqtSignal(str, str)
    signup_attempt = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Authentication")
        self.setFixedSize(400, 450)
        self.setModal(True)
        self.setStyleSheet(STYLE_SHEET)
        
        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_login_tab(), "Login")
        self.tab_widget.addTab(self.create_signup_tab(), "Signup")
        
        layout.addWidget(self.tab_widget)
    
    def create_login_tab(self):
        """Creates the login form tab."""
        login_widget = QWidget()
        form_layout = QFormLayout(login_widget)
        
        self.login_username_input = QLineEdit()
        self.login_username_input.setPlaceholderText("Enter your username")
        self.login_password_input = QLineEdit()
        self.login_password_input.setPlaceholderText("Enter your password")
        self.login_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.on_login_click)
        
        self.login_error_label = QLabel("")
        self.login_error_label.setStyleSheet("color: #EF4444;")
        
        form_layout.addRow("Username:", self.login_username_input)
        form_layout.addRow("Password:", self.login_password_input)
        form_layout.addRow("", login_btn)
        form_layout.addRow("", self.login_error_label)
        
        return login_widget
        
    def create_signup_tab(self):
        """Creates the signup form tab."""
        signup_widget = QWidget()
        form_layout = QFormLayout(signup_widget)
        
        self.signup_username_input = QLineEdit()
        self.signup_username_input.setPlaceholderText("Choose a username")
        self.signup_email_input = QLineEdit()
        self.signup_email_input.setPlaceholderText("Enter your email")
        self.signup_password_input = QLineEdit()
        self.signup_password_input.setPlaceholderText("Create a password")
        self.signup_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.signup_username_input.textChanged.connect(self.validate_signup_form)
        self.signup_email_input.textChanged.connect(self.validate_signup_form)
        self.signup_password_input.textChanged.connect(self.validate_signup_form)
        
        signup_btn = QPushButton("Sign Up")
        signup_btn.clicked.connect(self.on_signup_click)
        
        self.signup_error_label = QLabel("")
        self.signup_error_label.setStyleSheet("color: #EF4444;")
        
        form_layout.addRow("Username:", self.signup_username_input)
        form_layout.addRow("Email:", self.signup_email_input)
        form_layout.addRow("Password:",self.signup_password_input)
        form_layout.addRow("", signup_btn)
        form_layout.addRow("", self.signup_error_label)

        return signup_widget

    def validate_signup_form(self):
        """Performs basic form validation on the fly."""
        username = self.signup_username_input.text().strip()
        email = self.signup_email_input.text().strip()
        password = self.signup_password_input.text().strip()

        is_valid = True

        if not username:
            self.signup_username_input.setStyleSheet("border: 2px solid #EF4444;")
            self.signup_username_input.setToolTip("Username cannot be empty.")
            is_valid = False
        else:
            self.signup_username_input.setStyleSheet("")
            self.signup_username_input.setToolTip("")

        if not email or "@" not in email:
            self.signup_email_input.setStyleSheet("border: 2px solid #EF4444;")
            self.signup_email_input.setToolTip("Please enter a valid email address.")
            is_valid = False
        else:
            self.signup_email_input.setStyleSheet("")
            self.signup_email_input.setToolTip("")

        if len(password) < 6:
            self.signup_password_input.setStyleSheet("border: 2px solid #EF4444;")
            self.signup_password_input.setToolTip("Password must be at least 6 characters long.")
            is_valid = False
        else:
            self.signup_password_input.setStyleSheet("")
            self.signup_password_input.setToolTip("")

        return is_valid

    def on_login_click(self):
        username = self.login_username_input.text().strip()
        password = self.login_password_input.text().strip()
        if username and password:
            self.login_attempt.emit(username, password)
        else:
            self.login_error_label.setText("Please enter username and password.")

    def on_signup_click(self):
        if self.validate_signup_form():
            username = self.signup_username_input.text().strip()
            email = self.signup_email_input.text().strip()
            password = self.signup_password_input.text().strip()
            self.signup_attempt.emit(username, email, password)
        else:
            self.signup_error_label.setText("Please fix the highlighted errors.")

class PetDetailsDialog(QDialog):
    """Modal dialog for displaying detailed pet information."""
    adopt_pet = pyqtSignal(dict)

    def __init__(self, pet_data, parent=None):
        super().__init__(parent)
        self.pet_data = pet_data
        self.setWindowTitle(f"Meet {pet_data['name']}")
        self.setFixedSize(600, 600)
        self.setStyleSheet(STYLE_SHEET)

        layout = QVBoxLayout(self)

        info_layout = QHBoxLayout()
        image_label = QLabel()
        image_label.setPixmap(QPixmap(f"assets/{pet_data['image_path']}").scaled(250, 250, Qt.AspectRatioMode.KeepAspectFit))
        image_label.setAccessibleName(f"Photo of {pet_data['name']}")
        info_layout.addWidget(image_label)

        details_layout = QVBoxLayout()
        details_layout.addWidget(QLabel(f"<h2>{pet_data['name']}</h2>"))
        details_layout.addWidget(QLabel(f"<b>Breed:</b> {pet_data['breed']}"))
        details_layout.addWidget(QLabel(f"<b>Age:</b> {pet_data['age']} years"))
        details_layout.addWidget(QLabel(f"<b>Description:</b><br>{pet_data['description']}"))
        details_layout.addStretch()

        info_layout.addLayout(details_layout)
        layout.addLayout(info_layout)

        adopt_btn = QPushButton(f"Adopt {pet_data['name']}")
        adopt_btn.clicked.connect(lambda: self.adopt_pet.emit(self.pet_data))
        layout.addWidget(adopt_btn)

class AdoptionFormDialog(QDialog):
    """Modal dialog for the adoption application form."""
    form_submitted = pyqtSignal(dict)

    def __init__(self, pet_data, parent=None):
        super().__init__(parent)
        self.pet_data = pet_data
        self.setWindowTitle(f"Adopt {pet_data['name']}")
        self.setFixedSize(500, 400)
        self.setStyleSheet(STYLE_SHEET)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<h2>Adoption Application for {pet_data['name']}</h2>"))

        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.reason_input = QLineEdit()

        form_layout.addRow("Your Name:", self.name_input)
        form_layout.addRow("Your Email:", self.email_input)
        form_layout.addRow("Reason for Adoption:", self.reason_input)

        layout.addLayout(form_layout)

        submit_btn = QPushButton("Submit Application")
        submit_btn.clicked.connect(self.on_submit)
        layout.addWidget(submit_btn)

    def on_submit(self):
        data = {
            "name": self.name_input.text(),
            "email": self.email_input.text(),
            "reason": self.reason_input.text(),
            "pet_id": self.pet_data['id']
        }
        self.form_submitted.emit(data)
        self.accept()

class ServiceDetailsDialog(QDialog):
    """Modal dialog for a service's details."""
    book_service = pyqtSignal(dict)

    def __init__(self, service_data, parent=None):
        super().__init__(parent)
        self.service_data = service_data
        self.setWindowTitle(f"Service: {service_data['name']}")
        self.setFixedSize(500, 400)
        self.setStyleSheet(STYLE_SHEET)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<h2>{service_data['name']}</h2>"))
        layout.addWidget(QLabel(f"<b>Price:</b> ${service_data['price']:.2f}"))
        layout.addWidget(QLabel(f"<br><b>Description:</b><br>{service_data['description']}"))

        layout.addStretch()

        book_btn = QPushButton(f"Book This Service")
        book_btn.clicked.connect(lambda: self.book_service.emit(self.service_data))
        layout.addWidget(book_btn)

class ScheduleDialog(QDialog):
    """Modal dialog for scheduling a service."""
    schedule_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Schedule Your Service")
        self.setFixedSize(400, 450)
        self.setStyleSheet(STYLE_SHEET)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Select a Date</h2>"))

        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)

        select_btn = QPushButton("Select Date & Continue")
        select_btn.clicked.connect(self.on_select)
        layout.addWidget(select_btn)

    def on_select(self):
        selected_date = self.calendar.selectedDate().toString(Qt.DateFormat.ISODate)
        self.schedule_selected.emit(selected_date)
        self.accept()

class ConfirmationDialog(QDialog):
    """Modal dialog for confirmation message."""
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmation")
        self.setFixedSize(400, 200)
        self.setStyleSheet(STYLE_SHEET)

        layout = QVBoxLayout(self)
        label = QLabel(f"<h3 align='center'>{message}</h3>")
        label.setWordWrap(True)
        layout.addWidget(label)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
