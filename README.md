# Android Device Information Tracker

A small Flask website with a consent page and password-protected admin dashboard.

## Run locally
1. Install Python 3.10+.
2. In this folder run:
   ```bash
   pip install -r requirements.txt
   ```
3. Set a strong admin password and secret key:
   ```bash
   export ADMIN_PASSWORD='choose-a-long-unique-password'
   export SECRET_KEY='choose-a-long-random-secret'
   python app.py
   ```
4. Open `http://localhost:5000` for the visitor page and `http://localhost:5000/admin` for the dashboard.

On Windows PowerShell, use `$env:ADMIN_PASSWORD="..."` and `$env:SECRET_KEY="..."`.

## Deploy
Deploy to a Python host that supports Flask and persistent disk storage. Configure `ADMIN_PASSWORD` and `SECRET_KEY` as environment variables. Use HTTPS. Ensure the host's forwarded-IP configuration is trusted before relying on the IP field. The SQLite database must be on persistent storage.

## Limitations and privacy
- The visitor must actively tick the consent box and press the submit button.
- The Battery Status API is unsupported or restricted in many browsers; battery percentage and charging state may show as unavailable.
- Device model and brand are only exposed by some browsers through User-Agent Client Hints. They are not guaranteed.
- iOS Safari and many privacy-focused browsers provide limited device details.
- IP address is received by the server and stored with the submission; it may suggest an approximate region but this starter does not perform geolocation.
- No GPS, IMEI, phone number, contacts, photos, or files are collected.
- Add a privacy notice, retention/deletion policy, rate limiting, and production-grade database before public launch.
