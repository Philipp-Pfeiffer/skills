---
name: tailscale-hosting
description: "Host local services, static files, and dashboards securely within a Tailscale tailnet using `tailscale serve`. Use when (1) the user wants to make a local service accessible via a nice HTTPS URL within their tailnet, (2) hosting static HTML files or dashboards, (3) adding/removing/listing tailscale serve paths, (4) exposing a local port (e.g. 3000, 5123) under a custom path like /dashboard. Also covers the critical distinction between `tailscale serve` (private, tailnet-only) and `tailscale funnel` (public internet). NOT for: general web hosting, public-facing production sites, or when the user explicitly wants outside access without Tailscale."
---

# Tailscale Hosting

Securely expose local services and static files within your Tailscale tailnet.

## Core Concepts

### `tailscale serve` — Tailnet-Only (DEFAULT)
- **Scope**: Only devices in your Tailscale tailnet can access the URL
- **URL**: `https://<node>.<tailnet>.ts.net/<path>`
- **Use for**: Dashboards, internal tools, static files, personal projects
- **Security**: No external exposure. Safe by default.

### `tailscale funnel` — Public Internet (DANGER)
- **Scope**: Accessible from the entire internet
- **URL**: Same as serve, but reachable without Tailscale
- **Use for**: Sharing with people who don't have Tailscale (rarely needed)
- **Security**: Opens your service to the public. Requires explicit activation in Tailscale admin console.
- **Rule**: Only use funnel when the user explicitly asks for public access. Default to serve.

## Commands

### Check Status
```bash
tailscale serve status
tailscale serve status --json
```

### Add a Path
```bash
# Proxy a local service
tailscale serve --bg --set-path /dashboard http://localhost:5123

# Serve a static file
tailscale serve --bg --set-path /report http://localhost:8765/report.html

# Serve a directory
tailscale serve --bg --set-path /static http://localhost:8765
```

### Remove a Path
```bash
# Remove specific path
tailscale serve --https=443 off

# Reset all serve config
tailscale serve reset
```

### Background vs Foreground
- `--bg`: Runs in background (persistent across reboots if tailscaled is enabled)
- Without `--bg`: Runs in foreground (stops when terminal closes)

## Security Checklist

Before executing any serve command:

1. **Is the user asking for public access?**
   - Yes → Explain funnel risks, ask for explicit confirmation
   - No → Use `tailscale serve` (tailnet-only)

2. **What is being exposed?**
   - Dashboard with personal data → serve only
   - Static HTML visualization → serve is fine
   - Service with write access → extra caution, authentication required

3. **Does the port already have a listener?**
   - Verify with `curl http://localhost:<port>` before adding serve
   - If no listener, the serve path will return 502

## Common Patterns

### Pattern: Static File Hosting
```bash
# Start a simple HTTP server in the target directory
python3 -m http.server 8765 --directory /path/to/files &

# Expose it via Tailscale
tailscale serve --bg --set-path /sankey http://127.0.0.1:8765

# Result: https://<hostname>.<tailnet>.ts.net/sankey
```

### Pattern: Local Service Proxy
```bash
# App running locally on port 3000
tailscale serve --bg --set-path /app http://localhost:3000
```

### Pattern: Multiple Paths
```bash
tailscale serve --bg --set-path /dashboard http://localhost:5123
tailscale serve --bg --set-path /mockup http://localhost:5124
tailscale serve --bg --set-path /api http://localhost:8080
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `401 Unauthorized` | tailscale serve needs root/sudo | Run with `sudo` or as root |
| `listener already exists` | Port 443 already has serve config | Use `--set-path` to add sub-paths, or `tailscale serve reset` |
| `Funnel is not enabled` | Trying funnel without admin activation | Visit the provided URL to enable, or use serve instead |
| 502 Bad Gateway | No service on the proxied port | Start the local service first |
| URL not resolving | Tailscale not connected | Check `tailscale status` |

## Important Notes

- **Never default to funnel**. Always start with `serve`.
- **serve paths are persistent** when using `--bg` and tailscaled is running.
- **Reset removes ALL paths**. Use with caution.
- **HTTPS is automatic**. Tailscale handles certificates.
