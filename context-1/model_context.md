# Architectural Walkthrough & Codebase Blueprint

This document acts as an in-depth reference guide to help you master the inner workings of the codebase. It details **what every file includes, what it does, what every function inside does,** and provides a **live walkthrough text** showing how the architecture fits together.

---

# 🚶 Live Walkthrough: How the Architecture Works on the Whole

Imagine a user types `http://127.0.0.1:5000/` into their browser and interacts with the application. Here is the step-by-step walkthrough of how the system processes that interaction:

### Phase 1: Server Bootstrapping & Table Initialization
1. You run `python run.py`.
2. [run.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/run.py) triggers the `create_app()` factory function from [app/\_\_init\_\_.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/__init__.py).
3. The server reads [config.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/config.py) (extracting database credentials, upload directory locations, and file size limits).
4. Flask-SQLAlchemy (`db`) and Flask-Login (`login_manager`) are initialized with the app.
5. All three Blueprints (`auth_bp`, `main_bp`, `profile_bp`) are imported and registered.
6. The database session enters the **Application Context** (`with app.app_context():`), imports [models.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/models.py) to read all schema definitions, and executes `db.create_all()`. This automatically creates the `users` and `talent_profiles` SQL tables if they do not exist.
7. The server goes live and begins listening for HTTP requests.

### Phase 2: Route Navigation & Request Handling
1. **Entering the App**: The user hits `/`. The request is intercepted by the `main` blueprint in [main.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/blueprints/main.py). The `index()` view issues a redirect, pointing the browser to `/auth/login`.
2. **Rendering the Login Form**: The browser requests `/auth/login`. The route controller in [auth.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/blueprints/auth.py) executes the `login()` view. It returns a rendered HTML page using the Jinja2 template [login.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/auth/login.html), which wraps inside the master layout shell [base.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/base.html).
3. **Submitting Credentials**: The user submits the login form. The request goes to `/auth/login` as a `POST` request:
   - The route checks the client IP against `is_rate_limited()`. If okay, it looks up the email or username in the `User` model.
   - It runs `check_password()` using `bcrypt`. If matched, `login_user(user)` is triggered.
   - **Session Creation**: Flask-Login serializes the user's ID, signs it securely, and stores it in the user's browser as a cookie.
   - The user is redirected to the `/dashboard` route.

