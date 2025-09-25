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
            ctk.CTkLabel(self, image=ctk_img, text="").pack(pady=5, padx=5)
        except:
            ctk.CTkFrame(self, width=180, height=135).pack(pady=5, padx=5)

        # --- Details ---
        ctk.CTkLabel(self, text=pet_data['name'], font=FONTS["header"]).pack()
        
        # --- Clickable functionality ---
        self.bind("<Button-1>", lambda event, data=pet_data: command(data))
        for widget in self.winfo_children():
            widget.bind("<Button-1>", lambda event, data=pet_data: command(data))
        
class ServiceCard(ctk.CTkFrame):
    """A clickable card widget for displaying a service."""
    def __init__(self, master, service_data, command):
        super().__init__(master, corner_radius=12, fg_color="white", border_color=COLORS["border"], border_width=1)
        self.service_data = service_data

        # --- Image ---
        try:
            img = Image.open(f"assets/{service_data['image_path']}")
            ctk_img = ctk.CTkImage(light_image=img, size=(180, 135))
            ctk.CTkLabel(self, image=ctk_img, text="").pack(pady=5, padx=5)
        except:
            ctk.CTkFrame(self, width=180, height=135).pack(pady=5, padx=5)

        # --- Details ---
        ctk.CTkLabel(self, text=service_data['name'], font=FONTS["header"]).pack()
        ctk.CTkLabel(self, text=f"Price: ${service_data['price']}", font=FONTS["body_bold"]).pack()

        # --- Clickable functionality ---
        self.bind("<Button-1>", lambda event, data=service_data: command(data))
        for widget in self.winfo_children():
            widget.bind("<Button-1>", lambda event, data=service_data: command(data))
            
class PetDetailsDialog(ctk.CTkToplevel):
    """A dialog to display detailed information about a pet."""
    def __init__(self, master, pet_data, adopt_command):
        super().__init__(master)
        self.title("Pet Details")
        self.pet_data = pet_data
        self.adopt_command = adopt_command
        self.transient(master)
        self.grab_set()
        
        # --- Image ---
        try:
            img = Image.open(f"assets/{pet_data['image_path']}")
            ctk_img = ctk.CTkImage(light_image=img, size=(250, 250))
            ctk.CTkLabel(self, image=ctk_img, text="").pack(pady=10, padx=10)
        except:
            ctk.CTkFrame(self, width=250, height=250).pack(pady=10, padx=10)
        
        # --- Details ---
        details_frame = ctk.CTkFrame(self, fg_color="transparent")
        details_frame.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkLabel(details_frame, text=pet_data['name'], font=FONTS["title"]).pack()
        ctk.CTkLabel(details_frame, text=f"Breed: {pet_data['breed']}", font=FONTS["body_bold"]).pack(pady=(10,0))
        ctk.CTkLabel(details_frame, text=f"Age: {pet_data['age']} years", font=FONTS["body_bold"]).pack()
        ctk.CTkLabel(details_frame, text=f"Description: {pet_data['description']}", font=FONTS["body"]).pack(pady=10)
        
        # --- Buttons ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)
        
        ctk.CTkButton(button_frame, text="Adopt", command=self.on_adopt).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Close", command=self.destroy).pack(side="right", padx=5)
        
    def on_adopt(self):
        self.destroy()
        self.adopt_command(self.pet_data)


class MainView(ctk.CTk):
    """The main application window and container for all frames."""
    def __init__(self):
        super().__init__()
        self.title("OnlyPets")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Container for frames ---
        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage, PetListPage, ServiceListPage, AuthPage):
            page_name = F.__name__
            frame = F(master=container, controller=None)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.auth_button = ctk.CTkButton(self, text="Login")
        self.auth_button.pack(side="top", anchor="e", padx=10, pady=5)
        
        self.show_frame("HomePage")
        
    def show_frame(self, page_name):
        """Shows a frame for the given page name."""
        frame = self.frames[page_name]
        frame.tkraise()
        
    def set_controller(self, controller):
        """Sets the controller for all frames."""
        for frame in self.frames.values():
            frame.controller = controller


