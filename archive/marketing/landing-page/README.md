# ATLAS — Landing Page

A self-contained static marketing page (single `index.html`, no build step, no dependencies) for the Atlas Founder Decision OS. Brutalist structure · cinematic motion · giant editorial type · one acid-lime accent (`#D2FF00`).

## Preview locally
```bash
cd landing
python -m http.server 5500
# → http://127.0.0.1:5500
```

## Deploy to Vercel (2 minutes, free)
This repo is already on GitHub, so use the dashboard import — no CLI auth needed from here:

1. Go to **vercel.com → Add New → Project → Import** `krishagarwal175/Project-Atlas`.
2. **Root Directory:** set to `landing`.
3. **Framework Preset:** `Other`. **Build Command:** leave empty. **Output Directory:** `.` (current dir).
4. **Deploy.** Every push to `main` auto-redeploys.

Or via CLI (if you have it): `cd landing && npx vercel --prod`.

## Notes
- Fonts load from Google Fonts (Anton / Space Grotesk / Inter / JetBrains Mono) — allowed on Vercel.
- The **Request Access** form currently stores emails in `localStorage` only. To actually capture signups you need a backend endpoint (`/api/waitlist`) writing to a database — see the hosting options discussed with the team. This is deliberately not wired yet.
- Respects `prefers-reduced-motion`.
