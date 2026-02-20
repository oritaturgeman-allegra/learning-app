# Ariel's English Adventure 🌟

Gamified English learning for kids — fun, colorful, interactive.

## Project Overview

A TinyTap-inspired web app that teaches English vocabulary to Hebrew-speaking children through 4 mini-games: word matching, sentence building, listening comprehension, and true/false. Features star rewards, confetti animations, sound feedback, and persistent progress.

**Built for:** Ariel, 4th grade, Jet 2 textbook — Unit 2 vocabulary (clothes, seasons, weather, nature, actions, people).

## Recent Updates

| Version  | Date  | Change                                                                                   |
|----------|-------|------------------------------------------------------------------------------------------|
| v1.0.0   | 02/20 | Feature: Ariel's English Adventure — 4 learning games with rewards and animations        |

---

## How to Play

Just open the file in your browser — no installation needed!

```bash
# Option 1: Double-click english-fun.html in Finder

# Option 2: Open from terminal
open english-fun.html

# Option 3: Serve locally
python3 -m http.server 8000
# Then open http://localhost:8000/english-fun.html
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
- ⭐ Star rewards system with localStorage persistence
- 🎉 Confetti rain on correct answers, celebration at milestones
- 🔊 Text-to-speech pronunciation for all English words
- 🎵 Sound effects via AudioContext (chime, buzz, celebration melody)
- 🌟 Bouncing mascot star that wiggles on correct answers
- 📱 Responsive design — works on desktop and mobile
- 🔌 Fully offline — no backend or API calls needed

## Tech Stack

- Single HTML file (~900 lines)
- Vanilla JS + CSS animations
- Web Speech API for pronunciation
- AudioContext for sound effects
- Google Fonts (Fredoka + Rubik)
- localStorage for progress persistence
