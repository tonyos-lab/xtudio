# xtudio — Google Sign-In Setup Guide

Google Sign-In is **optional**. Email and password registration always works without this setup.
Follow these steps only if you want to enable "Continue with Google" on the login and register pages.

---

## Prerequisites
- xtudio running locally (follow `SETUP.md` first)
- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)

---

## Step 1 — Create a Google Cloud Project

1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Click the project dropdown at the top → **New Project**
3. Name it `xtudio-local` (or anything you prefer)
4. Click **Create** and wait for it to be ready
5. Make sure the new project is selected in the dropdown

---

## Step 2 — Configure the OAuth Consent Screen

1. In the left sidebar → **APIs & Services** → **OAuth consent screen**
2. Select **External** → click **Create**
3. Fill in the required fields:
   - **App name:** `xtudio`
   - **User support email:** your email
   - **Developer contact email:** your email
4. Click **Save and Continue** through the remaining steps (Scopes, Test users)
5. On the Summary page click **Back to Dashboard**

---

## Step 3 — Create OAuth Credentials

1. In the left sidebar → **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. Application type: **Web application**
4. Name: `xtudio local`
5. Under **Authorised redirect URIs** → click **+ Add URI** and enter:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
6. Click **Create**
7. A dialog shows your **Client ID** and **Client Secret** — copy both

---

## Step 4 — Add Credentials to .env

Open your `.env` file and update these lines:

```bash
GOOGLE_CLIENT_ID=your-actual-client-id-from-google
GOOGLE_CLIENT_SECRET=your-actual-client-secret-from-google
```

---

## Step 5 — Run the Seed Command

This creates the Site record and a Google SocialApp template record in the database:

```bash
python manage.py seed_google
```

Expected output:
```
  Updated: Site record → domain=127.0.0.1:8000, name=xtudio
  Created: Google SocialApp template record
  ⚠  Placeholder credentials used — update with real values in /admin/

Google OAuth seeding complete.
Next step: go to /admin/socialaccount/socialapp/ and update the
Google SocialApp record with your real Client ID and Secret Key.
```

---

## Step 6 — Update the SocialApp Record in Admin

1. Go to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) (log in with your superuser account)
2. Navigate to **Social Accounts** → **Social applications**
3. Click **Google**
4. Update the fields:
   - **Client id:** paste your real Google Client ID
   - **Secret key:** paste your real Google Client Secret
   - **Sites:** ensure `127.0.0.1:8000` is in the **Chosen sites** list
5. Click **Save**

---

## Step 7 — Test It

1. Go to [http://127.0.0.1:8000/accounts/login/](http://127.0.0.1:8000/accounts/login/)
2. Click **Continue with Google**
3. You should be redirected to Google's login page
4. After signing in, you'll be redirected back to the xtudio dashboard

---

## Troubleshooting

**"Continue with Google" button not showing**
The button only appears when a Google provider is configured. Make sure you ran `python manage.py seed_google` and the SocialApp record exists in admin.

**`SocialApp matching query does not exist` error**
The SocialApp record is missing or not linked to the site. Re-run `python manage.py seed_google` and check the record in `/admin/socialaccount/socialapp/`.

**`redirect_uri_mismatch` error from Google**
The redirect URI in Google Cloud Console doesn't match exactly. Make sure it is:
```
http://127.0.0.1:8000/accounts/google/login/callback/
```
Note: `127.0.0.1` and `localhost` are treated as different URIs — use `127.0.0.1` to match this guide.

**Intermediate "Sign In Via Google" page looks unstyled**
This is a known cosmetic issue — it works correctly. The styling will be fixed in Phase 2.

---

## For Production

When deploying to production, repeat Steps 3–6 with your production domain:
- Add your production redirect URI: `https://yourdomain.com/accounts/google/login/callback/`
- Update the Site record domain to your production domain
- Create a new set of OAuth credentials (or add the production URI to the existing app)
