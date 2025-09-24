# controllers.py
# Manages the application logic, state, and connects views with models.

import sys
import json
import logging
import os
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from models import DatabaseManager, WishlistManager, DataWorker
from views import MainView, AuthDialog, PetDetailsDialog, AdoptionFormDialog, ServiceDetailsDialog, ScheduleDialog, ConfirmationDialog

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AppController(QObject):
    """
    Main application controller managing state and UI flow.
    """
    
    # State Machine
    STATES = {
        'guest_home': 0,
        'guest_pet_list': 1,
        'guest_service_list': 2,
        'pet_details': 3,
        'service_details': 4,
        'login': 5,
        'signup': 6,
        'adoption_form': 7,
        'booking_schedule': 8,
        'payment': 9,
        'confirmation': 10,
        'user_dashboard': 11
    }
    
    BREADCRUMBS = {
        'adoption_track': ["Home", "Browse Pets", "Pet Details", "Adoption Application", "Payment", "Confirmation"],
        'booking_track': ["Home", "Browse Services", "Service Details", "Schedule", "Booking Form", "Payment", "Confirmation"]
    }
    
    def __init__(self, view: MainView, db: DatabaseManager, wishlist_manager: WishlistManager):
        super().__init__()
        self.view = view
        self.db = db
        self.wishlist_manager = wishlist_manager
        
        self.user_id = None
        self.username = "Guest"
        self.current_state = self.STATES['guest_home']
        self.current_flow = None # 'adoption' or 'booking'
        self.current_item = None # The pet or service being processed
        
        self.pending_action = None
        
        self.data_worker = None
        
        self.connect_signals()
        self.update_ui_for_state()

        # Initial data load
        self.load_pet_data()
        self.load_service_data()
        
    def connect_signals(self):
        """Connects signals from the view to controller slots."""
        self.view.home_view.findChild(QPushButton, "See All Pets").clicked.connect(self.show_pet_list)
        self.view.home_view.findChild(QPushButton, "See All Services").clicked.connect(self.show_service_list)
        self.view.pet_list_view.findChild(QPushButton, "Search").clicked.connect(self.on_pet_search)
        self.view.service_list_view.findChild(QPushButton, "Search").clicked.connect(self.on_service_search)
        self.view.auth_button.clicked.connect(self.show_auth_dialog)

    def load_pet_data(self):
        """Fetches pet data from the database in a separate thread."""
        self.start_worker_thread('get_pets')
        
    def load_service_data(self):
        """Fetches service data from the database in a separate thread."""
        self.start_worker_thread('get_services')

    def start_worker_thread(self, operation, **kwargs):
        """Starts a DataWorker thread for a given operation."""
        if self.data_worker and self.data_worker.isRunning():
            return
        
        self.data_worker = DataWorker(self.db, operation, **kwargs)
        self.data_worker.result_ready.connect(self.handle_worker_result)
        self.data_worker.error_occurred.connect(self.handle_worker_error)
        self.data_worker.finished.connect(self.on_worker_finished)
        self.data_worker.start()
        
    def handle_worker_result(self, result_type, data):
        """Handles results from the DataWorker thread."""
        if result_type == 'pets_list':
            self.view.display_pets(data)
        elif result_type == 'services_list':
            self.view.display_services(data)
        elif result_type == 'auth_result':
            self.on_login_result(data)
        elif result_type == 'signup_result':
            self.on_signup_result(data)
        elif result_type == 'wishlist_result':
            # Handle syncing the wishlist on login
            if self.pending_action == 'sync_wishlist' and data:
                for pet in data:
                    self.db.add_to_wishlist(self.user_id, pet['id'])
                os.remove(self.wishlist_manager.filename)
                self.pending_action = None
            
    def handle_worker_error(self, operation, error_msg):
        """Handles errors from the DataWorker thread."""
        logging.error(f"Worker thread for '{operation}' failed: {error_msg}")
        QMessageBox.warning(self.view, "Database Error", "An error occurred while accessing the database.")

    def on_worker_finished(self):
        """Cleans up the worker thread."""
        self.data_worker = None
        
    def update_ui_for_state(self):
        """Updates UI elements based on the current state."""
        self.view.progress_frame.setVisible(self.current_state > self.STATES['guest_home'])

        if self.current_flow == 'adoption':
            steps = self.BREADCRUMBS['adoption_track']
            progress_percent = int((self.current_state - self.STATES['guest_home']) / (len(steps) - 1) * 100)
        elif self.current_flow == 'booking':
            steps = self.BREADCRUMBS['booking_track']
            progress_percent = int((self.current_state - self.STATES['guest_home']) / (len(steps) - 1) * 100)
        else:
            steps = ["Home"]
            progress_percent = 0
            
        self.view.breadcrumbs.set_steps(steps)
        self.view.progress_bar.setValue(progress_percent)

        self.view.user_label.setText(self.username)
        self.view.auth_button.setText("Logout" if self.user_id else "Login / Signup")
        self.view.auth_button.clicked.disconnect()
        self.view.auth_button.clicked.connect(self.logout if self.user_id else self.show_auth_dialog)

    def on_pet_card_click(self, pet_data):
        """Handles click on a pet card."""
        self.current_flow = 'adoption'
        self.current_item = pet_data
        self.current_state = self.STATES['pet_details']
        self.update_ui_for_state()
        
        dialog = PetDetailsDialog(pet_data, self.view)
        dialog.adopt_pet.connect(self.on_adopt_click)
        dialog.exec()
        
    def on_service_card_click(self, service_data):
        """Handles click on a service card."""
        self.current_flow = 'booking'
        self.current_item = service_data
        self.current_state = self.STATES['service_details']
        self.update_ui_for_state()

        dialog = ServiceDetailsDialog(service_data, self.view)
        dialog.book_service.connect(self.on_book_click)
        dialog.exec()
        
    def show_auth_dialog(self):
        """Displays the authentication dialog."""
        dialog = AuthDialog(self.view)
        dialog.login_attempt.connect(self.on_login_attempt)
        dialog.signup_attempt.connect(self.on_signup_attempt)
        dialog.exec()
        
    def on_login_attempt(self, username, password):
        """Initiates a login attempt."""
        self.start_worker_thread('verify_user', username=username, password=password)
        
    def on_login_result(self, user_id):
        """Handles the result of a login attempt."""
        if user_id:
            self.user_id = user_id
            self.username = self.db.get_user_by_id(user_id)['username']
            QMessageBox.information(self.view, "Success", f"Welcome back, {self.username}!")
            self.update_ui_for_state()
            self.view.auth_dialog.accept()
            # If there's a pending action, redirect to it
            if self.pending_action == 'adopt':
                self.show_adoption_form()
            elif self.pending_action == 'book':
                self.show_schedule_dialog()
            # Check for guest wishlist to sync
            if os.path.exists(self.wishlist_manager.filename):
                self.pending_action = 'sync_wishlist'
                guest_wishlist = self.wishlist_manager.load_wishlist()
                if guest_wishlist:
                    for pet_id in guest_wishlist:
                        self.db.add_to_wishlist(self.user_id, pet_id)
                    os.remove(self.wishlist_manager.filename)
                    QMessageBox.information(self.view, "Wishlist Synced", "Your guest wishlist has been synced to your account!")

        else:
            self.view.auth_dialog.login_error_label.setText("Invalid username or password.")
            
    def on_signup_attempt(self, username, email, password):
        """Initiates a signup attempt."""
        self.start_worker_thread('add_user', username=username, email=email, password=password)
        
    def on_signup_result(self, success):
        """Handles the result of a signup attempt."""
        if success:
            QMessageBox.information(self.view, "Success", "Account created! Please log in.")
            self.view.auth_dialog.tab_widget.setCurrentIndex(0) # Switch to login tab
        else:
            self.view.auth_dialog.signup_error_label.setText("Username or email already exists.")
            
    def logout(self):
        """Logs the current user out."""
        self.user_id = None
        self.username = "Guest"
        self.current_state = self.STATES['guest_home']
        self.current_flow = None
        self.current_item = None
        self.view.show_home_view()
        self.update_ui_for_state()
        QMessageBox.information(self.view, "Logged Out", "You have been logged out.")
        
    def on_adopt_click(self, pet_data):
        """Handles the 'Adopt' button click, checks for auth."""
        if not self.user_id:
            self.pending_action = 'adopt'
            self.view.auth_dialog = AuthDialog(self.view)
            self.view.auth_dialog.login_attempt.connect(self.on_login_attempt)
            self.view.auth_dialog.signup_attempt.connect(self.on_signup_attempt)
            self.view.auth_dialog.exec()
        else:
            self.show_adoption_form()
    
    def on_book_click(self, service_data):
        """Handles the 'Book' button click, checks for auth."""
        if not self.user_id:
            self.pending_action = 'book'
            self.view.auth_dialog = AuthDialog(self.view)
            self.view.auth_dialog.login_attempt.connect(self.on_login_attempt)
            self.view.auth_dialog.signup_attempt.connect(self.on_signup_attempt)
            self.view.auth_dialog.exec()
        else:
            self.show_schedule_dialog()

    def show_adoption_form(self):
        """Shows the adoption application form."""
        self.current_state = self.STATES['adoption_form']
        self.update_ui_for_state()
        dialog = AdoptionFormDialog(self.current_item, self.view)
        dialog.form_submitted.connect(self.on_adoption_form_submitted)
        dialog.exec()
        
    def on_adoption_form_submitted(self, form_data):
        """Handles a completed adoption form."""
        QMessageBox.information(self.view, "Payment", "Payment placeholder. Proceeding to confirmation.")
        self.db.add_adopted_pet(self.user_id, self.current_item['id'])
        self.show_confirmation_dialog("Your adoption application has been submitted successfully!")

    def show_schedule_dialog(self):
        """Shows the service scheduling dialog."""
        self.current_state = self.STATES['booking_schedule']
        self.update_ui_for_state()
        dialog = ScheduleDialog(self.view)
        dialog.schedule_selected.connect(self.on_schedule_selected)
        dialog.exec()
        
    def on_schedule_selected(self, date_str):
        """Handles a selected booking date."""
        QMessageBox.information(self.view, "Booking", "Booking form and payment placeholder. Proceeding to confirmation.")
        self.db.add_booking(self.user_id, self.current_item['id'], date_str)
        self.show_confirmation_dialog("Your service booking is confirmed!")
        
    def show_confirmation_dialog(self, message):
        """Shows the final confirmation dialog."""
        self.current_state = self.STATES['confirmation']
        self.update_ui_for_state()
        dialog = ConfirmationDialog(message, self.view)
        dialog.exec()
        self.reset_to_home()

    def reset_to_home(self):
        """Resets the application state back to the home view."""
        self.current_state = self.STATES['guest_home']
        self.current_flow = None
        self.current_item = None
        self.update_ui_for_state()
        self.view.show_home_view()

    def show_pet_list(self):
        """Switches to the pet list view and updates state."""
        self.current_state = self.STATES['guest_pet_list']
        self.current_flow = 'adoption'
        self.update_ui_for_state()
        self.view.show_pet_list_view()
        self.view.clear_grid_layout(self.view.pet_grid_layout)
        self.load_pet_data()
        
    def show_service_list(self):
        """Switches to the service list view and updates state."""
        self.current_state = self.STATES['guest_service_list']
        self.current_flow = 'booking'
        self.update_ui_for_state()
        self.view.show_service_list_view()
        self.view.clear_grid_layout(self.view.service_grid_layout)
        self.load_service_data()
        
    def on_pet_search(self):
        """Handles the pet search button click."""
        query = self.view.pet_list_view.findChild(QLineEdit).text()
        # In a full app, we would also get filters.
        self.start_worker_thread('get_pets', query=query)
        
    def on_service_search(self):
        """Handles the service search button click."""
        query = self.view.service_list_view.findChild(QLineEdit).text()
        self.start_worker_thread('get_services', query=query)
        
    def on_home_view_pet_card_clicked(self, event):
        """Handles clicks on pet cards in the home view's grid."""
        widget = self.view.pets_section.findChild(QGridLayout).itemAt(0).widget().childAt(event.pos())
        if isinstance(widget, PetCard):
            self.on_pet_card_click(widget.pet_data)

    def on_home_view_service_card_clicked(self, event):
        """Handles clicks on service cards in the home view's grid."""
        widget = self.view.services_section.findChild(QGridLayout).itemAt(0).widget().childAt(event.pos())
        if isinstance(widget, ServiceCard):
            self.on_service_card_click(widget.service_data)
      
