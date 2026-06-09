# 11RUNCLUB Website — Projekt-Kontext

Website für den 11RUNCLUB, einen Runclub in Solothurn (Schweiz), Instagram: @11.runclub.
Live-Preview: https://11runclub.vercel.app · Repo: https://github.com/FelixKunzJr/11runclub
(Vercel ist mit dem Repo verbunden: Push auf `main` → Production-Deploy, PRs → Preview-URLs.)
Dieses Dokument ist die Wissensbasis: Alles hier wurde im Juni 2026 direkt aus dem
Instagram-Auftritt und Linktree des Clubs recherchiert. Lies zuerst
`corporate-design.md` (CI) und `website-concept.md` (Seitenkonzept) — sie sind verbindlich.

## Projektstand

- [x] Instagram-Recherche & CI-Analyse (Juni 2026)
- [x] Corporate Design definiert → `corporate-design.md`
- [x] Website-Konzept definiert → `website-concept.md`
- [x] Statischer Homepage-Mock → `preview/index.html` (self-contained, kein Build nötig)
- [ ] Feedback des Clubs zur Designrichtung
- [ ] Original-Logodateien & Fotos vom Club besorgen (Farben final abgleichen!)
- [ ] Echte Links einsetzen (WhatsApp/Strava/Insta — aktuell `href="#"` Platzhalter)
- [ ] Umsetzung als Next.js-Projekt (App Router + Tailwind, Deploy auf Vercel)
- [ ] Domain (Vorschlag: 11runclub.ch), danach Link-in-Bio von Linktree auf Website umstellen

## Fakten über den Club (Quelle: Instagram-Bio & Posts, Juni 2026)

