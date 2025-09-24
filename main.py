# main.py
# The entry point of the OnlyPets GUI application.

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from models import DatabaseManager, WishlistManager
from views import MainView
from controllers import AppController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_resources():
    """Create placeholder directories and assets if they don't exist."""
    if not os.path.exists('assets'):
        os.makedirs('assets')
    # Create empty placeholder files to avoid errors
    for i in range(1, 11):
        if not os.path.exists(f"assets/p{i}.jpg"):
            with open(f"assets/p{i}.jpg", 'w') as f:
                pass
    logging.info("Assets directory and placeholder files checked.")

def main():
    """Main function to run the application."""
    setup_resources()
    
    app = QApplication(sys.argv)
    app.setApplicationName("OnlyPets")
    
    # Check for font (Inter) availability and fallback
    font = app.font()
    if not font.family() == 'Inter':
        logging.warning("Font 'Inter' not found. Using system default.")

    # Try to connect to the database
    db_manager = DatabaseManager()
    if not db_manager.connect():
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Error")
        msg_box.setText("Failed to connect to the database. The application cannot start.")
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.exec()
        sys.exit(-1)
        
    db_manager.create_tables()
    db_manager.populate_sample_data()
    
    wishlist_manager = WishlistManager()
    
    main_view = MainView()
    controller = AppController(main_view, db_manager, wishlist_manager)
    
    main_view.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
  
