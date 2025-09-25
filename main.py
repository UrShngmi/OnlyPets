# main.py
# The entry point of the OnlyPets GUI application.

import sys
import os
import logging
import customtkinter as ctk
from tkinter import messagebox
from models import DatabaseManager, WishlistManager
from views import MainView
from controllers import AppController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_resources():
    """Create placeholder directories and assets if they don't exist."""
    if not os.path.exists('assets'):
        os.makedirs('assets')
        logging.info("Created 'assets' directory.")
    
    # Create empty placeholder image files to prevent errors on first run
    for i in range(1, 11):
        filepath = f"assets/p{i}.jpg"
        if not os.path.exists(filepath):
            try:
                from PIL import Image
                # Create a small blank image
                img = Image.new('RGB', (100, 100), color = 'gray')
                img.save(filepath)
            except ImportError:
                 # If Pillow is not installed, create an empty file
                with open(filepath, 'w') as f:
                    pass
    logging.info("Assets directory and placeholder files checked/created.")

def main():
    """Main function to run the application."""
    setup_resources()
    
    # Set CustomTkinter appearance
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    
    # Initialize database
    db_manager = DatabaseManager()
    try:
        # The connection is now managed per-thread, so we just initialize it here.
        db_manager.create_tables()
        db_manager.populate_sample_data()
        db_manager.close_conn() # Close the main thread's initial connection
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to initialize the database: {e}")
        sys.exit(1)
        
    wishlist_manager = WishlistManager()
    
    # Initialize MVC components
    main_view = MainView()
    controller = AppController(main_view, db_manager, wishlist_manager)
    
    # Start the main event loop
    main_view.mainloop()

if __name__ == '__main__':
    main()
