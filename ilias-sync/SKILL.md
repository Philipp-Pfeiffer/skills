# ilias-sync Skill

## Zweck
Automatisches Herunterladen von KIT-ILIAS-Materialien (Übungsblätter, Skripte, Videos) via PFERD.

## Setup
- Installiert: `~/.openclaw/workspace/ilias-sync/`
- PFERD-Version: 3.9.0
- Python venv: `~/.openclaw/workspace/ilias-sync/.venv/`

## Verwendung

### Manueller Sync
```bash
~/.openclaw/workspace/ilias-sync/.venv/bin/pferd \
  --config ~/.openclaw/workspace/ilias-sync/config/pferd.conf \
  -C desktop
```

Oder über Wrapper:
```bash
~/.openclaw/workspace/ilias-sync/scripts/sync.sh
```

### Neues Kurs-Target hinzufügen
In `config/pferd.conf` einen neuen `[crawl:...]`-Block anlegen:
```ini
[crawl:HM1]
type = kit-ilias-web
auth = auth:ilias
target = https://ilias.studium.kit.edu/ilias.php?ref_id=XXXXXXX&cmdClass=ilrepositorygui&cmdNode=uk&baseClass=ilRepositoryGUI
```

## Auth
- Keyring-basiert (Service: `PFERD`)
- Username in Config (`u-Kennung`)
- Passwort wird beim ersten Lauf interaktiv abgefragt oder via `keyring.set_password()` gesetzt

## Output
- Standard: `~/.openclaw/workspace/ilias-sync/output/`
- Struktur spiegelt ILIAS-Ordnerstruktur wider
- Transform-Rules können Dateien umbenennen / verschieben

## Status
- ✅ PFERD installiert
- ✅ Config erstellt
- ✅ Wrapper-Script erstellt
- ✅ Credentials
- ⏳ Erst-Test
- ✅ Cron-Job (isolated + agentTurn + MiniMax, timeout 600s — gleiches Pattern wie Daily Wakeup)

## Cron-Konfiguration (OpenClaw)
```json
{
  "name": "ilias-sync",
  "schedule": { "kind": "cron", "expr": "0 9 * * 1-5", "tz": "Europe/Berlin" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "bash $HOME/.openclaw/workspace/ilias-sync/scripts/sync.sh",
    "model": "minimax/MiniMax-M2.7",
    "timeoutSeconds": 600,
    "toolsAllow": ["exec", "message"]
  },
  "delivery": { "mode": "announce", "channel": "whatsapp", "to": "<deine-handynummer>" }
}
```
**Wichtig:** `timeoutSeconds: 600` (nicht 60). Zu kurze Timeouts bei MiniMax führen zu LLM request timeouts. Gleiches Pattern wie Daily Wakeup.
