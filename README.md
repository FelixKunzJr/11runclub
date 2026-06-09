# 11RUNCLUB — Website

Website-Projekt für den [11RUNCLUB](https://www.instagram.com/11.runclub/) — dein Runclub in Solothurn.
Jeden Dienstag, 18:30, SOL-ID Athletes World.

**Run together. Improve together. Enjoy together.**

🔗 **Live-Preview:** https://11runclub.vercel.app

## Was ist hier drin?

| Datei/Ordner | Inhalt |
|---|---|
| `corporate-design.md` | Corporate Design: Farben, Typografie, Motive, Tonalität |
| `website-concept.md` | Website-Konzept: Struktur, Motion, Technik, nächste Schritte |
| `preview/index.html` | Klickbarer Homepage-Mock (statisch, kein Build nötig) |
| `CLAUDE.md` | Projekt-Kontext für [Claude Code](https://claude.com/claude-code) — bitte aktuell halten |

## Preview lokal ansehen

```bash
cd preview && python3 -m http.server 8771
# → http://localhost:8771
```

Oder `preview/index.html` einfach im Browser öffnen.

## Mitarbeiten (mit Claude Code)

Das Repo ist so aufgebaut, dass Claude Code beim Start automatisch den vollen
Projekt-Kontext aus `CLAUDE.md` lädt — inklusive der Instagram-Recherche, des
Corporate Designs und aller offenen Punkte. Einfach:

```bash
git clone <repo-url> && cd 11runclub
claude
```

Wichtig: Wenn du Entscheidungen triffst oder den Stand änderst, **aktualisiere
`CLAUDE.md`** (Checkliste „Projektstand"), damit die nächste Person — Mensch wie
Claude — denselben Wissensstand hat.

## Deployment

Der Mock wird als statische Site aus `preview/` auf Vercel deployt (`vercel.json`).
Die spätere echte Website ist als Next.js-Projekt geplant (siehe `website-concept.md`).