class AuthDialog(ctk.CTkToplevel):
    """A dialog for user authentication (login/signup)."""
    def __init__(self, master, login_command, signup_command):
        super().__init__(master)
        self.title("Authenticate")
        self.geometry("300x400")
        self.transient(master)
        self.grab_set()

        # UI elements
        self.login_command = login_command
        self.signup_command = signup_command

        self.main_frame = ctk.CTkFrame(self, corner_radius=12)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.title_label = ctk.CTkLabel(self.main_frame, text="Login", font=FONTS["header"])
        self.title_label.pack(pady=10)

        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Username")
        self.username_entry.pack(pady=5, padx=10, fill="x")

        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=5, padx=10, fill="x")
        
        self.email_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Email (for signup only)")
        self.email_entry.pack(pady=5, padx=10, fill="x")
        self.email_entry.pack_forget() # Initially hidden

        self.login_button = ctk.CTkButton(self.main_frame, text="Login", command=self.on_login)
        self.login_button.pack(pady=10, padx=10, fill="x")
        
        self.switch_button = ctk.CTkButton(self.main_frame, text="Switch to Sign Up", fg_color="transparent", 
                                        text_color=COLORS["primary"], hover_color=COLORS["bg_dark"], command=self.switch_mode)
        self.switch_button.pack(pady=5)

        self.is_login_mode = True

    def switch_mode(self):
        self.is_login_mode = not self.is_login_mode
        if self.is_login_mode:
            self.title_label.configure(text="Login")
            self.login_button.configure(text="Login", command=self.on_login)
            self.switch_button.configure(text="Switch to Sign Up")
            self.email_entry.pack_forget()
        else:
            self.title_label.configure(text="Sign Up")
            self.login_button.configure(text="Sign Up", command=self.on_signup)
            self.switch_button.configure(text="Switch to Login")
            self.email_entry.pack(pady=5, padx=10, fill="x")

    def on_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.login_command(username, password)
        self.destroy()

    def on_signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()
        self.signup_command(username, email, password)
        self.destroy()

class HomePage(ctk.CTkFrame):
    """The main landing page with featured pets and services."""
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        
        # --- Pet Section ---
        self.pets_section = ctk.CTkFrame(self, fg_color="transparent")
        self.pets_section.pack(padx=20, pady=(20, 10), fill="x")
        ctk.CTkLabel(self.pets_section, text="Featured Pets", font=FONTS["header"]).pack(side="left")
        self.pets_section.see_all_button = ctk.CTkButton(self.pets_section, text="See All", fg_color="transparent", 
                                                         hover_color=COLORS["bg_dark"], text_color=COLORS["primary"])
        self.pets_section.see_all_button.pack(side="right")
        
        self.pet_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.pet_grid.pack(padx=20, fill="x", expand=True)
        self.pet_grid.grid_columnconfigure(0, weight=1)
        self.pet_grid.grid_columnconfigure(1, weight=1)
        self.pet_grid.grid_columnconfigure(2, weight=1)
        
        # --- Service Section ---
        self.services_section = ctk.CTkFrame(self, fg_color="transparent")
        self.services_section.pack(padx=20, pady=(20, 10), fill="x")
        ctk.CTkLabel(self.services_section, text="Featured Services", font=FONTS["header"]).pack(side="left")
        self.services_section.see_all_button = ctk.CTkButton(self.services_section, text="See All", fg_color="transparent",
                                                            hover_color=COLORS["bg_dark"], text_color=COLORS["primary"])
        self.services_section.see_all_button.pack(side="right")

        self.service_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.service_grid.pack(padx=20, fill="x", expand=True)
        self.service_grid.grid_columnconfigure(0, weight=1)
        self.service_grid.grid_columnconfigure(1, weight=1)
        self.service_grid.grid_columnconfigure(2, weight=1)
        
    def clear_grid(self, grid_frame):
        """Clears all widgets from the specified grid frame."""
        for widget in grid_frame.winfo_children():
            widget.destroy()

    def display_pets(self, pets):
        """Displays pet cards in the pet grid."""
        self.clear_grid(self.pet_grid)
        for i, pet in enumerate(pets[:3]): # Display only up to 3 for the home page
            card = PetCard(self.pet_grid, pet, self.controller.on_pet_click)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

    def display_services(self, services):
        """Displays service cards in the service grid."""
        self.clear_grid(self.service_grid)
        for i, service in enumerate(services[:3]): # Display only up to 3 for the home page
            card = ServiceCard(self.service_grid, service, self.controller.on_service_click)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")


