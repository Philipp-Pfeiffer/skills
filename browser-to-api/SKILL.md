---
name: browser-to-api
slug: browser-to-api
version: 1.0.0
description: "Replay-driven API discovery. Consume a browser-trace capture, pair CDP request/response events, templatize observed URLs, infer JSON schemas from samples, and emit an OpenAPI 3.1 document plus a human-readable coverage report. Purely offline post-processing on browser-trace's cdp/network/*.jsonl buckets."
metadata: {"clawdbot":{"emoji":"🌐","requires":{},"os":["linux","darwin","win32"]}}
---

# browser-to-api

Replay-driven API discovery from browser network traces.

## What it does

1. **Consumes** Chrome DevTools Protocol (CDP) network traces (`requests.jsonl` + `responses.jsonl`)
2. **Pairs** Request / Response events
3. **Templatizes** observed URLs (path parameters, query patterns)
4. **Infers** JSON schemas from response samples
5. **Emits** an OpenAPI 3.1 document + human-readable coverage report + client stub (`client.mjs`)

## Input / Output

```
browser-trace  →  .o11y/<run>/cdp/network/{requests,responses}.jsonl
browser-to-api →  .o11y/<run>/api-spec/index.html + openapi.yaml + client.mjs
```

## When to use

- The user wants an **OpenAPI document** for a **third-party or undocumented website API** (e.g. Airbnb, booking platforms, internal tools without published docs).
- The user has a **browser-trace run** and wants endpoints + schemas extracted from it.
- The user is **building a client/SDK** against a site that doesn't publish a spec.
- The user wants a **coverage report** showing which flows would broaden the spec.

## Prerequisites

**browser-trace** must capture traffic first. This skill is purely offline post-processing — it does not capture traffic itself.

## Practical use cases

| Scenario | How |
|---|---|
| **Airbnb search/listings** | Trace search → listings → detail page → extract `/api/v2/search_results`, `/api/v3/pdp_listing_details` endpoints |
| **Booking platforms** | Capture calendar availability, pricing, reservation flows |
| **Internal dashboards** | Document micro-service APIs behind SPA frontends |
| **Competitor research** | Reverse-engineer how a competitor's frontend talks to their backend |

## Notes

- Requires the `browser-trace` skill (or equivalent CDP capture) as input.
- Output is an **OpenAPI 3.1** YAML spec, not a live proxy or scraping tool.
- The generated `client.mjs` can be used as a starting point for programmatic access.
- Coverage report shows which user flows were captured and which endpoints remain undiscovered.
