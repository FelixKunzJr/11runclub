# 11RUNCLUB — Website-Konzept

## Idee in einem Satz

**Schweizer Plakat-Design trifft Apple-Scroll-Inszenierung:** grosszügiger Weissraum,
ruhige, präzise Sektionen mit viel Luft (Apple) — aber die Typografie und Energie eines
Race-Day-Posters (11RUNCLUB). Passenderweise ist „Swiss Style" die berühmteste
Design-Tradition der Schweiz — der Club bekommt eine Website, die wie ein
Solothurner Laufplakat von 2026 aussieht.

## Warum nicht einfach „Apple kopieren"

Apple-Websites leben von Produktfotografie und Zurückhaltung. Ein Runclub lebt von
Schweiss, Tempo und Gemeinschaft. Wir übernehmen von Apple die *Mechanik*
(eine Aussage pro Sektion, grosse Typo, weiche Scroll-Reveals, Sticky-Elemente,
hochwertige Übergänge) — aber die *Haut* ist 11RUNCLUB: Signal-Rot, Anton-Versalien,
Grain, Bewegungsunschärfe.

## Seitenstruktur (One-Pager + Unterseiten bei Bedarf)

1. **Ticker-Leiste** (immer sichtbar): Laufband „NÄCHSTER RUN — DI 18:30 — SOL-ID, KLOSTERPLATZ 6"
2. **Hero:** Vollbild. Riesige Headline „DEIN RUNCLUB IN SOLOTHURN.", dahinter
   Club-Foto/Video mit Bewegungsunschärfe. Countdown zum nächsten Run als Mono-Badge.
   Zwei CTAs: „Mitlaufen (WhatsApp)" + „Nächste Runs".
3. **Next Run:** Schwarze Sektion. Mono-Daten: Tag, Zeit, Treffpunkt, Distanzen,
   „keine Anmeldung nötig". Die Route selbst ist vor dem Run **geheim** (Clubprinzip) —
   inszeniert als gestrichelte Linie ab SOL-ID, die im Ungewissen endet:
   „Die Route? Erfährst du am Start."
4. **Was wir machen:** Die Lauf-Formate als Poster-Karten im Insta-Stil:
   TUESDAY RUN · LONGRUN · HILL REPS · PROGRESSION RUN · OUT & BACK.
   Beim Scrollen nacheinander einblenden (Apple-Mechanik).
5. **Events / Races:** Grosse Event-Bühne für selbst organisierte Läufe
   (z. B. Longrun-Events mit SOL-ID). Poster-Look: S/W-Foto, rote Typo, Datum gross,
   Karo-Motiv. Vergangene Events als Archiv-Strip.
6. **Community:** Foto-Marquee (echte Insta-Fotos), Zahl der Läufer:innen,
   Slogan RUN TOGETHER. IMPROVE TOGETHER. ENJOY TOGETHER. als durchlaufende Zeile.
7. **Join:** Drei grosse Buttons — WhatsApp Community, Strava Club, Instagram.
   Ersetzt das bisherige Linktree vollständig (Website wird der neue Link in Bio).
8. **Footer:** Überdimensionierter Wordmark, Partner-Logos (SOL-ID, peaq), Kontakt, Impressum.

## Interaktion & Motion (das „Innovative", ohne Spielerei)

- **Scroll-Reveals** mit Stagger — Inhalte schieben sich präzise ins Bild (IntersectionObserver / Motion).
- **Gepinnter Event-Moment** — Signature-Moment der Seite: Die Event-Sektion bleibt beim
  Scrollen kurz stehen (sticky), Headline und Datum bauen sich scrollgesteuert auf —
  die Apple-Mechanik, bewusst nur an dieser einen Stelle eingesetzt.
- **Marquee-Ticker** oben + Slogan-Marquee — Tempo-Gefühl, läuft endlos wie ein Long Run.
- **Live-Countdown** zum nächsten Dienstag 18:30 — die Seite fühlt sich „in Bewegung" an.
- **Hover:** Poster-Karten kippen leicht / Foto wechselt von S/W zu Farbe.
- Reduziert auf Mobile, `prefers-reduced-motion` respektieren.

## Inhalte / Pflege

- **Events & Runs:** anfangs eine simple JSON/Markdown-Datei im Repo (der Club hat
  wenige Termine); später optional ein kleines CMS (Sanity), wenn das Team selbst
  pflegen will. Countdown auf „jeden Dienstag 18:30" läuft ohne Pflege automatisch.
- **Fotos:** kuratierte Auswahl vom Instagram-Feed (Originaldateien beim Team anfragen).
- **Strava:** Link auf den Strava-Club; optional später Club-Stats (Kilometer der Woche) via Strava API.

## Technik-Empfehlung

- **Next.js (App Router) + Tailwind**, Deployment auf **Vercel** — schnell, gratis im Hobby-Tier, eigene Domain z. B. `11runclub.ch`.
- Ein-Seiten-Architektur, < 1s Ladezeit, Bilder über `next/image`, Fonts self-hosted.
- Mobile-first: 90 % der Insta-Audience kommt vom Handy.

## Nächste Schritte

1. Feedback des Clubs zu Designrichtung einholen (Preview `preview/index.html` zeigen).
2. Original-Logodateien + 15–20 Lieblingsfotos vom Team besorgen, Farbwerte final abgleichen.
3. WhatsApp-/Strava-/Insta-Links und Event-Daten sammeln.
4. Umsetzung als Next.js-Projekt, Domain registrieren, Link in Bio umstellen.
