=======================================================
  HOW PASSWORD RESET WORKS IN DATEME
=======================================================

  USER FLOW:
  1. User registers with their personal email (e.g. juan@gmail.com)
  2. User forgets password → clicks "Forgot Password"
  3. User types their registered email
  4. Django sends a reset link TO juan@gmail.com
  5. User clicks the link → sets a new password ✓

  The reset link is sent FROM a single app email account
  that you (the developer) set up once.

=======================================================
  ONE-TIME SETUP (do this once before running the app)
=======================================================

STEP 1 — Create a .env file in the project root folder:

    DATEME_EMAIL=youremail@gmail.com
    DATEME_EMAIL_PASSWORD=xxxx xxxx xxxx xxxx

STEP 2 — Get a Gmail App Password:
    1. Go to https://myaccount.google.com/security
    2. Turn on 2-Step Verification (if not already on)
    3. Go to https://myaccount.google.com/apppasswords
    4. Click "Create app password" → name it "DateMe"
    5. Copy the 16-character code into DATEME_EMAIL_PASSWORD

    ⚠️  Use the App Password, NOT your real Gmail password.
        Gmail blocks regular passwords for SMTP.

STEP 3 — Install dependencies:

    pip install -r requirements.txt

STEP 4 — Run the server:

    python manage.py runserver

    The .env file is loaded automatically by python-dotenv.

=======================================================
  TESTING
=======================================================
  1. Register a new account using a REAL email you own
  2. Log out
  3. Go to /accounts/password_reset/
  4. Enter that email
  5. Check your inbox — the reset link arrives in seconds

