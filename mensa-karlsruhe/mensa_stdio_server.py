#!/usr/bin/env python3
"""
Mensa Karlsruhe - Minimal MCP Server (Stdio)
Uses stdio for communication - works with any MCP client

Usage:
  python mensa_stdio_server.py

Commands via stdin (JSON-RPC 2.0):
  - initialize
  - tools/list
  - tools/call
"""

import json
import sys
import asyncio
import httpx
from datetime import date, timedelta
from typing import Any

BASE_URL = "https://mensa-api.fnka.de"

TOOLS = [
    {
        "name": "get_canteens",
        "description": "List all available canteens (Mensen)",
        "inputSchema": {"type": "object"},
    },
    {
        "name": "get_todays_meals",
        "description": "Get today's meal plan",
        "inputSchema": {
            "type": "object",
            "properties": {"canteens": {"type": "array", "items": {"type": "string"}}},
        },
    },
    {
        "name": "get_meals_by_date",
        "description": "Get meals for a specific date",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "canteens": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["date"],
        },
    },
    {
        "name": "search_meals",
        "description": "Search meals by keyword",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "days": {"type": "integer", "default": 3},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_legend",
        "description": "Get food additives legend",
        "inputSchema": {"type": "object"},
    },
]


async def fetch_json(path: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{BASE_URL}{path}")
        resp.raise_for_status()
        return resp.json()


async def handle_tool(name: str, args: dict) -> str:
    if name == "get_canteens":
        return json.dumps(await fetch_json("/canteens"), indent=2, ensure_ascii=False)

    elif name == "get_todays_meals":
        url = f"/plans/{date.today().isoformat()}"
        if args.get("canteens"):
            url += f"?canteens={','.join(args['canteens'])}"
        return json.dumps(await fetch_json(url), indent=2, ensure_ascii=False)

    elif name == "get_meals_by_date":
        url = f"/plans/{args['date']}"
        if args.get("canteens"):
            url += f"?canteens={','.join(args['canteens'])}"
        return json.dumps(await fetch_json(url), indent=2, ensure_ascii=False)

    elif name == "search_meals":
        results = []
        today = date.today()
        days = args.get("days", 3)

        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(min(days, 7)):
                day = today + timedelta(days=i)
                try:
                    resp = await client.get(f"{BASE_URL}/plans/{day.isoformat()}")
                    if resp.status_code == 200:
                        data = resp.json()
                        for cp in data.get("data", []):
                            for line in cp.get("lines", []):
                                for meal in line.get("meals", []):
                                    if (
                                        args["query"].lower()
                                        in meal.get("name", "").lower()
                                    ):
                                        results.append(
                                            {
                                                "date": day.isoformat(),
                                                "canteen": cp.get("canteen", {}).get(
                                                    "name"
                                                ),
                                                "meal": meal.get("name"),
                                                "price": meal.get("price"),
                                            }
                                        )
                except:
                    pass

        return json.dumps(results, indent=2, ensure_ascii=False)

    elif name == "get_legend":
        return json.dumps(
            await fetch_json("/meta/legend"), indent=2, ensure_ascii=False
        )

    return f"Unknown tool: {name}"


async def main():
    for line in sys.stdin:
        try:
            msg = json.loads(line.strip())
        except:
            continue

        method = msg.get("method")
        msg_id = msg.get("id")

        if method == "initialize":
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {
                                "name": "mensa-karlsruhe",
                                "version": "1.0.0",
                            },
                        },
                    }
                ),
                flush=True,
            )

        elif method == "tools/list":
            print(
                json.dumps(
                    {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
                ),
                flush=True,
            )

        elif method == "tools/call":
            name = msg["params"]["name"]
            args = msg["params"].get("arguments", {})
            content = await handle_tool(name, args)
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {"content": [{"type": "text", "text": content}]},
                    }
                ),
                flush=True,
            )


if __name__ == "__main__":
    asyncio.run(main())
