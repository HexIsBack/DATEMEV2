# 💘 DATEME — Django Dating App

> A Tinder-style dating web app built with Django — swipe, match, and chat in real time.

[![Login Screen](screenshots/login.png)](screenshots/login.png)

---

## ⚠️ Demo Project

All users, profiles, and data are fictional and for demonstration purposes only.

---

## ✨ Features

- 🔐 **User Authentication** — Register / login with CAPTCHA image verification and 18+ age gate
- 👤 **Profile Setup** — Upload a photo, set bio, age, gender, location, and dating preferences
- 💨 **Swipe Interface** — Drag-to-swipe card UI (Like 💚 / Pass 👋) using Vanilla JS pointer events + AJAX
- 💞 **Mutual Match Detection** — Server-side check on every swipe; auto-creates a `Match` object and fires a client-side popup
- 💬 **In-App Chat** — Short-poll AJAX chat between matched users (no WebSocket needed)
- 🚩 **Reporting System** — Report profiles for Harassment, Fake Profile, or Inappropriate Content
- 🛡️ **Admin Dashboard** — Staff-only panel with stats, block/unblock users, and report review
- 🟢 **Online Status** — Green badge if user was active within the last 5 minutes

---

## 📸 Screenshots

### Login
[![Login](screenshots/login.png)](screenshots/login.png)

### Discover / Swipe cards
[![Swipe – sakura_ph](screenshots/swipe_sakura.png)](screenshots/swipe_sakura.png)
[![Swipe – juan_dela](screenshots/swipe_juan.png)](screenshots/swipe_juan.png)
[![Profile saved toast](screenshots/profile_saved_swipe.png)](screenshots/profile_saved_swipe.png)

### Profile Setup
[![Profile Setup – no photo](screenshots/profile_setup.png)](screenshots/profile_setup.png)
[![Profile Setup – with photo](screenshots/profile_setup_photo.png)](screenshots/profile_setup_photo.png)

### Matches & Chat
[![Matches list](screenshots/matches_list.png)](screenshots/matches_list.png)
[![Chat with jj_jj22026](screenshots/chat.png)](screenshots/chat.png)

### Report a User
[![Report form](screenshots/report_user.png)](screenshots/report_user.png)

### Admin Dashboard
[![Admin Dashboard](screenshots/admin_dashboard.png)](screenshots/admin_dashboard.png)

---

## 🛠️ Tech Stack

### Backend

| Tool | Purpose |
|---|---|
| **Python 3.11+** | Core language |
| **Django 4.2+** | Web framework (MVT pattern), ORM, session auth |
| **Pillow** | CAPTCHA image generation; profile photo processing |
| **PostgreSQL (Neon)** | Production database — 3 separate databases (users, chat, media) |
| **SQLite** | Local development fallback only (used automatically when no `DATABASE_URL` is set) |
| **dj-database-url** | Parses `DATABASE_URL`-style connection strings into Django settings |
| **psycopg2-binary** | PostgreSQL driver |
| **python-dotenv** | Loads `.env` file for local development |
| **whitenoise** | Serves static files in production (Vercel) |

### Frontend / UI

| Tool | Purpose |
|---|---|
| **Django Templates** | Server-side HTML rendering |
| **Vanilla JS (ES2020)** | Drag-to-swipe gesture, `fetch()` AJAX, chat polling, match popup |
| **Custom CSS** | Dark space-theme, card-stack layout, swipe indicators |
| **Bootstrap 5** | Base grid, navbar, utility classes |

### Hosting / Infrastructure

| Tool | Purpose |
|---|---|
| **Vercel** | Serverless hosting — auto-deploys on every push to `main` |
| **Neon** | Managed PostgreSQL, free tier, one project holding all 3 databases |
| **Gmail SMTP** | Sends password-reset emails |

### Database Architecture

Uses **3 separate databases** routed via a custom `AppRouter` in `settings.py`. In production these are 3 Postgres databases on Neon; locally they fall back to SQLite files automatically if no Postgres URL is configured:

| Database | Env variable | Used by |
|---|---|---|
| `dateme_users` (`users.sqlite3` locally) | `DATABASE_URL` | `accounts`, `profiles`, `matching` apps, sessions, admin, auth |
| `dateme_chat` (`chat.sqlite3` locally) | `CHAT_DATABASE_URL` | `chat` app (messages) |
| `dateme_media` (`media.sqlite3` locally) | `MEDIA_DATABASE_URL` | Profile photos |

---

## ⚙️ JavaScript — How It Works

All client-side logic lives in `static/js/`. No frameworks — pure Vanilla JS.

### 1. Drag-to-Swipe Gesture (`swipe.js`)

