# views.py
# Contains all the UI classes and widgets using CustomTkinter.

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

# --- Constants for Theming ---
COLORS = {
    "bg_light": "#F0F4F8",
    "bg_dark": "#F8FAFC",
    "text": "#334155",
    "text_dark": "#1E293B",
    "primary": "#F97316",
    "primary_hover": "#EA580C",
    "secondary": "#64748B",
    "border": "#CBD5E1"
}

FONTS = {
    "title": ("Inter", 36, "bold"),
    "subtitle": ("Inter", 18),
    "header": ("Inter", 24, "bold"),
    "body_bold": ("Inter", 16, "bold"),
    "body": ("Inter", 14),
}

class PetCard(ctk.CTkFrame):
    """A clickable card widget for displaying a pet."""
    def __init__(self, master, pet_data, command):
        super().__init__(master, corner_radius=12, fg_color="white", border_color=COLORS["border"], border_width=1)
        self.pet_data = pet_data

        # --- Image ---
        try:
            img = Image.open(f"assets/{pet_data['image_path']}")
            ctk_img = ctk.CTkImage(light_image=img, size=(180, 135))
            image_label = ctk.CTkLabel(self, image=ctk_img, text="")
            image_label.pack(pady=(10, 5))
        except Exception as e:
            # Placeholder if image fails to load
            placeholder = ctk.CTkFrame(self, width=180, height=135, fg_color=COLORS["bg_light"])
            placeholder.pack(pady=(10, 5))
            logging.warning(f"Could not load image {pet_data['image_path']}: {e}")

        # --- Info ---
        ctk.CTkLabel(self, text=pet_data['name'], font=FONTS["body_bold"], text_color=COLORS["text_dark"]).pack()
        ctk.CTkLabel(self, text=pet_data['breed'], font=FONTS["body"], text_color=COLORS["text"]).pack(pady=(0, 10))

        # --- Bind Click Event ---
        self.bind("<Button-1>", lambda event: command(self.pet_data))
        for child in self.winfo_children():
            child.bind("<Button-1>", lambda event: command(self.pet_data))

class ServiceCard(ctk.CTkFrame):
    """A clickable card widget for a service."""
    def __init__(self, master, service_data, command):
        super().__init__(master, corner_radius=12, fg_color="white", border_color=COLORS["border"], border_width=1)
        self.service_data = service_data
        
        self.grid_rowconfigure(2, weight=1) # Allow description to expand
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text=service_data['name'], font=FONTS["body_bold"]).grid(row=0, column=0, pady=(15, 5), sticky="n")
        ctk.CTkLabel(self, text=f"${service_data['price']:.2f}", font=FONTS["body_bold"], text_color=COLORS["primary"]).grid(row=1, column=0, pady=5)
        ctk.CTkLabel(self, text=service_data['description'], wraplength=180, font=FONTS["body"]).grid(row=2, column=0, pady=5, sticky="nsew")

        self.bind("<Button-1>", lambda event: command(self.service_data))
        for child in self.winfo_children():
            child.bind("<Button-1>", lambda event: command(self.service_data))

class MainView(ctk.CTk):
    """The main window of the application."""
    def __init__(self):
        super().__init__(fg_color=COLORS["bg_light"])
        self.title("OnlyPets - Pet Adoption & Services")
        self.geometry("1100x750")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # --- Top Bar ---
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.user_label = ctk.CTkLabel(top_bar, text="Guest", font=FONTS["body"])
        self.user_label.pack(side="left")
        self.auth_button = ctk.CTkButton(top_bar, text="Login / Signup", fg_color=COLORS["secondary"])
        self.auth_button.pack(side="right")
        
        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(header_frame, text="OnlyPets", font=FONTS["title"], text_color=COLORS["text_dark"]).pack()
        ctk.CTkLabel(header_frame, text="Your one-stop shop for pet adoption and care.", font=FONTS["subtitle"], text_color=COLORS["text"]).pack()

        # --- Main Content Area (Stacked Frames) ---
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_rowconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage, PetListPage, ServiceListPage):
            page_name = F.__name__
            frame = F(master=main_content)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        """Shows a frame for the given page name."""
        frame = self.frames[page_name]
        frame.tkraise()

    def clear_grid(self, frame):
        """Helper to clear all widgets from a frame."""
        for widget in frame.winfo_children():
            widget.destroy()

# --- Page Frames ---

class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        
        # These frames will be populated by the controller
        self.pets_section = self._create_section("Adopt a Pet")
        self.pets_section.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.pet_grid = self.pets_section.grid_frame
        
        self.services_section = self._create_section("Book Services")
        self.services_section.grid(row=1, column=0, sticky="ew")
        self.service_grid = self.services_section.grid_frame

    def _create_section(self, title):
        section = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=16)
        section.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(header, text=title, font=FONTS["header"]).pack(side="left")
        section.see_all_button = ctk.CTkButton(header, text="See All", fg_color=COLORS["secondary"])
        section.see_all_button.pack(side="right")

        # This frame will hold the cards
        section.grid_frame = ctk.CTkFrame(section, fg_color="transparent")
        section.grid_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=20)

        return section

class PetListPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Search and Controls ---
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.home_button = ctk.CTkButton(controls_frame, text="< Back to Home", fg_color=COLORS["secondary"])
        self.home_button.pack(side="left")
        
        self.search_entry = ctk.CTkEntry(controls_frame, placeholder_text="Search for a pet...", width=300)
        self.search_entry.pack(side="left", padx=20)
        self.search_button = ctk.CTkButton(controls_frame, text="Search")
        self.search_button.pack(side="left")

        # --- Scrollable Grid for Pets ---
        scrollable_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"], corner_radius=16)
        scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.pet_grid = scrollable_frame

class ServiceListPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # --- Search and Controls ---
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.home_button = ctk.CTkButton(controls_frame, text="< Back to Home", fg_color=COLORS["secondary"])
        self.home_button.pack(side="left")

        self.search_entry = ctk.CTkEntry(controls_frame, placeholder_text="Search for a service...", width=300)
        self.search_entry.pack(side="left", padx=20)
        self.search_button = ctk.CTkButton(controls_frame, text="Search")
        self.search_button.pack(side="left")

        # --- Scrollable Grid for Services ---
        scrollable_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"], corner_radius=16)
        scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.service_grid = scrollable_frame

# --- Dialog Windows ---

class AuthDialog(ctk.CTkToplevel):
    """Modal dialog for user authentication (login/signup)."""
    def __init__(self, master):
        super().__init__(master)
        self.title("Authentication")
        self.geometry("400x450")
        self.transient(master) # Keep on top of the main window
        self.grab_set() # Modal behavior

        self.controller_callbacks = {}
        
        tab_view = ctk.CTkTabview(self, fg_color=COLORS["bg_dark"])
        tab_view.pack(expand=True, fill="both", padx=20, pady=20)
        tab_view.add("Login")
        tab_view.add("Signup")
        
        self._create_login_tab(tab_view.tab("Login"))
        self._create_signup_tab(tab_view.tab("Signup"))
        
    def _create_login_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(tab, text="Username").grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.login_user_entry = ctk.CTkEntry(tab)
        self.login_user_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        ctk.CTkLabel(tab, text="Password").grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.login_pass_entry = ctk.CTkEntry(tab, show="*")
        self.login_pass_entry.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        login_btn = ctk.CTkButton(tab, text="Login", command=self.on_login_click)
        login_btn.grid(row=4, column=0, padx=20, pady=20)

    def _create_signup_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(tab, text="Username").grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.signup_user_entry = ctk.CTkEntry(tab)
        self.signup_user_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        ctk.CTkLabel(tab, text="Email").grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.signup_email_entry = ctk.CTkEntry(tab)
        self.signup_email_entry.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(tab, text="Password").grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.signup_pass_entry = ctk.CTkEntry(tab, show="*")
        self.signup_pass_entry.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        signup_btn = ctk.CTkButton(tab, text="Sign Up", command=self.on_signup_click)
        signup_btn.grid(row=6, column=0, padx=20, pady=20)

    def on_login_click(self):
        username = self.login_user_entry.get()
        password = self.login_pass_entry.get()
        if self.controller_callbacks.get('login'):
            self.controller_callbacks['login'](username, password)

    def on_signup_click(self):
        username = self.signup_user_entry.get()
        email = self.signup_email_entry.get()
        password = self.signup_pass_entry.get()
        if self.controller_callbacks.get('signup'):
            self.controller_callbacks['signup'](username, email, password)

class PetDetailsDialog(ctk.CTkToplevel):
    def __init__(self, master, pet_data, adopt_callback):
        super().__init__(master)
        self.title(f"Meet {pet_data['name']}")
        self.geometry("600x400")
        self.transient(master)
        self.grab_set()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Image ---
        try:
            img = Image.open(f"assets/{pet_data['image_path']}")
            ctk_img = ctk.CTkImage(light_image=img, size=(250, 250))
            ctk.CTkLabel(self, image=ctk_img, text="").grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        except:
            ctk.CTkFrame(self, width=250, height=250).grid(row=0, column=0, padx=20, pady=20)

        # --- Details ---
        details_frame = ctk.CTkFrame(self, fg_color="transparent")
        details_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(details_frame, text=pet_data['name'], font=FONTS["header"]).pack(anchor="w")
        ctk.CTkLabel(details_frame, text=f"Breed: {pet_data['breed']}", font=FONTS["body_bold"]).pack(anchor="w", pady=(10,0))
        ctk.CTkLabel(details_frame, text=f"Age: {pet_data['age']} years", font=FONTS["body_bold"]).pack(anchor="w")
        ctk.CTkLabel(details_frame, text=pet_data['description'], font=FONTS["body"], wraplength=280, justify="left").pack(anchor="w", pady=10)
        
        # --- Adopt Button ---
        adopt_button = ctk.CTkButton(self, text=f"Adopt {pet_data['name']}", command=lambda: [adopt_callback(pet_data), self.destroy()])
        adopt_button.grid(row=1, column=0, columnspan=2, pady=20)