class PetListPage(ctk.CTkFrame):
    """A page to display a list of all pets."""
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller

        # --- Top Bar ---
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(pady=(20,10), padx=20, fill="x")
        ctk.CTkButton(top_bar, text="< Back", fg_color="transparent", hover_color=COLORS["bg_dark"], text_color=COLORS["primary"], command=self.go_back).pack(side="left")
        ctk.CTkLabel(top_bar, text="All Pets", font=FONTS["header"]).pack(side="left", padx=10)
        self.search_entry = ctk.CTkEntry(top_bar, placeholder_text="Search pets...")
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(10,0))
        ctk.CTkButton(top_bar, text="Search", command=self.on_search).pack(side="left", padx=(5,0))
        
        self.pet_grid = ctk.CTkScrollableFrame(self)
        self.pet_grid.pack(padx=20, pady=10, fill="both", expand=True)
        self.pet_grid.grid_columnconfigure(0, weight=1)
        self.pet_grid.grid_columnconfigure(1, weight=1)
        self.pet_grid.grid_columnconfigure(2, weight=1)
        
    def on_search(self):
        if self.controller:
            self.controller.on_pet_search()
            
    def go_back(self):
        if self.controller:
            self.controller.show_home()
            
    def display_pets(self, pets):
        """Displays pet cards in the pet grid."""
        for widget in self.pet_grid.winfo_children():
            widget.destroy()
        
        for i, pet in enumerate(pets):
            card = PetCard(self.pet_grid, pet, self.controller.on_pet_click)
            row = i // 3
            col = i % 3
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")


class ServiceListPage(ctk.CTkFrame):
    """A page to display a list of all services."""
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        
        # --- Top Bar ---
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(pady=(20,10), padx=20, fill="x")
        ctk.CTkButton(top_bar, text="< Back", fg_color="transparent", hover_color=COLORS["bg_dark"], text_color=COLORS["primary"], command=self.go_back).pack(side="left")
        ctk.CTkLabel(top_bar, text="All Services", font=FONTS["header"]).pack(side="left", padx=10)
        self.search_entry = ctk.CTkEntry(top_bar, placeholder_text="Search services...")
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(10,0))
        ctk.CTkButton(top_bar, text="Search", command=self.on_search).pack(side="left", padx=(5,0))
        
        self.service_grid = ctk.CTkScrollableFrame(self)
        self.service_grid.pack(padx=20, pady=10, fill="both", expand=True)
        self.service_grid.grid_columnconfigure(0, weight=1)
        self.service_grid.grid_columnconfigure(1, weight=1)
        self.service_grid.grid_columnconfigure(2, weight=1)
        
    def on_search(self):
        if self.controller:
            self.controller.on_service_search()
            
    def go_back(self):
        if self.controller:
            self.controller.show_home()

    def display_services(self, services):
        """Displays service cards in the service grid."""
        for widget in self.service_grid.winfo_children():
            widget.destroy()
        
        for i, service in enumerate(services):
            card = ServiceCard(self.service_grid, service, self.controller.on_service_click)
            row = i // 3
            col = i % 3
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")


class AuthPage(ctk.CTkFrame):
    """A placeholder frame for authentication-related content."""
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        
        # This frame is not used for direct display, as AuthDialog is a top-level window.
        # It exists as a placeholder in the MainView frames dictionary for consistency.
