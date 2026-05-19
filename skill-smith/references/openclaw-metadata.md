# OpenClaw Metadata Examples

Complete examples of `metadata.openclaw` blocks for different skill types.

## Pure Knowledge Skill

No external dependencies, only markdown instructions.

```yaml
---
name: code-style-guide
description: "Enforce project-specific code style rules. Use when reviewing code, formatting files, or discussing naming conventions."
metadata:
  openclaw:
    emoji: "📏"
---
```

## Python Script Skill

Skill that includes Python scripts requiring specific packages.

```yaml
---
name: dwd-weather
description: "German weather forecasts via DWD API. Use when users need weather data for German locations."
metadata:
  openclaw:
    emoji: "🌤️"
    requires:
      bins: ["python3"]
      python: ["requests"]
---
```

## Node.js Script Skill

Skill that includes JavaScript/TypeScript scripts.

```yaml
---
name: bahn-connections
description: "Check Deutsche Bahn train connections and delays. Use when users need train schedules or delay information."
metadata:
  openclaw:
    emoji: "🚆"
    requires:
      bins: ["node"]
      node: ["db-vendo-client"]
---
```

## Multi-Tool Skill

Skill requiring multiple binaries and languages.

```yaml
---
name: data-pipeline
description: "Extract, transform, and load data from various sources. Use when working with data pipelines or batch processing."
metadata:
  openclaw:
    emoji: "🔧"
    requires:
      bins: ["python3", "node", "curl"]
      python: ["pandas", "requests", "sqlalchemy"]
      node: ["csv-parser"]
---
```

## Skill with Optional Dependencies

Some dependencies are only needed for specific features.

```yaml
---
name: image-processor
description: "Process and analyze images. Use when users need image resizing, format conversion, or EXIF data extraction."
metadata:
  openclaw:
    emoji: "🖼️"
    requires:
      bins: ["python3"]
      python: ["pillow"]
---
```

Note: Optional dependencies for advanced features can be documented in the skill body rather than the header.

## Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `emoji` | string | No | Visual identifier displayed in skill listings |
| `requires.bins` | array | No | System binaries the skill needs (e.g., `python3`, `node`, `curl`) |
| `requires.python` | array | No | Python packages installable via pip |
| `requires.node` | array | No | npm packages installable via npm/yarn |
