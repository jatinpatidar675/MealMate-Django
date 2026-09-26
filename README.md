# Meal Mate

Meal Mate is a Django food-ordering app with restaurant and menu management, cart quantities, saved delivery addresses, Razorpay checkout, and light/dark themes.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set `DJANGO_SECRET_KEY`, `RAZORPAY_KEY_ID`, and `RAZORPAY_KEY_SECRET`. Django loads this local file on startup; `.env` is ignored by Git.
4. Run `python manage.py migrate` and `python manage.py runserver`.

Run `python manage.py seed_demo_data` to add five sample restaurants and their photo-backed menus. The command can be run again without creating duplicates.

Use Razorpay test-mode keys locally and live keys only in the Render service environment after payment activation. Never commit `.env` or share the secret key in chat.

## Deploy on Render

1. Push the `mealmate` project directory to a GitHub repository.
2. In Render, choose **New** then **Blueprint**, and connect that repository. Render reads `render.yaml`, builds static assets, creates a PostgreSQL database, runs migrations, and seeds the sample restaurants on startup.
3. Add `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in the Render service environment. Use the provider's live credentials only after enabling the account for live payments.
4. Deploy and open the generated `onrender.com` URL.

The Blueprint uses Render's free plans where available. Free services may sleep while idle, and free databases can have storage or lifetime limits; choose a supported paid database plan for durable production data.