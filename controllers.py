# controllers.py
# Manages application logic, state, and connects views with models.

import logging
from tkinter import messagebox
import queue
import os

from models import DatabaseManager, WishlistManager, DataWorker
from views import MainView, AuthDialog, PetDetailsDialog

class AppController:
    """Main application controller managing state and UI flow."""
    
    def __init__(self, view: MainView, db: DatabaseManager, wishlist_manager: WishlistManager):
        self.view = view
        self.db = db
        self.wishlist_manager = wishlist_manager
        
        self.user_id = None
        self.username = "Guest"
        self.current_item = None # The pet or service being processed
        self.pending_action = None
        
        # Queue for thread-safe communication
        self.data_queue = queue.Queue()
        
        self.setup_callbacks()
        self.update_ui_for_state()

        # Initial data load
        self.load_pet_data()
        self.load_service_data()
        
        # Start the queue listener
        self.view.after(100, self.process_queue)

    def setup_callbacks(self):
        """Assigns controller methods to view widget commands."""
        # --- Main View ---
        self.view.auth_button.configure(command=self.auth_button_action)
        
        # --- Home Page ---
        home_page = self.view.frames["HomePage"]
        home_page.pets_section.see_all_button.configure(command=self.show_pet_list)
        home_page.services_section.see_all_button.configure(command=self.show_service_list)
        
        # --- Pet List Page ---
        pet_page = self.view.frames["PetListPage"]
        pet_page.home_button.configure(command=self.show_home)
        pet_page.search_button.configure(command=self.on_pet_search)

        # --- Service List Page ---
        service_page = self.view.frames["ServiceListPage"]
        service_page.home_button.configure(command=self.show_home)
        service_page.search_button.configure(command=self.on_service_search)
        
    def process_queue(self):
        """Processes results from the data worker thread queue."""
        try:
            while not self.data_queue.empty():
                operation, data = self.data_queue.get_nowait()
                
                if isinstance(data, Exception):
                    logging.error(f"Worker thread for '{operation}' failed: {data}")
                    messagebox.showerror("Database Error", "An error occurred while accessing the database.")
                    continue

                if operation == 'get_pets':
                    self.view.frames["HomePage"].clear_grid(self.view.frames["HomePage"].pet_grid)
                    self.view.frames["PetListPage"].clear_grid(self.view.frames["PetListPage"].pet_grid)
                    self.populate_pet_grids(data)
                elif operation == 'get_services':
                    self.view.frames["HomePage"].clear_grid(self.view.frames["HomePage"].service_grid)
                    self.view.frames["ServiceListPage"].clear_grid(self.view.frames["ServiceListPage"].service_grid)
                    self.populate_service_grids(data)
                elif operation == 'verify_user':
                    self.on_login_result(data)
                elif operation == 'add_user':
                    self.on_signup_result(data)
        finally:
            self.view.after(100, self.process_queue)
    
    def start_worker(self, operation, **kwargs):
        """Starts a DataWorker thread."""
        worker = DataWorker(self.db, operation, self.data_queue, **kwargs)
        worker.start()

    def load_pet_data(self, query=None):
        """Fetches pet data from the database."""
        self.start_worker('get_pets', query=query)
        
    def load_service_data(self, query=None):
        """Fetches service data from the database."""
        self.start_worker('get_services', query=query)

    def populate_pet_grids(self, pet_list):
        """Populates both home and list pet grids with cards."""
        home_grid = self.view.frames["HomePage"].pet_grid
        list_grid = self.view.frames["PetListPage"].pet_grid

        # Display first 4 on home page
        for i, pet in enumerate(pet_list[:4]):
            card = self.view.PetCard(home_grid, pet, self.on_pet_card_click)
            card.grid(row=0, column=i, padx=10, pady=10)

        # Display all on the list page
        cols = 4
        for i, pet in enumerate(pet_list):
            card = self.view.PetCard(list_grid, pet, self.on_pet_card_click)
            card.grid(row=i // cols, column=i % cols, padx=10, pady=10)
    
    def populate_service_grids(self, service_list):
        """Populates both home and list service grids with cards."""
        home_grid = self.view.frames["HomePage"].service_grid
        list_grid = self.view.frames["ServiceListPage"].service_grid

        for i, service in enumerate(service_list[:4]):
            card = self.view.ServiceCard(home_grid, service, self.on_service_card_click)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

        cols = 4
        for i, service in enumerate(service_list):
            card = self.view.ServiceCard(list_grid, service, self.on_service_card_click)
            card.grid(row=i // cols, column=i % cols, padx=10, pady=10, sticky="nsew")

    def update_ui_for_state(self):
        """Updates UI elements based on login state."""
        self.view.user_label.configure(text=self.username)
        self.view.auth_button.configure(text="Logout" if self.user_id else "Login / Signup")

    def auth_button_action(self):
        """Handles click on the main auth button (Login or Logout)."""
        if self.user_id:
            self.logout()
        else:
            self.show_auth_dialog()

    def show_auth_dialog(self):
        dialog = AuthDialog(self.view)
        dialog.controller_callbacks['login'] = self.on_login_attempt
        dialog.controller_callbacks['signup'] = self.on_signup_attempt
        self.auth_dialog = dialog # Keep a reference

    def on_login_attempt(self, username, password):
        if not username or not password:
            messagebox.showwarning("Login Failed", "Please enter both username and password.", parent=self.auth_dialog)
            return
        self.start_worker('verify_user', username=username, password=password)
        
    def on_login_result(self, user_id):
        if user_id:
            self.user_id = user_id
            user_data = self.db.get_user_by_id(user_id)
            self.username = user_data['username']
            self.auth_dialog.destroy()
            messagebox.showinfo("Success", f"Welcome back, {self.username}!")
            self.update_ui_for_state()
            if self.pending_action == 'adopt':
                self.show_adoption_form()
            self.pending_action = None
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=self.auth_dialog)
            
    def on_signup_attempt(self, username, email, password):
        if not all([username, email, password]):
            messagebox.showwarning("Signup Failed", "Please fill all fields.", parent=self.auth_dialog)
            return
        self.start_worker('add_user', username=username, email=email, password=password)
        
    def on_signup_result(self, success):
        if success:
            messagebox.showinfo("Success", "Account created successfully! Please log in.", parent=self.auth_dialog)
            self.auth_dialog.tab_view.set("Login") # Switch to login tab
        else:
            messagebox.showerror("Signup Failed", "Username or email already exists.", parent=self.auth_dialog)
            
    def logout(self):
        self.user_id = None
        self.username = "Guest"
        self.update_ui_for_state()
        self.show_home()
        messagebox.showinfo("Logged Out", "You have been successfully logged out.")

    def on_pet_card_click(self, pet_data):
        self.current_item = pet_data
        PetDetailsDialog(self.view, pet_data, adopt_callback=self.on_adopt_click)
        
    def on_service_card_click(self, service_data):
        self.current_item = service_data
        messagebox.showinfo("Service Details", f"Details for {service_data['name']}\n\nThis would open a details dialog.")

    def on_adopt_click(self, pet_data):
        if not self.user_id:
            self.pending_action = 'adopt'
            messagebox.showinfo("Login Required", "Please log in or create an account to adopt a pet.")
            self.show_auth_dialog()
        else:
            self.show_adoption_form()

    def show_adoption_form(self):
        # Placeholder for adoption form logic
        pet_name = self.current_item['name']
        res = messagebox.askyesno("Confirm Adoption", f"Are you sure you want to proceed with adopting {pet_name}?")
        if res:
            self.db.add_adopted_pet(self.user_id, self.current_item['id'])
            messagebox.showinfo("Success", f"Your adoption application for {pet_name} has been submitted!")
            self.show_home()

    def on_pet_search(self):
        query = self.view.frames["PetListPage"].search_entry.get()
        self.load_pet_data(query=query)
        
    def on_service_search(self):
        query = self.view.frames["ServiceListPage"].search_entry.get()
        self.load_service_data(query=query)

    def show_home(self):
        self.view.show_frame("HomePage")
        
    def show_pet_list(self):
        self.view.show_frame("PetListPage")
        self.load_pet_data()

    def show_service_list(self):
        self.view.show_frame("ServiceListPage")
        self.load_service_data()
