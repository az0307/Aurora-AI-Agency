# AutoBoros Cockpit v2

React 19 + Vite rebuild of the original single-file HTML dashboard.

## Features

- **React 19** with `useReducer` state management
- **localStorage persistence** — all jobs, activity, and grouping survive reloads
- **Global search** — filter by title, client, status, or skill (`/` shortcut)
- **New job modal** — quick-add with full form (`n` shortcut)
- **Editable drafts** — L2 job drafts save to localStorage as you type
- **Keyboard shortcuts** — `Escape` closes drawers/modals, `/` focuses search, `n` opens new job
- **Accessibility** — focus trapping, ARIA labels, focus-visible outlines, reduced-motion support
- **Responsive** — collapses to single column on mobile, drawer becomes full-width
- **Deployment ready** — GitHub Actions → Pages, or Docker → anywhere

## Quick start

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Deploy

### GitHub Pages
Push to `main`. The `.github/workflows/deploy.yml` handles the rest. Enable Pages in repo settings → Source: GitHub Actions.

### Docker
```bash
docker build -t autoboros-cockpit .
docker run -p 3000:80 autoboros-cockpit
```

### Static host (Netlify, Vercel, Cloudflare Pages)
Drop the `dist/` folder after `npm run build`.

## Architecture

```
src/
  App.jsx              — root composition
  main.jsx             — React entry
  index.css            — all styles (ported from original)
  data/
    initialData.js     — LADDER, STATUS_ORDER, CLIENT_ORDER, seed data
  context/
    AppContext.jsx     — reducer, persistence, actions, filtered views
  hooks/
    useClock.js        — live clock (30s tick)
    useKeyboard.js     — global shortcuts
  components/
    Header.jsx         — wordmark + live clock
    SearchBar.jsx      — search + new-job button
    Hero.jsx           — horizontal scroll of "needs you" cards
    Stats.jsx          — 4-up metrics bar
    Board.jsx          — groupable card grid (status/level/client)
    Card.jsx           — individual job card
    Feed.jsx           — activity log with pulse dot
    Ladder.jsx         — L0–L4 legend
    Drawer.jsx         — slide-out detail panel with actions
    Modals.jsx         — new job form + confirm delete
    Toast.jsx          — ephemeral bottom notifications
```

## Data model

Jobs are plain objects with these fields:
- `id`, `t` (title), `client`, `status`, `lvl` (0–4), `actor`, `src`
- `skill` (string|null), `steps` (string[]), `ask` (string), `draft` (string|undefined)
- `esc` (bool), `est` (minutes saved), `last` ({ag, ts}), `result` ({label, url}|undefined)

Activity log entries: `{type, t, ts}` where `type` ∈ `['ok','info','you','warn','esc']`.

## License

MIT — same as the original.