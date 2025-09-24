# models.py
# Manages the SQLite database and data-related operations.

import sqlite3
import json
import logging
from passlib.hash import argon2
from PyQt6.QtCore import QObject, pyqtSignal, QThread

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    """Handles all SQLite database connections and operations."""

    def __init__(self, db_name="onlypets.db"):
        """Initializes the database manager and creates tables if they don't exist."""
        self.db_name = db_name
        self.conn = None

    def connect(self):
        """Establishes a connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row  # Allows accessing columns by name
            logging.info("Database connection successful.")
            return True
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            return False

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")

    def _execute_query(self, query, params=()):
        """Internal helper to execute a query and handle common errors."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor
        except sqlite3.Error as e:
            logging.error(f"SQLite query error: {e}")
            return None

    def create_tables(self):
        """Creates the necessary database tables (pets, services, users, wishlists, adoptions, bookings)."""
        if not self.conn:
            logging.error("Database not connected. Cannot create tables.")
            return

        queries = [
            """
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                breed TEXT NOT NULL,
                age INTEGER NOT NULL,
                description TEXT,
                image_path TEXT
            );""",
            """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price REAL
            );""",
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );""",
            """
            CREATE TABLE IF NOT EXISTS user_wishlist (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                pet_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (pet_id) REFERENCES pets(id)
            );""",
            """
            CREATE TABLE IF NOT EXISTS user_adoptions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                pet_id INTEGER,
                adoption_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (pet_id) REFERENCES pets(id)
            );""",
            """
            CREATE TABLE IF NOT EXISTS user_bookings (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                service_id INTEGER,
                booking_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (service_id) REFERENCES services(id)
            );"""
        ]
        for query in queries:
            self._execute_query(query)

    def populate_sample_data(self):
        """Populates the database with initial sample data."""
        pets_data = [
            ("Buddy", "Golden Retriever", 3, "A friendly and playful dog, loves long walks.", "p1.jpg"),
            ("Whiskers", "Tabby Cat", 2, "An independent cat who enjoys sunbathing.", "p2.jpg"),
            ("Max", "German Shepherd", 5, "Loyal and energetic, would be a great running partner.", "p3.jpg"),
            ("Luna", "Siamese Cat", 1, "A curious kitten who loves to play with toys.", "p4.jpg"),
            ("Rocky", "Labrador", 4, "A sweet and gentle giant, good with kids.", "p5.jpg"),
            ("Milo", "Beagle", 2, "A happy and outgoing dog, always ready for an adventure.", "p6.jpg"),
            ("Chloe", "Persian Cat", 3, "An elegant and calm cat, enjoys quiet afternoons.", "p7.jpg"),
            ("Daisy", "Poodle", 1, "A smart and mischievous pup, loves learning new tricks.", "p8.jpg"),
            ("Zoe", "Dachshund", 6, "A spirited and brave little dog, full of personality.", "p9.jpg"),
            ("Oliver", "Maine Coon", 4, "A large and gentle cat, very affectionate.", "p10.jpg"),
        ]
        self._execute_query("INSERT OR IGNORE INTO pets (name, breed, age, description, image_path) VALUES (?, ?, ?, ?, ?)", pets_data)

        services_data = [
            ("Grooming", "Full grooming service including bath, trim, and nail clipping.", 50.00),
            ("Vet Checkup", "Comprehensive health checkup by a licensed veterinarian.", 75.00),
            ("Pet Training", "Basic obedience training for dogs of all ages.", 150.00),
            ("Daycare", "Supervised daily care for your pet while you're away.", 30.00),
            ("Boarding", "Overnight care and comfortable lodging for your pet.", 40.00),
        ]
        self._execute_query("INSERT OR IGNORE INTO services (name, description, price) VALUES (?, ?, ?)", services_data)

    def get_pets(self, query=None, filters=None):
        """Fetches a list of pets, optionally with search query and filters."""
        sql = "SELECT * FROM pets"
        params = []
        where_clauses = []

        if query:
            where_clauses.append("(name LIKE ? OR breed LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])

        if filters:
            if filters.get('breed'):
                where_clauses.append("breed = ?")
                params.append(filters['breed'])
            if filters.get('age_min') is not None:
                where_clauses.append("age >= ?")
                params.append(filters['age_min'])
            if filters.get('age_max') is not None:
                where_clauses.append("age <= ?")
                params.append(filters['age_max'])

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        
        cursor = self.conn.cursor()
        cursor.execute(sql, tuple(params))
        return [dict(row) for row in cursor.fetchall()]

    def get_services(self, query=None):
        """Fetches a list of services, optionally with a search query."""
        sql = "SELECT * FROM services"
        params = []
        if query:
            sql += " WHERE name LIKE ?"
            params.append(f"%{query}%")
        
        cursor = self.conn.cursor()
        cursor.execute(sql, tuple(params))
        return [dict(row) for row in cursor.fetchall()]

    def get_pet_by_id(self, pet_id):
        """Fetches a single pet by its ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pets WHERE id = ?", (pet_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_service_by_id(self, service_id):
        """Fetches a single service by its ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def add_user(self, username, email, password):
        """Adds a new user to the database with a hashed password."""
        try:
            password_hash = argon2.hash(password)
            self._execute_query("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", 
                                (username, email, password_hash))
            logging.info(f"New user {username} added successfully.")
            return True
        except sqlite3.IntegrityError:
            logging.warning(f"Username or email '{username}' already exists.")
            return False

    def verify_user(self, username, password):
        """Verifies a user's password against the stored hash."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row and argon2.verify(password, row['password_hash']):
            logging.info(f"User {username} authenticated successfully.")
            return row['id']
        logging.warning(f"Failed authentication attempt for user: {username}")
        return None

    def get_user_by_id(self, user_id):
        """Fetches user details by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def add_to_wishlist(self, user_id, pet_id):
        """Adds a pet to a user's wishlist."""
        self._execute_query("INSERT OR IGNORE INTO user_wishlist (user_id, pet_id) VALUES (?, ?)", (user_id, pet_id))

    def get_wishlist(self, user_id):
        """Retrieves a user's wishlist."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT p.* FROM user_wishlist uw JOIN pets p ON uw.pet_id = p.id WHERE uw.user_id = ?", (user_id,))
        return [dict(row) for row in cursor.fetchall()]
        
    def add_adopted_pet(self, user_id, pet_id):
        """Adds an adopted pet to a user's history."""
        self._execute_query("INSERT INTO user_adoptions (user_id, pet_id, adoption_date) VALUES (?, ?, date('now'))", (user_id, pet_id))

    def get_adopted_pets(self, user_id):
        """Retrieves a user's adoption history."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT p.* FROM user_adoptions ua JOIN pets p ON ua.pet_id = p.id WHERE ua.user_id = ?", (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def add_booking(self, user_id, service_id, booking_date):
        """Adds a service booking to a user's history."""
        self._execute_query("INSERT INTO user_bookings (user_id, service_id, booking_date) VALUES (?, ?, ?)", (user_id, service_id, booking_date))

    def get_user_bookings(self, user_id):
        """Retrieves a user's booking history."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT s.*, ub.booking_date FROM user_bookings ub JOIN services s ON ub.service_id = s.id WHERE ub.user_id = ?", (user_id,))
        return [dict(row) for row in cursor.fetchall()]


class WishlistManager:
    """Manages the guest wishlist saved to a local JSON file."""
    def __init__(self, filename="guest_wishlist.json"):
        self.filename = filename

    def load_wishlist(self):
        """Loads a wishlist from a JSON file."""
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_wishlist(self, wishlist_ids):
        """Saves a wishlist to a JSON file."""
        with open(self.filename, 'w') as f:
            json.dump(wishlist_ids, f)

class DataWorker(QThread):
    """
    Worker thread to perform database operations in the background.
    This prevents the UI from freezing during I/O operations.
    """
    result_ready = pyqtSignal(str, object)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, db_manager, operation, **kwargs):
        super().__init__()
        self.db = db_manager
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        """Executes the requested database operation."""
        try:
            if self.operation == 'get_pets':
                data = self.db.get_pets(self.kwargs.get('query'), self.kwargs.get('filters'))
                self.result_ready.emit('pets_list', data)
            elif self.operation == 'get_services':
                data = self.db.get_services(self.kwargs.get('query'))
                self.result_ready.emit('services_list', data)
            elif self.operation == 'verify_user':
                user_id = self.db.verify_user(self.kwargs['username'], self.kwargs['password'])
                self.result_ready.emit('auth_result', user_id)
            elif self.operation == 'add_user':
                success = self.db.add_user(self.kwargs['username'], self.kwargs['email'], self.kwargs['password'])
                self.result_ready.emit('signup_result', success)
            elif self.operation == 'get_wishlist':
                data = self.db.get_wishlist(self.kwargs['user_id'])
                self.result_ready.emit('wishlist_result', data)
            elif self.operation == 'add_to_wishlist':
                self.db.add_to_wishlist(self.kwargs['user_id'], self.kwargs['pet_id'])
                self.result_ready.emit('wishlist_updated', True)
            elif self.operation == 'add_adopted_pet':
                self.db.add_adopted_pet(self.kwargs['user_id'], self.kwargs['pet_id'])
                self.result_ready.emit('adoption_completed', True)
            elif self.operation == 'add_booking':
                self.db.add_booking(self.kwargs['user_id'], self.kwargs['service_id'], self.kwargs['booking_date'])
                self.result_ready.emit('booking_completed', True)
            
        except Exception as e:
            logging.error(f"Error in DataWorker thread: {e}")
            self.error_occurred.emit(self.operation, str(e))
