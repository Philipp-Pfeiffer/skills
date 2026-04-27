#!/usr/bin/env python3
"""
Mensa Karlsruhe - Simple REST Adapter
Direct HTTP access without MCP dependency
Usage: python mensa_simple.py [command] [args]
"""

import json
import sys
import asyncio
import httpx
from datetime import date, timedelta

BASE_URL = "https://mensa-api.fnka.de"


async def cmd_canteens():
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{BASE_URL}/canteens")
        data = resp.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))


async def cmd_today(canteens=None):
    today = date.today().isoformat()
    url = f"{BASE_URL}/plans/{today}"
    if canteens:
        url += f"?canteens={','.join(canteens)}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        data = resp.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))


async def cmd_date(date_str, canteens=None):
    url = f"{BASE_URL}/plans/{date_str}"
    if canteens:
        url += f"?canteens={','.join(canteens)}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        data = resp.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))


async def cmd_search(query, days=3):
    results = []
    today = date.today()
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
                                if query.lower() in meal.get("name", "").lower():
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
    print(json.dumps(results, indent=2, ensure_ascii=False))


async def cmd_legend():
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{BASE_URL}/meta/legend")
        data = resp.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))


async def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python mensa_simple.py <command> [args]")
        print("Commands:")
        print("  canteens                 - List all canteens")
        print("  today [canteen1,canteen2] - Today's meals")
        print("  date YYYY-MM-DD [canteens] - Meals for date")
        print("  search <term> [days]     - Search meals")
        print("  legend                   - Food additives")
        return

    cmd = args[0]

    if cmd == "canteens":
        await cmd_canteens()
    elif cmd == "today":
        canteens = args[1].split(",") if len(args) > 1 else None
        await cmd_today(canteens)
    elif cmd == "date":
        if len(args) < 2:
            print("Error: date required (YYYY-MM-DD)")
            return
        canteens = args[2].split(",") if len(args) > 2 else None
        await cmd_date(args[1], canteens)
    elif cmd == "search":
        if len(args) < 2:
            print("Error: search term required")
            return
        days = int(args[2]) if len(args) > 2 else 3
        await cmd_search(args[1], days)
    elif cmd == "legend":
        await cmd_legend()
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    asyncio.run(main())
