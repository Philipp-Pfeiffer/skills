#!/usr/bin/env python3
"""
Mensa Karlsruhe MCP Adapter
Provides meal plan access for local AI agents via MCP protocol
"""

import json
import httpx
from datetime import date, timedelta
from typing import Optional

BASE_URL = "https://mensa-api.fnka.de"


async def get_canteens() -> str:
    """Get all available canteens (Mensen)"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{BASE_URL}/canteens")
        resp.raise_for_status()
        data = resp.json()
        return json.dumps(data, indent=2, ensure_ascii=False)


async def get_meal_plan(
    date_str: Optional[str] = None, canteens: Optional[list] = None
) -> str:
    """Get meal plan for a specific date or today if not specified"""
    if date_str is None:
        date_str = date.today().isoformat()

    url = f"{BASE_URL}/plans/{date_str}"
    if canteens:
        url += f"?canteens={','.join(canteens)}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
        return json.dumps(data, indent=2, ensure_ascii=False)


async def get_week_plan(canteens: Optional[list] = None) -> str:
    """Get meal plans for the next 7 days"""
    plans = []
    today = date.today()

    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(7):
            day = today + timedelta(days=i)
            try:
                url = f"{BASE_URL}/plans/{day.isoformat()}"
                if canteens:
                    url += f"?canteens={','.join(canteens)}"
                resp = await client.get(url)
                if resp.status_code == 200:
                    plans.append({**resp.json(), "date_iso": day.isoformat()})
            except httpx.HTTPError:
                continue

    return json.dumps(plans, indent=2, ensure_ascii=False)


async def get_legend() -> str:
    """Get food additives and classifiers legend"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{BASE_URL}/meta/legend")
        resp.raise_for_status()
        data = resp.json()
        return json.dumps(data, indent=2, ensure_ascii=False)


async def search_meals(query: str, days: int = 3) -> str:
    """Search for meals containing a specific term"""
    results = []
    today = date.today()

    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(days):
            day = today + timedelta(days=i)
            try:
                resp = await client.get(f"{BASE_URL}/plans/{day.isoformat()}")
                if resp.status_code == 200:
                    data = resp.json()
                    for canteen_plan in data.get("data", []):
                        for line in canteen_plan.get("lines", []):
                            for meal in line.get("meals", []):
                                if query.lower() in meal.get("name", "").lower():
                                    results.append(
                                        {
                                            "date": day.isoformat(),
                                            "canteen": canteen_plan.get(
                                                "canteen", {}
                                            ).get("name"),
                                            "line": line.get("name"),
                                            "meal": meal.get("name"),
                                            "price": meal.get("price"),
                                        }
                                    )
            except httpx.HTTPError:
                continue

    return json.dumps(results, indent=2, ensure_ascii=False)


def format_meal_for_llm(meal_data: str) -> str:
    """Format meal plan data as human-readable text for LLM context"""
    try:
        data = json.loads(meal_data)
        if not data.get("success"):
            return f"Error: {data.get('error', 'Unknown error')}"

        output = []
        for canteen_plan in data.get("data", []):
            canteen_name = canteen_plan.get("canteen", {}).get("name", "Unknown")
            output.append(f"\n## {canteen_name}\n")

            for line in canteen_plan.get("lines", []):
                line_name = line.get("name", "Unknown")
                meals = line.get("meals", [])

                if meals:
                    output.append(f"\n**{line_name}:**")
                    for meal in meals:
                        name = meal.get("name", "")
                        price = meal.get("price", "")
                        output.append(f"  - {name} ({price})")

        return "\n".join(output) if output else "No meal plans available"
    except json.JSONDecodeError:
        return meal_data


if __name__ == "__main__":
    import asyncio

    async def demo():
        print("=== Mensa Karlsruhe API Demo ===\n")

        print("1. Available Canteens:")
        canteens = await get_canteens()
        data = json.loads(canteens)
        for c in data.get("data", []):
            print(f"   - {c['name']} (ID: {c['id']})")

        print("\n2. Today's Meals (Mensa Am Adenauerring):")
        plan = await get_meal_plan(canteens=["adenauerring"])
        print(format_meal_for_llm(plan)[:1000])

        print("\n3. Searching for 'vegetarisch':")
        results = await search_meals("vegetarisch")
        if results:
            data = json.loads(results)
            for r in data[:3]:
                print(f"   {r['date']}: {r['meal']} @ {r['canteen']}")

    asyncio.run(demo())