- „Dein RUNCLUB in Solothurn." — ~841 Follower, gegründet ~2025
- **Tuesday Run:** jeden Dienstag 18:30, Treffpunkt SOL-ID Athletes World, Klosterplatz 6, 4500 Solothurn
- **Longruns:** samstags 09:30, wahlweise 10 oder 15 km, Start vor dem SOL-ID
- Weitere Formate aus Posts: Hill Reps, Progression Run, Out & Back
- **Keine Anmeldung nötig** (für die wöchentlichen Runs) — zentrale Botschaft, immer kommunizieren
- Slogan: **RUN TOGETHER. IMPROVE TOGETHER. ENJOY TOGETHER.**
- **ENTER HILLCLIMB** — das eigene Rennen des Clubs (Datum aus Insta-Highlight
  „SAVE THE DATE": **FR 25.09.2026**): Staffel-Rennen in 4er-Teams in der ENTER
  Technikwelt Derendingen, die Rampen rauf aufs Parkdeck und runter, ziemlich steil,
  Ziel 100+ Teilnehmende. Startzeit/Reglement/Anmeldung: **Infos folgen** — auf der
  Landing Page (`preview/enter-hillclimb.html`) nichts erfinden, Platzhalter
  „Infos folgen" stehen lassen, bis der Club Details liefert.
- Partner: SOL-ID Athletes World (Treffpunkt/Supporter), peaq hydration („Hydrated by")
- Linktree (linktr.ee/11RUNCLUB) enthält nur: WhatsApp Community + Strava Club.
  Die Website soll das Linktree als Link-in-Bio ersetzen.
- Tonalität: Deutsch, Du-Form, locker, niederschwellig (Insta-Captions teils Schweizerdeutsch,
  Website aber Hochdeutsch)

## Corporate Design — Kurzfassung (Details in corporate-design.md)

- **Farben:** Signal Red `#EE3829` (primär), Coral `#F2594B` (Logo-Kreis), Cobalt `#1E3BD1`
  (Logo-Läufer, sparsam), Track Black `#0D0C0B`, Chalk `#F4F1EB` (warmes Off-White), Ash `#8A857C`.
  ⚠️ Aus Screenshots gemessen — vor Launch mit Original-Logodateien abgleichen.
- **Logo:** korallenroter Kreis, zwei handgezeichnete Läufer in Kobaltblau formen eine „11".
  Original-Dateien fehlen noch; im Mock nur als Badge angedeutet.
- **Typografie:** Anton (Display, Versalien, Druk-Ersatz) · Archivo (Text/UI) ·
  IBM Plex Mono (Daten: Pace, Distanz, Datum — gesperrt gesetzt)
- **Motive:** Kreis (Fotomasken/Badges), rote Routenlinie (animiertes SVG), Zielflaggen-Karo,
  Filmkorn-Grain, riesige „11" als Wasserzeichen
- **Designidee:** „Schweizer Plakat trifft Apple-Scroll-Inszenierung" — Apple-Mechanik
  (eine Aussage pro Sektion, Weissraum, Scroll-Reveals), 11RUNCLUB-Haut (Rot, fette
  Condensed-Versalien, Grain, Bewegungsunschärfe). Der Club wünscht sich explizit
  Apple-Niveau, will aber seine eigene CI behalten.

## Referenzmaterial

`reference/` enthält vom Auftraggeber bereitgestellte Referenzbilder der ENTER
Technikwelt (Axonometrie-Diagramm mit der umlaufenden Rampe aufs Dach-Parkdeck
sowie ein Gebäudefoto). **Nur als Gestaltungsreferenz verwenden, nicht auf der
Website veröffentlichen** — Urheber-/Lizenzlage ungeklärt (Foto vermutlich
Wikimedia, Diagramm vom Architekturbüro). Wichtigste Erkenntnis daraus: Die
Rampe läuft aussen ums Gebäude bis aufs Parkdeck über dem obersten Geschoss —
die Serpentinen-Grafik der Race-Page entspricht dem Prinzip.

## Arbeiten mit dem Mock

```bash
cd preview && python3 -m http.server 8771   # → http://localhost:8771
```

Eine einzige HTML-Datei, Fonts via Google Fonts, kein Build. Enthält: Ticker,
Hero mit Live-Countdown (nächster Dienstag 18:30, lokale Zeit) und Parallax-„11",
„Geheime Route"-Karte (gestrichelte Linie ab SOL-ID, endet im „?"), Format-Karten,
gepinnte Event-Sektion (scrollgesteuerter Aufbau — der eine Apple-Moment der Seite),
Slogan-Marquee, Join-Buttons, Footer und am Ende ein Design-System-Anhang (Style Tile).
`prefers-reduced-motion` wird respektiert — beibehalten.

## Regeln für Weiterentwicklung

- **Kommende Routen sind nie publik** (Clubprinzip, vom Club bestätigt Juni 2026):
  niemals die *echte* Strecke eines zukünftigen Runs zeigen. Eine als solche
  gekennzeichnete **Beispielroute** (~6 km, Solothurn-Schema: Aare-Ufer/Altstadt/St. Ursen)
  ist okay und gewünscht — immer mit Hinweis „Beispielroute, die echte Strecke gibts am Start".
  (Ein früherer „?"-Mystery-Ansatz wurde vom Club verworfen — nicht wieder einführen.)
- **Scroll-Animationen dosiert** (Club mag die Apple-Scroll-Mechanik, Juni 2026):
  Scroll-Reveals überall okay; *ein* gepinnter scrollgesteuerter Moment pro Seite
  (aktuell die Event-Sektion). Kein Scroll-Hijacking, nur transform/opacity animieren.
- Keine Stock-Fotos. Nur echte Club-Fotos (Originale beim Team anfragen, Insta-Screenshots reichen nicht).
- Rot braucht Ruhe drumherum: pro Sektion eine dominante Grundfläche (Chalk/Black/Red).
- Headlines: Anton, Versalien, line-height ~0.9, dürfen am Rand anschneiden.
- Daten immer in IBM Plex Mono mit letter-spacing (Laufuhr-Ästhetik).
- Texte: Deutsch, Du-Form, kurz. „Keine Anmeldung nötig" prominent halten.
- Geplanter Stack für die echte Site: Next.js App Router + Tailwind auf Vercel;
  Events anfangs als JSON/Markdown im Repo, CMS (Sanity) erst wenn das Team selbst pflegen will.
- Vercel-Deployment: statisch aus `preview/` (siehe `vercel.json`).
