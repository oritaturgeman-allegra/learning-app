# Design System

Visual design language for Ariel's English Adventure — a playful, kid-friendly learning app.

## Design Principles

1. **Playful & Colorful** — Bright pastels, emojis, and animations keep a 9-year-old engaged
2. **Pink Theme** — Pink bows background, pastel game cards, warm feminine aesthetic
3. **RTL-First** — Hebrew UI is right-to-left; English content elements switch to LTR
4. **Big Touch Targets** — All interactive elements sized for easy tapping
5. **Immediate Feedback** — Every action gets visual + audio response

---

## Color Palette

### CSS Custom Properties (Design Tokens)

Defined in `frontend/static/css/shared.css`. Math overrides in `frontend/static/css/math.css`.

```css
:root {
    /* Core Colors */
    --purple: #a855f7;
    --orange: #f97316;
    --yellow: #eab308;
    --pink: #ec4899;
    --green: #22c55e;
    --blue: #3b82f6;
    --red: #ef4444;
    --bg: #f5f0ff;        /* English page background (soft lavender) */
    /* Math overrides --bg: #f0f7ff (soft blue) in math.css */
    --white: #ffffff;
    --text-dark: #1e1b4b;
    --text-muted: #6b7280;
    --gold: #f59e0b;      /* Star rewards */
    --gold-bg: #fef3c7;
}
```

### English Game Card Colors

| Card | Class | Background | Game |
|------|-------|-----------|------|
| Purple | `.game-card-word-match` | `#c4b5fd` | Word Match |
| Orange | `.game-card-sentence-builder` | `#fdba74` | Sentence Builder |
| Blue | `.game-card-listen-choose` | `#7dd3fc` | Listen & Choose |
| Pink | `.game-card-true-false` | `#f9a8d4` | True or False |

### Math Game Card Colors

| Card | Class | Background | Game |
|------|-------|-----------|------|
| Light Blue | `.game-card-quick-solve` | `#93c5fd` | Quick Solve |
| Mint | `.game-card-missing-number` | `#6ee7b7` | Missing Number |
| Rose | `.game-card-true-false-math` | `#fda4af` | True or False |
| Lavender | `.game-card-bubble-pop` | `#c4b5fd` | Bubble Pop |

### Answer Feedback Colors

