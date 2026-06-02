╔═══════════════════════════════════════════════════════╗
║        DateMe — Django Dating App with Auth                                ║
╚═══════════════════════════════════════════════════════╝

⚠️  DEMO PROJECT — All users, profiles, and data are
    fictional and for demonstration purposes only.

QUICK START
───────────
1.  python -m venv venv
2.  venv\Scripts\activate
3.  pip install -r requirements.txt
4.  python manage.py makemigrations accounts profiles matching chat
5.  python manage.py migrate
6.  python manage.py migrate --database=chat_db
7.  python manage.py migrate --database=media_db
8.  python manage.py createsuperuser
9.  python manage.py runserver

LOAD DUMMY DATA (optional but recommended for demo)
────────────────────────────────────────────────────
After step 7, run:

  python manage.py loaddata fixtures.json
  python manage.py loaddata chat_fixtures.json --database=chat_db

Demo account password for ALL dummy users:  Demo@1234

DUMMY USERS INCLUDED
─────────────────────
  sakura_ph   | Female | Quezon City  | Demo@1234
  juan_dela   | Male   | Makati       | Demo@1234
  mia_santos  | Female | Pasig        | Demo@1234
  carlo_v     | Male   | BGC, Taguig  | Demo@1234
  ana_lim     | Female | Mandaluyong  | Demo@1234
  marco_t     | Male   | Marikina     | Demo@1234
  lily_cruz   | Female | Paranaque    | Demo@1234
  ryan_go     | Male   | Las Pinas    | Demo@1234
  nina_b      | Female | Caloocan     | Demo@1234
  alex_m      | Male   | Muntinlupa   | Demo@1234

PRE-LOADED MATCHES
──────────────────
  carlo_v  ↔ sakura_ph  (with chat messages)
  juan_dela ↔ mia_santos (with chat messages)
  marco_t  ↔ lily_cruz  (with chat messages)

FEATURES
────────
  ✅ Registration with 18+ age verification
  ✅ CAPTCHA image verification (distorted text)
  ✅ Profile setup (photo, bio, location, gender)
  ✅ Swipe left/right card UI (drag or buttons)
  ✅ Mutual match detection + popup
  ✅ Matches page with online status
  ✅ Chat between matched users
  ✅ Admin dashboard — stats, block/unblock users
  ✅ Online status indicator
  ✅ 3 SQLite databases (users, chat, media/images)

DATABASES
─────────
  users.sqlite3  — accounts, profiles, matches
  chat.sqlite3   — chat messages
  media.sqlite3  — profile photos (binary storage)

ROUTES
──────
  /                           Login
  /register/                  Register
  /match/swipe/               Swipe cards
  /match/matches/             Your matches
  /chat/<id>/                 Chat with match
  /profiles/setup/            Edit profile
  /accounts/admin-panel/      Admin dashboard (staff only)
  /admin/                     Django admin panel