Uses the **Pointer Events API** (`pointerdown` / `pointermove` / `pointerup`) to track drag delta. When the drag exceeds a threshold the card is flung off-screen and a like or pass is sent via AJAX.

```javascript
// static/js/swipe.js
const THRESHOLD = 100;   // px before fling triggers
let startX, isDragging = false;

card.addEventListener('pointerdown', e => {
  startX = e.clientX;
  isDragging = true;
  card.setPointerCapture(e.pointerId);  // keep all events on this card
});

card.addEventListener('pointermove', e => {
  if (!isDragging) return;
  const delta = e.clientX - startX;

  // Rotate and translate the card proportional to drag distance
  card.style.transform = `translateX(${delta}px) rotate(${delta * 0.05}deg)`;

  // Fade in the LIKE / PASS indicator overlays
  likeIndicator.style.opacity  = delta > 0 ? delta / THRESHOLD : 0;
  passIndicator.style.opacity  = delta < 0 ? -delta / THRESHOLD : 0;
});

card.addEventListener('pointerup', e => {
  const delta = e.clientX - startX;
  isDragging = false;

  if (Math.abs(delta) > THRESHOLD) {
    flingCard(delta > 0 ? 'like' : 'pass');  // animate off-screen then AJAX
  } else {
    card.style.transform = '';  // snap back to center
    likeIndicator.style.opacity = 0;
    passIndicator.style.opacity = 0;
  }
});

function flingCard(action) {
  const direction = action === 'like' ? 1 : -1;
  card.style.transition = 'transform 0.4s ease';
  card.style.transform   = `translateX(${direction * window.innerWidth}px) rotate(${direction * 30}deg)`;
  card.addEventListener('transitionend', () => sendSwipe(targetUserId, action), { once: true });
}
```

---

### 2. AJAX Swipe — `fetch()` POST (`swipe.js`)

No full page reload on every swipe. Django's view returns JSON so the client can react (match popup, load next card) without leaving the page.

```javascript
// Called after the fling animation ends
async function sendSwipe(targetUserId, action) {
  const res = await fetch('/match/swipe/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),  // Django requires this header
    },
    body: JSON.stringify({ target_id: targetUserId, action })
  });

  const data = await res.json();
  // Response shape: { matched: true/false, match_id: 42 }

  if (data.matched) showMatchPopup(data.match_id);
  loadNextCard();  // reveal next card in the DOM stack
}

// Utility: read a cookie by name (needed for CSRF token)
function getCookie(name) {
  return document.cookie.split('; ')
    .find(r => r.startsWith(name + '='))
    ?.split('=')[1];
}
```

**Django view equivalent (`matching/views.py`):**

```python
@login_required
def swipe(request):
    if request.method == 'POST':
        data      = json.loads(request.body)
        target    = get_object_or_404(User, pk=data['target_id'])
        liked     = data['action'] == 'like'

        Swipe.objects.update_or_create(
            from_user=request.user, to_user=target,
            defaults={'liked': liked}
        )

        # Check for a mutual like
        matched = liked and Swipe.objects.filter(
            from_user=target, to_user=request.user, liked=True
        ).exists()

        match_id = None
        if matched:
            match, _ = Match.objects.get_or_create(
                user1=min(request.user, target, key=lambda u: u.pk),
                user2=max(request.user, target, key=lambda u: u.pk)
            )
            match_id = match.pk

        return JsonResponse({'matched': matched, 'match_id': match_id})

    # GET: render the swipe page
    ...
```

---

### 3. Match Popup (`swipe.js`)

When `fetch()` returns `matched: true`, a hidden overlay fades in with both avatars and a "Start chatting" CTA. No page reload needed.

```javascript
function showMatchPopup(matchId) {
  const overlay = document.getElementById('match-overlay');
  const chatBtn  = overlay.querySelector('#chat-link');

  chatBtn.href = `/chat/${matchId}/`;
  overlay.classList.add('visible');  // CSS handles the fade-in

  overlay.querySelector('#keep-swiping')
    .addEventListener('click', () => overlay.classList.remove('visible'));
}
```

```css
/* templates/matching/swipe.html — embedded <style> */
.match-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.85);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; pointer-events: none;
  transition: opacity 0.35s ease;
  z-index: 999;
}
.match-overlay.visible {
  opacity: 1;
  pointer-events: all;
}
```

---

### 4. Chat Short-Polling (`chat.js`)

Real-time-style chat without WebSockets. `setInterval` fires every 3 seconds and appends only new messages (tracked by last seen ID).

