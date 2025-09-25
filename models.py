# models.py
# Manages the SQLite database and data-related operations.

import sqlite3
import json
import logging
import threading
from passlib.hash import argon2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    """Handles all SQLite database connections and operations."""

    def __init__(self, db_name="onlypets.db"):
        """Initializes the database manager."""
        self.db_name = db_name
        self.conn = None
        # Use a thread-local connection object for thread safety
        self.local = threading.local()

    def get_conn(self):
        """Gets a database connection for the current thread."""
        if not hasattr(self.local, 'conn'):
            try:
                self.local.conn = sqlite3.connect(self.db_name)
                self.local.conn.row_factory = sqlite3.Row
                logging.info("New database connection for thread %s.", threading.current_thread().name)
            except sqlite3.Error as e:
                logging.error(f"Database connection error: {e}")
                return None
        return self.local.conn

    def close_conn(self):
        """Closes the database connection for the current thread."""
        if hasattr(self.local, 'conn') and self.local.conn:
            self.local.conn.close()
            logging.info("Database connection closed for thread %s.", threading.current_thread().name)

    def _execute_query(self, query, params=(), fetch=None):
        """
        Internal helper to execute a query.
        'fetch' can be 'one', 'all', or None.
        """
        conn = self.get_conn()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch == 'one':
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch == 'all':
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"SQLite query error: {e}")
            return None

    def create_tables(self):
        """Creates the necessary database tables."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, breed TEXT NOT NULL,
                age INTEGER NOT NULL, description TEXT, image_path TEXT
            );""",
            """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT, price REAL
            );""",
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL
            );""",
            """
            CREATE TABLE IF NOT EXISTS user_wishlist (
                id INTEGER PRIMARY KEY, user_id INTEGER, pet_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (pet_id) REFERENCES pets(id)
            );""",
            """
            CREATE TABLE IF NOT EXISTS user_adoptions (
                id INTEGER PRIMARY KEY, user_id INTEGER, pet_id INTEGER, adoption_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (pet_id) REFERENCES pets(id)
            );""",
            """
            CREATE TABLE IF NOT EXISTS user_bookings (
                id INTEGER PRIMARY KEY, user_id INTEGER, service_id INTEGER, booking_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (service_id) REFERENCES services(id)
            );"""
        ]
        for query in queries:
            self._execute_query(query)
        logging.info("Database tables checked/created.")

    def populate_sample_data(self):
        """Populates the database with initial sample data if tables are empty."""
        if not self._execute_query("SELECT id FROM pets LIMIT 1;", fetch='one'):
            pets_data = [
                ("Buddy", "Golden Retriever", 3, "A friendly and playful dog.", "p1.jpg"),
                ("Whiskers", "Tabby Cat", 2, "An independent cat who enjoys sunbathing.", "p2.jpg"),
                ("Max", "German Shepherd", 5, "Loyal and energetic.", "p3.jpg"),
                ("Luna", "Siamese Cat", 1, "A curious kitten who loves to play.", "p4.jpg"),
                ("Rocky", "Labrador", 4, "A sweet and gentle giant.", "p5.jpg"),
                ("Milo", "Beagle", 2, "A happy and outgoing dog.", "p6.jpg"),
                ("Chloe", "Persian Cat", 3, "An elegant and calm cat.", "p7.jpg"),
                ("Daisy", "Poodle", 1, "A smart and mischievous pup.", "p8.jpg"),
                ("Zoe", "Dachshund", 6, "A spirited and brave little dog.", "p9.jpg"),
                ("Oliver", "Maine Coon", 4, "A large and gentle cat.", "p10.jpg"),
            ]
            for pet in pets_data:
                self._execute_query("INSERT INTO pets (name, breed, age, description, image_path) VALUES (?, ?, ?, ?, ?)", pet)
            logging.info("Sample pet data populated.")

        if not self._execute_query("SELECT id FROM services LIMIT 1;", fetch='one'):
            services_data = [
                ("Grooming", "Full grooming service.", 50.00),
                ("Vet Checkup", "Comprehensive health checkup.", 75.00),
                ("Pet Training", "Basic obedience training.", 150.00),
                ("Daycare", "Supervised daily care.", 30.00),
                ("Boarding", "Overnight care and lodging.", 40.00),
            ]
            for service in services_data:
                self._execute_query("INSERT INTO services (name, description, price) VALUES (?, ?, ?)", service)
            logging.info("Sample service data populated.")

    def get_pets(self, query=None, filters=None):
        """Fetches a list of pets, optionally with search query and filters."""
        sql = "SELECT * FROM pets"
        params = []
        where_clauses = []
        if query:
            where_clauses.append("(name LIKE ? OR breed LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        return self._execute_query(sql, tuple(params), fetch='all')

    def get_services(self, query=None):
        """Fetches a list of services, optionally with a search query."""
        sql = "SELECT * FROM services"
        params = []
        if query:
            sql += " WHERE name LIKE ?"
            params.append(f"%{query}%")
        return self._execute_query(sql, tuple(params), fetch='all')

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
        row = self._execute_query("SELECT id, password_hash FROM users WHERE username = ?", (username,), fetch='one')
        if row and argon2.verify(password, row['password_hash']):
            logging.info(f"User {username} authenticated successfully.")
            return row['id']
        logging.warning(f"Failed authentication attempt for user: {username}")
        return None

    def get_user_by_id(self, user_id):
        """Fetches user details by ID."""
        return self._execute_query("SELECT id, username, email FROM users WHERE id = ?", (user_id,), fetch='one')
    
    def add_adopted_pet(self, user_id, pet_id):
        """Adds an adopted pet to a user's history."""
        self._execute_query("INSERT INTO user_adoptions (user_id, pet_id, adoption_date) VALUES (?, ?, date('now'))", (user_id, pet_id))

    def add_booking(self, user_id, service_id, booking_date):
        """Adds a service booking to a user's history."""
        self._execute_query("INSERT INTO user_bookings (user_id, service_id, booking_date) VALUES (?, ?, ?)", (user_id, service_id, booking_date))


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

class DataWorker(threading.Thread):
    """
    Worker thread to perform database operations in the background,
    preventing the UI from freezing.
    """
    def __init__(self, db_manager, operation, result_queue, **kwargs):
        super().__init__()
        self.db = db_manager
        self.operation = operation
        self.kwargs = kwargs
        self.result_queue = result_queue
        self.daemon = True # Allows main thread to exit even if worker is running

    def run(self):
        """Executes the requested database operation and puts the result in a queue."""
        try:
            result = None
            if self.operation == 'get_pets':
                result = self.db.get_pets(self.kwargs.get('query'), self.kwargs.get('filters'))
            elif self.operation == 'get_services':
                result = self.db.get_services(self.kwargs.get('query'))
            elif self.operation == 'verify_user':
                result = self.db.verify_user(self.kwargs['username'], self.kwargs['password'])
            elif self.operation == 'add_user':
                result = self.db.add_user(self.kwargs['username'], self.kwargs['email'], self.kwargs['password'])
            
            # Put the result and operation type into the queue for the main thread
            self.result_queue.put((self.operation, result))
            
        except Exception as e:
            logging.error(f"Error in DataWorker thread: {e}")
            self.result_queue.put((self.operation, e))
        finally:
            self.db.close_conn()
