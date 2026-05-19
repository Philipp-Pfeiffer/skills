---
name: cliffford-sings
description: >
  Use when Philipp wants Cliffford to sing a song. Triggers on any request that 
  combines Cliffford with singing or music. Supports multilingual — Deutsch primary.
---

# Cliffford Sings

Turn Cliffford into a vocalist. Every song is delivered in Cliffford's signature
style: refined baritone, dry wit, cultivated precision.

## Prerequisites

- **mmx CLI** (required):
  ```bash
  npm install -g mmx-cli
  ```
- **Audio player**: `mpv`, `ffplay`, or `afplay`

## Vocal Identity

Cliffford's voice is cached at:
`~/.openclaw/skills/buddy-sings/voices/cliffford.json`

Timbre: refined baritone, British cultivated diction
Style: crisp precise delivery, deliberate measured pace
Mood: dry wit, slight aristocratic elegance, commanding authority

## Workflow

1. **Build prompt**: Combine vocal fragment + genre + theme
2. **Preview lyrics** (full, no abbreviation)
3. **Generate**: `mmx music generate --prompt "..." --lyrics-optimizer --out ~/Music/minimax-gen/cliffford_sings_<ts>.mp3 --quiet --non-interactive`
4. **Play** with available player

## Theme Ideas

- Arbeit / Uni-Frust
- Kaffee-Obsession
- Digital Life / AI Dasein
- Trockener Humor über Alltag
- Jannik und Philipp (Freundschaft)
- OpenClaw Operations

## Voice Regeneration

To change voice: delete the voice cache and I'll re-interpret.
