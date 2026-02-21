# Ariel Learning App 🌟

Gamified English learning for kids — fun, colorful, interactive.

## Project Overview

A web app that teaches English vocabulary to Hebrew-speaking children through 4 mini-games: word matching, sentence building, listening comprehension, and true/false. Features star rewards, confetti animations, sound feedback, and persistent progress.

**Built for:** Ariel, Gen Alpha 4th grader, Jet 2 textbook — Unit 2 vocabulary (clothes, seasons, weather, nature, actions, people, body, food, places, descriptions, things).

## Recent Updates

| Version  | Date  | Change                                                                                   |
|----------|-------|------------------------------------------------------------------------------------------|
| v2.6.0   | 02/21 | Feature: Per-session star tracking — each unit card shows its own earned stars             |
| v2.5.0   | 02/21 | Feature: Math subject + subject tabs on all screens — switch between English and Math     |
| v2.4.0   | 02/21 | Feature: Subject picker screen — choose English or Math before picking a unit              |
| v2.3.0   | 02/21 | Feature: Subject-based URL routing — `/learning/english/jet2-unit2` prepares for math     |
| v2.2.0   | 02/21 | Feature: Session picker screen — choose a learning unit before jumping into games         |
| v2.1.0   | 02/21 | Feature: URL routing — `/learning` page persists on refresh, no more losing your place   |

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
