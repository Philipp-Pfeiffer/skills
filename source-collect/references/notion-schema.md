# Notion Reference Library — Schema

## Database ID
- **Database ID** (für API-Calls): `cac95d11-69da-434a-a223-60eaf26affdd`
- **Data Source ID** (für Queries/Resolve): `04f32113-9015-4884-8325-7b6c1e29c0d2`

> ⚠️ **Wichtig:** Beim Erstellen von Pages via `ntn api v1/pages` muss `parent.database_id` die echte Database-ID sein, nicht die Data Source ID. Für Queries/`resolve` verwendet man die Data Source ID.

## Properties (Fields)

| Name | Type | Required | Notes |
|------|------|----------|-------|
| Title | `title` | ✅ | Artikel-Titel |
| URL | `url` | ✅ | Quell-URL |
| Author/Source | `rich_text` | ❌ | Handle (Twitter) oder Name |
| Core Insight | `rich_text` | ❌ | 1-2 Sätze Kernaussage |
| Domains | `multi_select` | ❌ | z.B. "AI", "Politics", "Economics" |
| Topics | `multi_select` | ❌ | Spezifischere Tags |
| Quality | `select` | ❌ | "TBD", "High", "Medium", "Low" |
| Type | `select` | ❌ | "Tweet / Thread", "Article", "Thread / Discussion" |
| Status | `select` | ❌ | "Unread", "Read", "Archived" |
| Saved At | `created_time` | ✅ (auto) | Timestamp |

## Type Mapping (lokal → Notion)

| Local Folder | Notion Type |
|-------------|-------------|
| `sources/twitter/` | Tweet / Thread |
| `sources/articles/` | Article |
| `sources/threads/` | Thread / Discussion |

## API Endpoints (via ntn CLI)

```bash
# Create entry via API (use DATABASE_ID, not data_source_id!)
ntn api v1/pages -d '{"parent":{"database_id":"cac95d11-69da-434a-a223-60eaf26affdd"},"properties":{...}}'

# Query all
ntn datasources query DATA_SOURCE_ID --limit 100 --json
```

## Auth
Environment variable `NOTION_API_TOKEN` muss gesetzt sein. Der Token aus `~/.config/notion/api_key` funktioniert; der Keychain-Token nicht.