```javascript
// static/js/chat.js
let lastMessageId = 0;

async function pollMessages() {
  const res  = await fetch(`/chat/poll/${matchId}/?since=${lastMessageId}`);
  const data = await res.json();
  // Response: { messages: [{ id, sender_username, text, timestamp, is_mine }, ...] }

  data.messages.forEach(msg => {
    const div = document.createElement('div');
    div.className = `message ${msg.is_mine ? 'mine' : 'theirs'}`;

    div.innerHTML = `
      <span class="bubble">${escapeHtml(msg.text)}</span>
      <span class="ts">${msg.timestamp}</span>
    `;

    chatBox.appendChild(div);
    lastMessageId = Math.max(lastMessageId, msg.id);
  });

  if (data.messages.length) {
    chatBox.scrollTop = chatBox.scrollHeight;  // auto-scroll to latest
  }
}

// Kick off polling immediately then every 3 s
pollMessages();
setInterval(pollMessages, 3000);

// Send a message via AJAX (no page reload)
sendBtn.addEventListener('click', async () => {
  const text = input.value.trim();
  if (!text) return;

  await fetch(`/chat/send/${matchId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ text })
  });

  input.value = '';
  pollMessages();  // immediate refresh after sending
});

// XSS protection — never use innerHTML with raw user content
function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
```

> **Production upgrade path:** Replace `setInterval` polling with [Django Channels](https://channels.readthedocs.io/) (WebSocket) or Server-Sent Events for lower latency.

---

### 5. CAPTCHA Refresh (`register.js`)

CAPTCHA is generated server-side with **Pillow** (distorted text drawn onto a PNG, saved to the session). A "Refresh" button swaps the image without reloading the form.

```javascript
// static/js/register.js
document.getElementById('refresh-captcha')
  .addEventListener('click', async () => {
    const res  = await fetch('/accounts/captcha/refresh/');
    const data = await res.json();
    // Response: { image_url: '/accounts/captcha/image/?v=1719123456' }

    // Cache-bust with a timestamp so the browser doesn't serve the old image
    document.getElementById('captcha-img').src = data.image_url + '&t=' + Date.now();
  });
```

**Django view (`accounts/views.py`):**

```python
import random, string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

def captcha_refresh(request):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    request.session['captcha_code'] = code
    return JsonResponse({'image_url': reverse('captcha_image')})

def captcha_image(request):
    code  = request.session.get('captcha_code', '')
    image = draw_distorted_captcha(code)   # Pillow draws + distorts text
    buf   = BytesIO()
    image.save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type='image/png')
