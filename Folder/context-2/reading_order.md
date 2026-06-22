# Codebase Reading Order Guide

To understand this Flask talent portal project, it is highly recommended to read the files in the following logical sequence. This order starts from application initialization, moves to data structures, and then goes to route controllers and templates.

---

## 1. Application Setup & Configuration

*   **[run.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/run.py)**
    *   *Purpose*: The main entry point of the project. Run this file to start the local development server.
    *   *Significance*: Shows how the Flask application instance is generated and run.
*   **[config.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/config.py)**
    *   *Purpose*: Defines the application environment configurations.
    *   *Significance*: Contains settings for database URIs, secret keys, file size restrictions, and allowed image uploads.
*   **[app/__init__.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/__init__.py)**
    *   *Purpose*: Initializes extensions and builds the app using the factory pattern.
    *   *Significance*: Sets up Flask-SQLAlchemy, Flask-Login, registers the blueprints (auth, main, profile), and creates database tables on startup.

---

## 2. Models & Data Structures

*   **[app/models.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/models.py)**
    *   *Purpose*: Declares the SQLAlchemy database tables and relationships.
    *   *Significance*: Contains the `User` model (with fields like `id`, `username`, `email`, `role`) and the `TalentProfile` model (with fields like `bio`, `skills`, `links`, and `photo_filename`).
*   **[app/schemas.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/schemas.py)**
    *   *Purpose*: Contains Pydantic v2 schemas used for strict validation of forms.
    *   *Significance*: Defines field formats, length limits, matching checks, and regular expressions for password safety.

---

## 3. Route Controllers (Blueprints)

*   **[app/blueprints/auth.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/blueprints/auth.py)**
    *   *Purpose*: Controls user onboarding and session states.
    *   *Significance*: Handles `/auth/register`, `/auth/login` (with login rate limiting), `/auth/logout`, and `/auth/change-password`.
*   **[app/blueprints/profile.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/blueprints/profile.py)**
    *   *Purpose*: Handles profile creation, editing, visual display, and PDF exportation.
    *   *Significance*: Handles photo file saving and directory creation, as well as the PDF export engine route.
*   **[app/blueprints/main.py](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/blueprints/main.py)**
    *   *Purpose*: Houses landing redirections, dashboards, search directories, and admin panels.
    *   *Significance*: Registers the `@admin_required` decorator, handles search query filters, admin panel list/delete routes, and JSON API endpoints.

---

## 4. Frontend Layer (HTML Templates)

*   **[app/templates/base.html](file:///c:/Users/lakshmanan.subbiah/OneDrive%20-%20Perficient,%20Inc/Documents/Project/hc--talentapp-main/app/templates/base.html)**
    *   *Purpose*: The master container template.
    *   *Significance*: Defines CSS stylesheet tokens and links, the universal navigation menu (dynamically displaying "Admin Panel", "Dashboard", or "Login" tabs depending on credentials), flash alerts, and live JS validation handlers.
*   **Forms & Auth**:
    *   `auth/login.html`, `auth/register.html`, `auth/change_password.html` - Form views containing validation placeholders and password strength indicator progress displays.
*   **Profiles & Main Panels**:
    *   `profile_form.html`, `profile_view.html` - Handles profile updates (with file attachments) and clean public viewing layouts (with PDF download link).
    *   `main/dashboard.html`, `main/browse.html` - User hub displaying profile status, and the public talent directory with pagination.
    *   `admin_talents.html` - Table showing users and profiles to let admins delete records.
