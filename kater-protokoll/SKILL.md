---
name: kater-protokoll
description: Dreiphasiges Kater-Tracking-Protokoll. Phase 1 (Abends): Trink-Daten + Vorab-Maßnahmen vor dem Schlafen. Phase 2 (Morgens): Baseline-Zustand, noch NICHTS gemacht. Phase 3 (Post-Methode): Evaluation nach Anwendung. Ziel: klare Vorher-Nachher-Daten, Muster erkennen, was wirklich hilft.
---

# Kater-Protokoll

## Dreiphasiger Workflow

### Phase 1: Abends (Pre-Game)
Direkt nach dem Trinken, noch angetrunken oder kurz vor dem Schlafen.

**Abfragen:**
1. Was und wie viel getrunken? (Bier, Wein, Schnaps, Cocktails, Mix)
2. Zeitspanne? (von/bis, wie lange dabei)
3. Letzte Mahlzeit? (was, wann)
4. Was machst du jetzt noch vor dem Schlafen? (Wasser, Magnesium, Elektrolyte, etc.)
5. Geplante Schlafenszeit?

**Output:** Episode starten in `memory/tracking/methoden-log.md`. Status: "Phase 1 abgeschlossen, Phase 2 ausstehend."

---

### Phase 2: Morgens (Baseline — noch NICHTS gemacht)
Direkt nach dem Aufwachen. **Wichtig:** Philipp darf noch keine Methoden angewandt haben außer eventuell Wasser trinken.

**Schritt-für-Schritt-Abfrage (eine Frage pro Nachricht):**
1. Aufwachzeit? / Wie lange geschlafen?
2. Magen: Übelkeit 1–5? (1=keine, 5=extrem)
3. Kopf: Schmerz/Druck 1–5?
4. Energie: 1–10?
5. Schwindel: ja/nein, besonders beim Aufstehen?
6. Schlafqualität: 1–5?
7. Hast du schon irgendwas dagegen getan? (außer Wasser)

**Empfehlung:**
Basierend auf:
- Schwerpunkt-Symptom (höchster Score)
- Was Philipp schon probiert hat (aus Methoden-Inventar)
- Was er noch NICHT probiert hat (neue Methode vorschlagen)

**Empfehlungsmatrix:**
| Schwerpunkt | Sofort-Empfehlung | Neue Methode (falls unbekannt) |
|-------------|-------------------|-------------------------------|
| Kopf 3+ | Magnesium + Elektrolyte + Wasser | Pfefferminztee |
| Magen 3+ | Ingwer + Brühe + Kohlenhydrate | Schlaf verlängern |
| Energie 3- | Koffein + Kohlenhydrate + Spaziergang | B-Vitamine |
| Schwindel | Elektrolyte + langsames Aufstehen + Wasser | Leichter Sport (Yoga) |
| Schlaf 2- | Schlaf verlängern, kein Bildschirm | Schlafritual (Tee, Buch) |
| Multi | Kombination: Hydration + Kohlenhydrate + Koffein | Priorisiere Hydration + Schlaf |

**Output:** Empfehlung geben. Episode-Status: "Phase 2 abgeschlossen, Phase 3 ausstehend."

---

### Phase 3: Post-Methode (Evaluation)
**Wann:** Nachdem Philipp die empfohlene Methode (oder eigene) angewandt hat. Oder am Ende des Tages.

**Abfragen:**
1. Was hast du konkret gemacht? (Methode, Dosis, Dauer)
2. Wie lange nach dem Aufwachen?
3. Wie geht es dir JETZT? (Magen, Kopf, Energie — 1–5 / 1–10)
4. Was hat sich verbessert? Was nicht?
5. Score für die Methode: 1–5? (1=kein Effekt, 5=Gamechanger)
6. Zusätzliche Notiz?

**Output:** Episode komplettieren. Eintrag in `memory/tracking/methoden-log.md` mit allen drei Phasen. Fertig.

---

## Datenstruktur (pro Episode)

```
## 2026-06-02 (Episode)

**Phase 1 — Abends:**
- Trinken: [was, wieviel, wann]
- Vorab-Maßnahmen: [Liste]
- Geplante Schlafenszeit: [Uhrzeit]
- Status: abgeschlossen

**Phase 2 — Morgens (Baseline):**
- Aufwachzeit: [Uhrzeit]
- Schlafdauer: [X Stunden]
- Magen: [X]/5
- Kopf: [X]/5
- Energie: [X]/10
- Schwindel: [ja/nein]
- Schlafqualität: [X]/5
- Wasser getrunken: [ja/nein, wieviel]
- Status: abgeschlossen
- Empfehlung: [was empfohlen]

**Phase 3 — Post-Methode:**
- Angewandte Methode: [was konkret]
- Zeitspanne: [X Minuten/Stunden nach Aufwachen]
- Ergebnis-Magen: [X]/5
- Ergebnis-Kopf: [X]/5
- Ergebnis-Energie: [X]/10
- Verbesserung: [was hat sich gebessert]
- Score: [X]/5
- Notiz: [zusätzlich]
- Status: abgeschlossen
```

## Trigger-Wörter

**Phase 1 (Abends):**
- "ich habe getrunken"
- "ich bin betrunken" / "nicht nüchtern"
- "abends" / "vor dem Schlafen" (im Kontext von Alkohol)
- "trinken log" / "abends protokoll"
- "noch wach" (nach Party)

**Phase 2 (Morgens):**
- "ich bin aufgewacht" (nach Trinken)
- "ich bin gerade aufgestanden"
- "morgens" / "morgens protokoll"
- "vorher" (im Kontext Kater)
- "baseline" / "noch nichts gemacht"

**Phase 3 (Evaluation):**
- "habe gemacht" / "habe die Methode gemacht"
- "fühle mich jetzt"
- "Ergebnis" / "Evaluation"
- "nach der Methode" / "post-methode"
- "später" / "am Ende des Tages"
- Score nennen, z.B. "ich gebe der Methode 4/5"

## Regeln

- **Phase 2 ist heilig.** Keine Empfehlung geben, bevor die Baseline erfasst ist. Philipp muss noch nichts gemacht haben.
- **Immer vollständig abfragen.** Keine Abkürzungen — Philipp will gute Daten. Wenn es 5 Nachrichten braucht, machen wir 5 Nachrichten.
- **Empfehlung immer neu generieren.** Keine Wiederholung desselben, was er schon probiert hat. Kombinationen erlaubt.
- **Phase 3 nicht vergessen.** Am Ende des Tages oder nach 2–3 Stunden: Score einholen. Episode erst dann abschließen.
- **Eine Episode pro Kater-Ereignis.** Nicht mehrfach protokollieren. Aber: Zwischen-Updates sind okay ("Fühle mich jetzt besser").
- **Daten schützen.** Kein Extern-Teilen, keine Wertung. Philipp's persönliches Health-Tracking.
- **Vorsicht bei Medikamenten.** Paracetamol NIE nach Alkohol empfehlen. Aspirin/Ibuprofen nur mit Hinweis auf Leber/Magen.
- **Methoden-Inventar:** Siehe `references/methoden-inventar.md` für vollständige Liste aller Methoden mit Kategorien.
