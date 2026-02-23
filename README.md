# Ariel Learning App 🌟

Gamified English + Math learning for kids — fun, colorful, interactive.

## Project Overview

A web app that teaches English vocabulary and math skills to Hebrew-speaking children through interactive mini-games. Features star rewards, collectible trophies, confetti animations, sound feedback, and persistent progress across subjects.

**Built for:** Ariel, Gen Alpha 4th grader — English (Jet 2 textbook, Unit 2) and Math (multiplication, division, primes).

## Recent Updates

| Version  | Date  | Change                                                                                   |
|----------|-------|------------------------------------------------------------------------------------------|
| v3.0.3   | 02/23 | Feature: Reset button — fresh word rounds for English games, stars preserved                |
| v3.0.2   | 02/23 | Polish: Hebrew session names in GameMenu, centered back button, TopicSessions title fix    |
| v3.0.1   | 02/23 | Polish: Lavender tint on session cards to distinguish from topic cards in math navigation  |
| v3.0.0   | 02/23 | Major: React is sole frontend — legacy Jinja2 removed, code splitting, served at root     |
| v2.18.0  | 02/23 | Feature: All 4 math games in React — QuickSolve, MissingNumber, MathTrueFalse, BubblePop |
| v2.17.0  | 02/23 | Feature: All 4 English games playable in React — WordMatch, SentenceScramble, ListenAndChoose, TrueFalse |

---

## How to Run

```bash
# Start the server
.venv/bin/python -m backend.web_app

# Open in browser
open http://localhost:8000/
```

## Subjects & Sessions

### English
| Session | Content |
|---------|---------|
| Jet 2: Unit 2 | Clothes, seasons, weather, nature, actions, people, body, food, places, descriptions |

### Math
| Session | Content |
|---------|---------|
| Tens & Hundreds | Multiply/divide by 10s and 100s, properties of 0 and 1, order of operations |
| Two-Digit Multiply | Two-digit × one-digit, two-digit × two-digit |
| Long Division | Long division with remainder, division verification |
| Primes & Divisibility | Prime/composite numbers, divisibility rules (3/6/9), prime factorization |

## Games

### English Games
| Game | Hebrew Name | Description | Stars |
|------|-------------|-------------|-------|
| 🔤 Word Match | ?מה המילה | See emoji + Hebrew, pick the English word | +1⭐ × 10 rounds |
| 📝 Sentence Scramble | תרגמי את המשפט | Read Hebrew sentence, arrange English words | +2⭐ × 6 rounds |
| 👂 Listen & Choose | האזיני ובחרי | Hear English word, pick matching card | +1⭐ × 10 rounds |
| 🤔 True or False | ?כן או לא | Is the English sentence correct? | +1⭐ × 8 rounds |

### Math Games
| Game | Hebrew Name | Description | Stars |
|------|-------------|-------------|-------|
| ⚡ Quick Solve | !פתרי מהר | Pick the correct answer to a math problem | +1⭐ × 10 rounds |
| 🔍 Missing Number | !מצאי את המספר | Find the missing number in an equation | +1⭐ × 8 rounds |
| 🤔 True or False | ?נכון או לא | Is the equation correct? | +1⭐ × 10 rounds |
| 🫧 Bubble Pop | !פוצצי בועות | Pop bubbles with expressions equal to the target | +1⭐ × 8 rounds |

## Features

- 🌈 Vibrant, kid-friendly UI with gradient cards and animations
- ⭐ Star rewards system — combined across all subjects, persistent progress
- 🏆 Collectible reward trophies unlocked at star milestones (6 tiers)
- 🎉 Confetti rain on correct answers, celebration at milestones
- 💡 Smart hints for every math problem type (natural Hebrew explanations)
- 🔊 Text-to-speech pronunciation for English words
- 🎵 Sound effects via AudioContext (chime, buzz, celebration melody)
- 🌟 Bouncing mascot star that wiggles on correct answers
- 📱 Responsive design — works on desktop and mobile
- 📊 Weak word detection — tracks words you get wrong most often

## Tech Stack

- **Backend:** Python 3.13, FastAPI, SQLAlchemy (SQLite dev / PostgreSQL prod)
- **Frontend:** React 19 + TypeScript + MUI 7 + Vite (SPA with code splitting)
- **Audio:** Web Speech API (TTS), AudioContext (sound effects)
- **Fonts:** Google Fonts (Fredoka + Rubik)
- **Storage:** Database (game results, progress) + localStorage (fallback)
- **Languages:** Hebrew UI (RTL) + English/Math content (LTR)

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/game/result` | POST | Save a game result with per-word accuracy |
| `/api/game/progress` | GET | Get stars, games played, weak words, earned rewards |
| `/api/game/practiced-words` | GET | Get practiced words since last reset |
| `/api/game/config` | GET | App config for React SPA (version, sessions, rewards, changelog) |
| `/api/game/reset` | POST | Reset practiced words for fresh round (stars preserved) |
