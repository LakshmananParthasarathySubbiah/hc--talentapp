# Logical Workflows & Validations Guide

This document outlines the directory structure, file responsibilities, validation systems, and data workflows of the Flask Talent Portal.

---

## 1. Directory Tree & File Highlights

```text
hc--talentapp-main/
│
├── config.py                 # Application configuration values (database, secrets, uploads)
├── run.py                    # Application launch script
│
└── app/                      # Main application module
    ├── __init__.py           # Application factory pattern constructor
    ├── models.py             # Database model definitions (SQLAlchemy)
    ├── schemas.py            # Form validation schemas (Pydantic v2)
    │
    ├── blueprints/           # Blueprint controllers (business logic and routes)
    │   ├── auth.py           # Onboarding, sessions, rate limits
    │   ├── main.py           # Landing, search, admin dashboard, JSON APIs
    │   └── profile.py        # Talent profile creation, editing, viewing, and PDF export
    │
    ├── static/               # Static directory
    │   └── uploads/          # Uploaded profile photos directory
    │
    └── templates/            # HTML views
        ├── base.html         # Master styling and base page structure
        ├── admin_talents.html# Admin panel list and delete table
        ├── profile_form.html # Create / edit profile form
        ├── profile_view.html # Public profile details with PDF export link
        │
        ├── auth/             # Onboarding views
        │   ├── login.html
        │   ├── register.html
        │   └── change_password.html
        │
        └── main/             # Navigation views
            ├── browse.html   # Paginated search directory
            └── dashboard.html# User dashboard status center
```

### File Highlights
*   `run.py`: Standard script launching the app context.
*   `config.py`: Limits uploaded file sizes (`MAX_CONTENT_LENGTH = 2 * 1024 * 1024` / 2MB) and defines image type lists.
*   `app/__init__.py`: Connects extensions (`db`, `login_manager`) to the Flask app object and runs `db.create_all()` to provision the database.
*   `app/models.py`: Houses the database structure.
*   `app/schemas.py`: Prevents invalid database entries by filtering inputs before they reach database commits.
*   `app/blueprints/auth.py`: Directs registration, rate limits IPs, and manages sessions.
*   `app/blueprints/profile.py`: Processes profile creation/modification and compiles PDF records.
*   `app/blueprints/main.py`: Coordinates admin panels, deletion queries, search criteria, and JSON web endpoints.

---

## 2. Core Validation Rules

### A. Database Models (`app/models.py` & `app/schemas.py`)
*   **Username**: Must match regex `^[a-zA-Z0-9_]{3,20}$` (3 to 20 alphanumeric characters or underscores only).
*   **Email**: Checked against regular expression `^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$`. Length restricted to 120 characters max.
*   **Password**: Checked against regular expression `^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,32}$` (8 to 32 characters, requiring at least one uppercase letter, one digit, and one special character).
*   **Biography**: Required field, maximum length capped at 500 characters.
*   **Skills**: Must contain at least one skill.
*   **URLs (GitHub, LinkedIn, Website)**: Checked against URL validation patterns.
*   **Profile Photo**: Restricts attachments to allowed extensions (`png`, `jpg`, `jpeg`, `webp`).

---

## 3. Logical Phase Workflows

### Phase 1: User Registration
```mermaid
graph TD
    A[User fills form] --> B[HTML5 Pattern Validation]
    B -->|Success| C[Submit POST to /auth/register]
    B -->|Failure| Block[Browser blocks submit]
    C --> D[Pydantic Schema Validation]
    D -->|Invalid Data| E[Return Form with Errors]
    D -->|Valid Data| F[Query DB for Username / Email Existence]
    F -->|Exists| G[Show Error: Taken]
    F -->|Unique| H[Hash password using Bcrypt]
    H --> I[Insert User in DB role='user']
    I --> J[Flash Success & Redirect to Login]
```

### Phase 2: Login Flow
```mermaid
graph TD
    A[User enters credentials] --> B[Client-side validation]
    B -->|Success| C[POST /auth/login]
    C --> D[IP Rate Limit Check - max 5 attempts per 10min]
    D -->|Rate Limited| E[Flash Rate Error]
    D -->|Allowed| F[Validate via LoginSchema]
    F -->|Valid| G[Look up user in DB by Email or Username]
    G -->|Found| H[Bcrypt check_password verification]
    H -->|Match| I[Flask-Login login_user session start]
    H -->|Mismatch| J[Record IP attempt & return error]
    I --> K[Redirect to Dashboard or Next Parameter URL]
```

### Phase 3: Profile Creation & Modification
```mermaid
graph TD
    A[User visits form page] --> B[Check if user already has profile]
    B -->|Yes - Edit Route| C[Load existing data in form]
    B -->|No - Create Route| D[Load empty form]
    C & D --> E[User submits form data & file attachment]
    E --> F[Verify form data against ProfileSchema]
    F -->|Valid| G[Verify file extension if photo uploaded]
    G -->|Valid| H[Save photo as USER_ID_securefilename]
    H --> I[Update or insert TalentProfile row]
    I --> J[Commit to database]
    J --> K[Redirect to view_profile]
```

### Phase 4: Admin Management & Profile Deletion
```mermaid
graph TD
    A[Access /admin/talents] --> B[Check login status]
    B -->|Logged In| C[Check user role column]
    B -->|Not Logged In| Redirect[Redirect to Login]
    C -->|role == 'admin'| D[Load admin page with talents table]
    C -->|role != 'admin'| E[Return 403 Forbidden]
    D --> F[Click Delete Profile POST /admin/delete/id]
    F --> G[Decorator confirms admin identity]
    G -->|Confirmed| H[Delete TalentProfile record from DB]
    H --> I[Commit changes & redirect back to /admin/talents]
```

### Phase 5: REST API Access
```mermaid
graph TD
    A[GET /api/talents or GET /api/talents/id] --> B[Query database]
    B -->|Talent Found| C[Assemble data dictionary manually]
    B -->|Not Found| D[Return 404 JSON response]
    C --> E[Return manually-serialized data using jsonify 200]
```

### Phase 6: PDF Profile Export
```mermaid
graph TD
    A[Click Download PDF button /profile/id/pdf] --> B[Check if profile exists]
    B -->|Found| C[Open io.BytesIO stream]
    B -->|Not Found| D[Return 404]
    C --> E[Create ReportLab SimpleDocTemplate]
    E --> F[Inject user name, email, biography, skills, and links]
    F --> G[Generate PDF output stream]
    G --> H[Return PDF to client as attachment with filename]
```
