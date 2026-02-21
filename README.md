# Ariel's English Adventure 🌟

Gamified English learning for kids — fun, colorful, interactive.

## Project Overview

A web app that teaches English vocabulary to Hebrew-speaking children through 4 mini-games: word matching, sentence building, listening comprehension, and true/false. Features star rewards, confetti animations, sound feedback, and persistent progress.

**Built for:** Ariel, 4th grade, Jet 2 textbook — Unit 2 vocabulary (clothes, seasons, weather, nature, actions, people, body, food, places, descriptions, things).

## Recent Updates

| Version  | Date  | Change                                                                                   |
|----------|-------|------------------------------------------------------------------------------------------|
| v2.0.0   | 02/21 | Fix: Word tracker now tracks all vocab from sentences — no missing words after refresh    |
| v1.9.1   | 02/21 | Fix: Reward card popup — simpler reveal animation, auto-dismiss after 5s                  |
| v1.9.0   | 02/21 | Feature: Collectible reward cards — 6 cards to unlock at star milestones + gallery        |
| v1.8.0   | 02/21 | Feature: Full vocabulary coverage — all 55 words guaranteed across one session            |
| v1.7.0   | 02/21 | Feature: Reset button — start a fresh practice round, stars stay forever                 |
| v1.6.3   | 02/20 | UX: Word chip makeover — purple/lavender unpracticed, sage green practiced + bounce anim  |

---

## How to Run

```bash
# Start the server
.venv/bin/python -m backend.web_app

# Open in browser
open http://localhost:8000
```

## Games

| Game | Hebrew Name | Description | Stars |
|------|-------------|-------------|-------|
| 🔤 Word Match | ?מה המילה | See emoji + Hebrew, pick the English word | +1⭐ × 10 rounds |
| 📝 Sentence Scramble | תרגמי את המשפט | Read Hebrew sentence, arrange English words | +2⭐ × 6 rounds |
| 👂 Listen & Choose | האזיני ובחרי | Hear English word, pick matching card | +1⭐ × 10 rounds |
| 🤔 True or False | ?כן או לא | Is the English sentence correct? | +1⭐ × 8 rounds |

## Features

- 🌈 Vibrant, kid-friendly UI with gradient cards and animations
- ⭐ Star rewards system with persistent progress tracking
- 🎉 Confetti rain on correct answers, celebration at milestones
- 🔊 Text-to-speech pronunciation for all English words
- 🎵 Sound effects via AudioContext (chime, buzz, celebration melody)
- 🌟 Bouncing mascot star that wiggles on correct answers
- 📱 Responsive design — works on desktop and mobile
- 📊 Weak word detection — tracks words you get wrong most often

## Tech Stack

- **Backend:** Python 3.13, FastAPI, SQLAlchemy (SQLite)
- **Frontend:** Jinja2-served HTML, vanilla JS + CSS animations
- **Audio:** Web Speech API (TTS), AudioContext (sound effects)
- **Fonts:** Google Fonts (Fredoka + Rubik)

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/game/result` | POST | Save a game result with per-word accuracy |
| `/api/game/progress` | GET | Get stars, games played, weak words, recent history |
| `/api/game/practiced-words` | GET | Get all unique vocabulary words ever practiced |