```

---

## 🚀 Quick Start (Local Development)

### 1. Clone the repo
```bash
git clone https://github.com/your-username/DATEME.git
cd DATEME
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your environment variables
```bash
# Copy the template and fill in your own values
cp .env.example .env
```
Edit `.env` and set at minimum `DATEME_EMAIL` and `DATEME_EMAIL_PASSWORD` (a Gmail App Password — see [Get an App Password](https://myaccount.google.com/apppasswords)). Leave `DATABASE_URL`, `CHAT_DATABASE_URL`, and `MEDIA_DATABASE_URL` blank for local dev — the app automatically falls back to local SQLite files when those aren't set.

### 5. Run all migrations
```bash
python manage.py migrate --database=default
python manage.py migrate --database=chat_db
python manage.py migrate --database=media_db
```

### 6. Load dummy data (recommended for demo)
```bash
python manage.py loaddata fixtures.json
python manage.py loaddata chat_fixtures.json --database=chat_db
```

### 7. Create a superuser
```bash
python manage.py createsuperuser
```

### 8. Start the server
```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## 👥 Dummy Users

All passwords: **`Demo@1234`**

| Username | Gender | Location |
|---|---|---|
| `sakura_ph` | Female | Quezon City, PH |
| `juan_dela` | Male | Makati, PH |
| `mia_santos` | Female | Pasig, PH |
| `carlo_v` | Male | BGC, Taguig, PH |
| `ana_lim` | Female | Mandaluyong, PH |
| `marco_t` | Male | Marikina, PH |
| `lily_cruz` | Female | Paranaque, PH |
| `ryan_go` | Male | Las Pinas, PH |
| `nina_b` | Female | Caloocan, PH |
| `alex_m` | Male | Muntinlupa, PH |

### Pre-loaded Matches (with chat messages)

| Match |
|---|
| `carlo_v` ↔ `sakura_ph` |
| `juan_dela` ↔ `mia_santos` |
| `marco_t` ↔ `lily_cruz` |

---

## 🗺️ URL Routes

| URL | Description |
|---|---|
| `/` | Login page |
| `/register/` | Register with CAPTCHA + 18+ age verification |
| `/profiles/setup/` | Edit profile — photo, bio, location, gender |
| `/match/swipe/` | Swipe card stack (GET renders page, POST handles AJAX swipe) |
| `/match/matches/` | Your mutual matches with online status |
| `/chat/<match_id>/` | Direct message with a match |
| `/chat/poll/<match_id>/` | AJAX endpoint — returns new messages since last ID |
| `/match/report/<user_id>/` | Report a user |
| `/accounts/admin-panel/` | Staff-only moderation dashboard |
| `/admin/` | Django admin panel |

---

## 📁 Project Structure

```
DATEME/
├── accounts/          # Custom user model, auth views, admin dashboard, CAPTCHA
├── profiles/          # Profile model, setup form, photo upload
├── matching/          # Swipe logic, Match model, reporting
├── chat/              # Message model, chat views, poll endpoint
├── dateme/            # Django project settings, URL config, DB router
├── templates/         # Shared base templates + per-app templates
├── static/
│   ├── css/           # Dark space-theme CSS
│   └── js/
│       ├── swipe.js   # Drag gesture + AJAX like/pass + match popup
│       ├── chat.js    # Short-poll chat + send message
│       └── register.js # CAPTCHA refresh
├── fixtures.json      # Dummy user/profile/match data
├── chat_fixtures.json # Dummy chat messages
├── manage.py
├── requirements.txt
├── .env.example       # Template for environment variables (safe to commit)
└── .env                # Real secrets — gitignored, never committed
```

---

## ☁️ Deployment (Vercel + Neon)

The app is deployed serverlessly on **Vercel**, backed by 3 **Neon** (managed Postgres) databases. Vercel's serverless filesystem can't persist SQLite writes, so production always uses Postgres — locally, SQLite is still used automatically as a fallback.

### 1. Create the Neon databases

1. Sign up at [neon.tech](https://neon.tech), create one project
2. In the **SQL Editor**, run:
   ```sql
   CREATE DATABASE dateme_users;
   CREATE DATABASE dateme_chat;
   CREATE DATABASE dateme_media;
   ```
3. Grab the connection string for each database from the **Connect** panel (switch the database dropdown for each one)

### 2. Run migrations against Neon

Fill in `DATABASE_URL`, `CHAT_DATABASE_URL`, `MEDIA_DATABASE_URL` in your local `.env` with the 3 Neon strings, then:
```bash
python manage.py migrate --database=default
python manage.py migrate --database=chat_db
python manage.py migrate --database=media_db
python manage.py loaddata fixtures.json
python manage.py loaddata chat_fixtures.json --database=chat_db
```

### 3. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New → Project** → import this repo
2. Vercel auto-detects the Django preset — leave build settings as-is
3. Add these **Environment Variables** (Production and Preview):

| Variable | Value |
|---|---|
| `SECRET_KEY` | a fresh random string — generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.vercel.app` |
| `DATABASE_URL` | Neon `dateme_users` connection string |
| `CHAT_DATABASE_URL` | Neon `dateme_chat` connection string |
| `MEDIA_DATABASE_URL` | Neon `dateme_media` connection string |
| `DATEME_EMAIL` | your Gmail address |
| `DATEME_EMAIL_PASSWORD` | your Gmail App Password |

4. Click **Deploy**

Every subsequent `git push origin main` auto-triggers a redeploy.

### Where secrets live (and don't)

| Location | Has real secrets? |
|---|---|
| GitHub repo / `settings.py` | ❌ No — reads everything from env vars |
| `.env` (local machine) | ✅ Yes — gitignored, never committed |
| `.env.example` (committed) | ❌ No — placeholders only |
| Vercel → Settings → Environment Variables | ✅ Yes — this is the only place production secrets live |

### Before deploying, double check:
1. `DEBUG = False` and `ALLOWED_HOSTS` set to your real domain in Vercel's env vars (not `*`/`True`, which are dev-only defaults)
2. `SECRET_KEY` used in production is different from your local dev key
3. Media files: profile photos are stored as binary blobs in `dateme_media` — fine for a demo/hobby scale, but consider object storage (e.g. S3) if this grows
4. Add rate limiting to the swipe and chat poll endpoints before any real public launch

---

## 🎨 UI Design

The app uses a **dark space-theme**:

| Element | Value |
|---|---|
| Background | Deep navy `#1a1a2e` |
| Accent | Coral-red gradient `#ff6b6b → #ee5a24` |
| Cards | Rounded with shadows + drag-to-swipe gesture |
| Online badge | Neon green `#2ed573` |

---

## 📝 License

Open for personal and educational use. Add your preferred license here.

---

## 🙋 Contributing

Pull requests are welcome! Please open an issue first to discuss what you'd like to change.