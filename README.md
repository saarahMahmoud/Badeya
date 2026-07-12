# بادية (Badeya) — Landing Page

Single-file Arabic (RTL) landing page for Badeya, a natural olive-oil / body-care
brand from Marsa Matrouh. `index.html` is the whole site — no build step, no
dependencies.

## How orders work

1. Customer adds products to the cart (client-side only, persisted in
   `localStorage` so a refresh doesn't lose it).
2. Customer fills name / phone / address in the cart drawer and hits
   **"أكّد طلبك على واتساب"**.
3. The order is:
   - Logged as a row in a Google Sheet (via a Google Apps Script Web App —
     see setup below). This is a fire-and-forget backup record.
   - Sent as a pre-filled WhatsApp message to the business number — this is
     the real-time confirmation channel, since WhatsApp still needs a human
     to open it.

## One-time setup: connect the Google Sheet

1. Go to [sheet.new](https://sheet.new) and create a sheet, e.g. "Badeya Orders".
2. In the sheet: **Extensions → Apps Script**.
3. Delete the placeholder code and paste in the contents of
   [`google-apps-script.gs`](google-apps-script.gs) from this repo.
4. **Deploy → New deployment → gear icon → Web app**.
   - Execute as: **Me**
   - Who has access: **Anyone**
5. Click **Deploy**, approve the Google permission prompt (it's your own script).
6. Copy the Web app URL (ends in `/exec`).
7. In `index.html`, find:
   ```js
   const SHEET_WEBAPP_URL = "PASTE_YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL_HERE";
   ```
   and paste your URL in.
8. Every new order will now append a row: Timestamp, Name, Phone, Address,
   Notes, Items, Total.

**If you ever need to change the logic** (add a column, send an email
notification, etc.), edit the Apps Script project directly at
script.google.com, then **Deploy → Manage deployments → Edit → New version**.

## Changing the WhatsApp number

```js
const WA_NUMBER = "201016860556"; // country code, no + and no spaces
```

## Editing products

Products are defined in `index.html` inside `const PRODUCTS = [...]`. Each
entry needs `id`, `img` (a key from `IMGS`), `name`, `size`, `desc`, `price`.
Product photos are embedded as base64 in `const IMGS = {...}` right above it —
to swap a photo, replace its base64 string (or move to real image files, see
"Future enhancements" below).

## Deployment (GitHub Pages, free)

This repo is set up to deploy at `https://hikids-kg.github.io/Badeya/`.

1. Push this folder to `github.com/HiKids-KG/Badeya` (see push instructions
   given separately, since it needs your authenticated GitHub session).
2. On GitHub: **Settings → Pages**.
3. Under "Build and deployment", **Source: Deploy from a branch**.
4. Branch: `main`, folder: `/ (root)` → **Save**.
5. Wait ~1 minute, then the site is live at the URL above.
6. Any future `git push` to `main` redeploys automatically.

## Future enhancements worth considering

- **Extract product images out of base64** into `/images/*.jpg` — cuts page
  weight drastically (currently ~470KB of inline images) and makes WhatsApp/
  Facebook link previews (`og:image`) actually work, since those platforms
  can't fetch data-URIs.
- **Order confirmation email** — the Apps Script can also call
  `MailApp.sendEmail(...)` to notify you or the customer automatically.
- **Payment integration** — Instapay/Fawry/Paymob for online prepayment
  instead of cash-on-delivery only.
- **Analytics** — Google Analytics or Meta Pixel to see where traffic and
  drop-off happen.
- **Reviews/testimonials section** for social proof.
- **Multi-branch inventory / stock flags** if products can sell out.
- **A custom domain** (e.g. `badeya.com`) pointed at GitHub Pages — still free
  hosting, just a paid domain registration (~$10-15/yr).