| State | Color | Usage |
|-------|-------|-------|
| Correct | `--green` (#22c55e) | Answer button background |
| Wrong | `--red` (#ef4444) | Answer button background |
| Star earned | `--gold` (#f59e0b) | Star animations |

---

## Typography

| Token | Font | Usage |
|-------|------|-------|
| `--font-display` | Fredoka | Headings, titles, game UI |
| `--font-body` | Rubik | Body text, Hebrew content, descriptions |

Both fonts loaded from Google Fonts with system font fallbacks.

---

## Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | 4px | Tight gaps |
| `--space-sm` | 8px | Small padding |
| `--space-md` | 16px | Standard gap |
| `--space-lg` | 24px | Section spacing |
| `--space-xl` | 32px | Large padding |
| `--space-2xl` | 48px | Hero spacing |

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | 8px | Small buttons |
| `--radius-md` | 16px | Cards, containers |
| `--radius-lg` | 24px | Large cards |
| `--radius-xl` | 32px | Hero elements |
| `--radius-pill` | 9999px | Pill buttons, tags |

---

## Gradients

```css
--grad-purple: linear-gradient(135deg, #a855f7, #7c3aed);  /* Game buttons */
--grad-orange: linear-gradient(135deg, #f97316, #eab308);  /* Highlights */
--grad-pink: linear-gradient(135deg, #ec4899, #a855f7);    /* Accents */
--grad-green: linear-gradient(135deg, #22c55e, #10b981);   /* Success */
--grad-rainbow: linear-gradient(90deg, #ef4444, #f97316, #eab308, #22c55e, #3b82f6, #a855f7);
--grad-welcome: linear-gradient(135deg, #a855f7, #ec4899, #f97316);
```

---

## Backgrounds

### Page Background
```css
background: #f5f0ff;  /* Soft lavender */
```

### Session Picker Screen
```css
background: linear-gradient(135deg, #ede9fe, #fce7f3, #fff7ed);
background-size: 400% 400%;
animation: gradientCycle 8s ease infinite;
```

### Menu Screen
```css
background: #fce4ec;  /* Soft pink header */
background: url('/static/bg-bows.svg') repeat;  /* Pink bows pattern */
background-size: 250px 250px;
```

---

## Components

### Session Cards (Session Picker)
```css
.session-card {
    padding: var(--space-xl);
    border-radius: var(--radius-lg);
    background: white;
    min-height: 120px;
    direction: rtl;
    border: 2px solid transparent;
    box-shadow: 0 4px 20px rgba(168, 85, 247, 0.12);
}
.session-card:hover {
    border-color: var(--purple);
    transform: translateY(-4px);
}
```

Layout: emoji (3rem) | info (name, Hebrew subtitle, star badge) | arrow. Session picker screen has a soft gradient background (`#ede9fe → #fce7f3 → #fff7ed`).

### Game Cards (Menu)
```css
.game-card {
    padding: var(--space-lg) var(--space-xl);
    border-radius: var(--radius-md);
    color: white;
    min-height: 100px;
    direction: rtl;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.game-card:hover { transform: translateY(-4px); }
```

### Answer Buttons
```css
.answer-btn {
    padding: var(--space-md) var(--space-lg);
    border-radius: var(--radius-md);
    border: 2px solid #e5e7eb;
    background: white;
    font-size: 1.1rem;
}
```

### Star Counter
```css
.star-counter {
    background: var(--gold-bg);
    border-radius: var(--radius-pill);
    padding: var(--space-xs) var(--space-md);
}
```

### Home Button
```css
.home-btn {
    background: none;
    border: 2px solid rgba(0, 0, 0, 0.12);
    border-radius: var(--radius-pill);
    padding: 6px 14px;
    height: 38px;
    color: var(--text-muted);
}
.home-btn:hover {
    border-color: var(--purple);
    color: var(--purple);
}
```

Pill-shaped 🏠 button on the left side of the header (`.header-left`, absolutely positioned). Links to `/learning` (subject picker). Appears on session picker and game menu screens — not on subject picker (already there) or during gameplay.

### Reset Button
```css
.reset-btn {
    background: #fce4ec;
    border: 2px solid rgba(0, 0, 0, 0.08);
    border-radius: 50%;
    width: 44px;
    height: 44px;
}
```

Replaces the previous shuffle button on the menu screen. Triggers a confirmation dialog before resetting practiced words progress.

### Reset Confirmation Dialog

Modal overlay with Hebrew text asking the user to confirm the reset. Two buttons: confirm (resets via `POST /api/game/reset`) and cancel (dismisses dialog). Uses semi-transparent backdrop to focus attention on the dialog.

---

## Animations

| Animation | Usage | Duration |
|-----------|-------|----------|
| `slideUp` | Menu cards entrance | 0.5s ease-out (staggered) |
| `popIn` | Answer buttons, questions | 0.3s ease-out |
| `starBurst` | Stars earned | 0.6s ease-out |
| `confettiFall` | Game completion | 3s linear |
| `spin` | Reset button | 0.6s ease-in-out |
| `rainbow-shift` | Welcome button gradient | 3s linear infinite |
| `bounce` | Correct answer feedback | 0.4s |

---

## Responsive Breakpoints

```css
@media (max-width: 480px) {
    /* Reduced padding, smaller fonts, compact cards */
    .game-card { padding: var(--space-md) var(--space-lg); min-height: 80px; }
}
```

---

## RTL/LTR Handling

- Root: `<html lang="he" dir="rtl">` — all layout flows right-to-left
- English content: wrapped in `.ltr` class with `direction: ltr; text-align: left;`
- Game cards: explicit `direction: rtl`
- Answer buttons with English: use `.ltr` span

---

## MUI Theme (React Migration — In Progress)

The design tokens above are being migrated to a MUI theme object (`frontend/src/theme.ts`). Key mappings:

- **Direction**: `rtl` — MUI + Emotion RTL cache (`stylis-plugin-rtl`) flips all component styles automatically
- **Palette**: CSS custom properties → `theme.palette` (primary=purple, secondary=pink, success=green, error=red, info=blue, warning=gold)
- **Typography**: Fredoka for headings + buttons, Rubik for body text — same as legacy
- **Shape**: `borderRadius: 16` (matches `--radius-md`), buttons override to `9999` (pill)
- **Spacing**: MUI default factor of 8 matches our `--space-sm` increment
- **Component overrides**: `MuiButton` (pill shape, no text-transform), `MuiCard` (24px radius)

MUI's responsive grid (`<Grid>`) and breakpoint-aware components replace manual `@media` queries. Touch targets default to 48px minimum (Apple HIG = 44px).