### Phase 3: Profile CRUD & Image Upload Pipeline
1. **Checking Authorization**: When the user requests `/profile/create` or `/profile/edit`, the route decorator `@login_required` checks if their session cookie contains a valid, serialized user ID.
2. **Uploading a Photo & Inputs**: The user fills in their bio, skills, social links, and uploads a profile image. They submit the form as a `POST`:
   - [profile.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/blueprints/profile.py) intercepts the form data.
   - **Inputs Validation**: It checks if the bio is under 500 characters and skills are filled.
   - **Photo Validation**: It verifies that the photo file has an allowed extension (jpg, png, etc.) using `allowed_file()`.
   - **File Safety**: It sanitizes the original filename using `secure_filename()` and prepends the user's database ID.
   - **File Write**: It creates the storage directory (if it doesn't exist) and writes the image file to `app/static/uploads/`.
   - **Database Persistence**: It inserts/updates the `TalentProfile` record in the database using `db.session.commit()`.
   - The user is redirected to `/profile/<user_id>` to view their completed profile card.

---

# 📂 Detailed File-by-File & Function-by-Function Reference

This section details what every file in the project includes, what it does, and explains the purpose of every class, function, and method.

---

## 🛠️ Root Configuration & Entry Files

### 1. [run.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/run.py)
* **What it includes**: Imports the application factory function `create_app` from the `app` package.
* **What it does**: Acts as the main entry point to start the Flask development server. It instantiates the app and runs it in debug mode.
* **Function Breakdown**:
  * No custom functions. It runs `app.run(debug=True)` under a standard Python module execution block (`if __name__ == "__main__":`).

### 2. [config.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/config.py)
* **What it includes**: Imports `os` (operating system utilities) and `load_dotenv` from `dotenv` (to load environment variables from the `.env` file).
* **What it does**: Holds all configuration values for the application in a unified `Config` class, pulling credentials from the system or environment files.
* **Class & Setting Breakdown**:
  * `Config` class:
    * `SECRET_KEY`: Used by Flask for signing session cookies and flash messages. Defaults to `"dev-secret-change-this"`.
    * `SQLALCHEMY_DATABASE_URI`: Points Flask-SQLAlchemy to the database. Defaults to a local PostgreSQL URI (`postgresql://postgres:password@localhost:5432/talentdb`).
    * `SQLALCHEMY_TRACK_MODIFICATIONS`: Set to `False` to turn off SQLAlchemy's overhead-heavy event modification tracking.
    * `MAX_CONTENT_LENGTH`: Restricts file uploads to `2 MB` (`2 * 1024 * 1024` bytes) to prevent Denial of Service (DoS) disk-space attacks.
    * `UPLOAD_FOLDER`: Computes the absolute file path pointing to `app/static/uploads` where profile pictures are stored.
    * `ALLOWED_EXTENSIONS`: A set of allowed image types (`{"png", "jpg", "jpeg", "webp"}`).

---

## 📦 Core App Module (`app/`)

### 3. [app/\_\_init\_\_.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/__init__.py)
* **What it includes**: Imports `Flask`, `SQLAlchemy`, and `LoginManager`.
* **What it does**: Initializes the SQLAlchemy database object (`db`) and the Flask-Login manager (`login_manager`) globally. It exposes the Application Factory pattern through `create_app()`.
* **Function Breakdown**:
  * `create_app()`:
    * Instantiates the `Flask` application.
    * Configures the app using the parameters defined in `config.py` (`Config` class).
    * Binds `db` and `login_manager` to the active Flask application.
    * Configures the Flask-Login settings (`login_view` redirects unauthorized users to `/auth/login`, and defines authorization alert messages).
    * Imports and registers the three blueprints: `auth_bp`, `main_bp`, and `profile_bp`.
    * Opens a database application context (`with app.app_context():`), imports [app/models.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/models.py), and runs `db.create_all()` to ensure all database tables are generated on startup.

---

### 4. [app/models.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/models.py)
* **What it includes**: Imports `re` (regular expressions), typing indicators, `db` and `login_manager` from the parent package, and `UserMixin` (which provides default implementations for user session methods like `is_active` and `is_authenticated`).
* **What it does**: Outlines the relational database tables, their columns, relationships, validation constraints, and loads users for session monitoring.
* **Function & Class Breakdown**:
  * `validate_email(email)`:
    * **Purpose**: Checks format and length.
    * **Behavior**: Returns an error string if the email is empty, exceeds 120 characters, or fails the `EMAIL_RE` regex pattern. Otherwise returns `None`.
  * `validate_password(password)`:
    * **Purpose**: Enforces password security complexity rules.
    * **Behavior**: Returns an error message if the password fails the `PASSWORD_RE` regex pattern (must be 8-32 characters and contain at least one uppercase letter, one digit, and one special symbol). Otherwise returns `None`.
  * `validate_username(username)`:
    * **Purpose**: Restricts username format.
    * **Behavior**: Returns an error message if the username is empty or fails the `USERNAME_RE` regex pattern (must be 3-20 characters: letters, numbers, and underscores only). Otherwise returns `None`.
  * `User` class (inherits `UserMixin` and `db.Model`):
    * **Purpose**: Maps user account credentials and roles to the `users` table.
    * **Columns**:
      * `id`: Integer primary key.
      * `username`: String (max 20 characters), unique, cannot be null.
      * `email`: String (max 120 characters), unique, cannot be null.
      * `password_hash`: String (max 255 characters), stores the hashed bcrypt password, cannot be null.
      * `role`: String (max 10 characters), defaults to `"user"`, cannot be null.
      * `created_at`: Datetime timestamp, defaults to the server system time.
    * **Relationships**:
      * `profile`: Sets up a one-to-one link with `TalentProfile`. Enforced by `uselist=False`. Includes cascade commands (`cascade='all, delete-orphan'`) to delete profiles automatically if a user is deleted.
  * `TalentProfile` class (inherits `db.Model`):
    * **Purpose**: Maps user talent details (bios, skills, photos) to the `talent_profiles` table.
    * **Columns**:
      * `id`: Integer primary key.
      * `bio`: Text (allows descriptions/summaries), nullable.
      * `skills`: Text (comma-separated or block skills list), nullable.
      * `photo_filename`: String (max 255 characters), references the profile picture file name, nullable.
      * `links`: JSON column, holds custom key-value pairs for social links (GitHub, LinkedIn, Portfolio), nullable.
      * `user_id`: Integer foreign key linked to `users.id`. Enforced as unique to guarantee one profile per user.
  * `load_user(user_id)` (decorated with `@login_manager.user_loader`):
    * **Purpose**: Resolves session storage.
    * **Behavior**: Fetches and returns the active `User` record from the database matching the provided integer ID.

---

## 🎛️ Controllers & Blueprints (`app/blueprints/`)

### 5. [app/blueprints/auth.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/blueprints/auth.py)
* **What it includes**: Imports `bcrypt` (for cryptographic hashing), time modules, data structures (`defaultdict`), Flask routing utilities (Blueprint, templates, requests, flash alerts, and redirects), and Flask-Login authentication state controls.
* **What it does**: Manages registration, logins, session logouts, password revisions, and rate-limiting to block brute-force attempts.
* **Function & Route Breakdown**:
  * `hash_password(plain)`:
    * **Behavior**: Generates a secure salt and returns the hashed UTF-8 password string. Uses a salt cost factor of 12 rounds.
  * `check_password(plain, hashed)`:
    * **Behavior**: Compares a plain text candidate password with the stored hash. Returns `True` if they match, `False` otherwise.
  * `collect_errors(**fields)`:
    * **Behavior**: Iterates over a dictionary of user input fields (email, username, password) and matches them to their respective validation functions in `models.py`. Returns a dictionary of accumulated validation errors.
  * `is_rate_limited(ip)`:
    * **Behavior**: Inspects the list of failed login timestamps for the given client IP. Removes attempts older than 10 minutes. Returns `True` if there are 5 or more failed logins within the last 10 minutes.
  * `record_attempt(ip)`:
    * **Behavior**: Appends the current epoch timestamp to the login attempts list for the given client IP.
  * `register()` (Route: `/auth/register` [GET, POST]):
    * **Behavior**: Resolves user registrations. If a user is already authenticated, redirects them to `/dashboard`. On POST, validates form fields (username, email, passwords) and checks for database duplicates. If errors are present, re-renders the form with error notifications. If valid, hashes the password, writes the user to the database, and redirects them to `/auth/login`.
  * `login()` (Route: `/auth/login` [GET, POST]):
    * **Behavior**: Resolves user logins. Blocks rate-limited IPs. On POST, looks up the user profile matching the email or username. Compares password hashes. If successful, creates the session via `login_user()` and redirects to `/dashboard` (or the previous target URL). If unsuccessful, records the attempt and returns validation errors.
  * `logout()` (Route: `/auth/logout` [GET]):
    * **Behavior**: Destroys the active user login session using `logout_user()`, flashes a logout notification, and redirects to `/auth/login`. Requires authorization.
  * `change_password()` (Route: `/auth/change-password` [GET, POST]):
    * **Behavior**: Allows users to change their password. Verifies the current password, validates the complexity of the new password, hashes it, commits it to the database, and redirects the user to `/dashboard`. Requires authorization.

---

### 6. [app/blueprints/profile.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/blueprints/profile.py)
* **What it includes**: Imports file management modules (`os`), Flask core routing elements, Flask-Login authentication features, and `secure_filename` from `werkzeug.utils` (to sanitize file upload names).
* **What it does**: Handles creating, updating, displaying, and uploading profile cards and profile photos.
* **Function & Route Breakdown**:
  * `allowed_file(filename)`:
    * **Behavior**: Inspects file names and checks if their file extension matches the permitted image formats set in the configuration rules (`png, jpg, jpeg, webp`). Returns `True` or `False`.
  * `create_profile()` (Route: `/profile/create` [GET, POST]):
    * **Behavior**: Creates a new user profile. Blocks users who already have profiles. On POST, extracts biography, skills, and social links (GitHub, LinkedIn, Portfolio Website). If validation checks fail, saves inputs in an ephemeral (unsaved) `TalentProfile` in memory and re-renders the form with validation alerts. If valid, sanitizes any uploaded file using `secure_filename()`, saves the image file to the static upload folder, writes the new profile record to the database, and redirects to the public profile card view. Requires authorization.
  * `edit_profile()` (Route: `/profile/edit` [GET, POST]):
    * **Behavior**: Edits an existing user profile. On POST, validates the form inputs. If the user uploads a new image, it replaces their old image. Updates the bio, skills, and links columns in the database, saves the session database transaction, and redirects the user to `/profile/<user_id>`. Requires authorization.
  * `view_profile(user_id)` (Route: `/profile/<int:user_id>` [GET]):
    * **Behavior**: Displays a user's profile card publicly. Queries the database for the user by ID. Returns `404` (not found) if the user or the user's profile does not exist. Renders the profile page using [profile_view.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/profile_view.html).

---

### 7. [app/blueprints/main.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/blueprints/main.py)
* **What it includes**: Imports Flask routing helpers and Flask-Login authorization tools.
* **What it does**: Serves simple root routes, dashboard pages, and user directories.
* **Function & Route Breakdown**:
  * `index()` (Route: `/` [GET]):
    * **Behavior**: Simple landing page routing. Redirects all hits directly to the login blueprint (`/auth/login`).
  * `dashboard()` (Route: `/dashboard` [GET]):
    * **Behavior**: Renders the main dashboard page for logged-in users using [dashboard.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/main/dashboard.html). Requires authorization.
  * `browse()` (Route: `/browse` [GET]):
    * **Behavior**: Renders [browse.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/main/browse.html) (currently populated with an empty talents list placeholder).

---

## 🎨 Views & Jinja2 Templates (`app/templates/`)

### 8. [app/templates/base.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/base.html)
* **What it includes**: HTML5 structure, Bootstrap 5 CSS link, Google Fonts integration (if any), custom global stylesheet parameters, and Bootstrap 5 JS bundle.
* **What it does**: Acts as the master layout template wrapper. It defines:
  * A standard header, navigation bar (showing Dashboard and Browse for logged-in users, and Login/Signup links for guests).
  * A floating alert box section to render one-time flash messages (`get_flashed_messages()`).
  * A central container block (`{% block content %}`) where sub-templates inject their HTML content.
  * A global JavaScript validation handler that checks input formatting instantly as users type, using Bootstrap validation classes.

### 9. [app/templates/profile_form.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/profile_form.html)
* **What it includes**: Textareas for bio and skills, file input for profile photos, and text inputs for GitHub, LinkedIn, and website links.
* **What it does**: Renders the form UI used for both **creating** and **editing** profile cards. It displays validation warnings below fields and loads current profile attributes into input fields when editing.

### 10. [app/templates/profile_view.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/profile_view.html)
* **What it includes**: Image cards, typography, custom icons/badges, and list blocks.
* **What it does**: Displays the public profile card of a user. Renders the profile picture from `static/uploads/` (or displays a default placeholder if no image exists), shows the bio and skills, and renders links to GitHub, LinkedIn, or personal websites.

### 11. [app/templates/auth/login.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/auth/login.html)
* **What it includes**: Forms, password fields, remember-me check boxes, and button selectors.
* **What it does**: Renders the login form, showing errors if authentication validation fails or if the IP is blocked.

### 12. [app/templates/auth/register.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/auth/register.html)
* **What it includes**: Form fields for username, email, password, and password confirmation.
* **What it does**: Renders the registration form and provides instant user feedback using built-in client-side validation scripts.

### 13. [app/templates/auth/change_password.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/auth/change_password.html)
* **What it includes**: Password inputs (current password, new password, and password confirmation).
* **What it does**: Renders the password modification form.

### 14. [app/templates/main/dashboard.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/main/dashboard.html)
* **What it includes**: Cards, buttons, and alert layouts.
* **What it does**: Displays the dashboard. If the user has a profile, links to their profile card; if not, shows an alert asking them to create one.

### 15. [app/templates/main/browse.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/main/browse.html)
* **What it includes**: Listing blocks and table containers.
* **What it does**: Serves as a placeholder template for searching or browsing other profiles.
