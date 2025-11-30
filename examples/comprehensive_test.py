#!/usr/bin/env python
"""Comprehensive test demonstrating all MCP tools."""

import asyncio
import json
from mtg_mcp.database import Database
from mtg_mcp.rules_rag import RulesRAG
from mtg_mcp.api_clients import ArchidektClient, EDHRECClient, CommanderSpellbookClient


async def main():
    """Test all major components."""
    print("=" * 70)
    print("MTG MCP Server - Comprehensive Feature Demonstration")
    print("=" * 70 + "\n")

    # Test 1: Database and CSV Ingestion
    print("1. Testing CSV Ingestion and Database...")
    csv_content = """Name,Set,Collector Number,Quantity,Scryfall ID,Colors,Color Identity,CMC
Lightning Bolt,LEA,161,4,test-id-1,R,R,1
Counterspell,LEA,50,2,test-id-2,U,U,2
Path to Exile,EXO,20,1,test-id-3,W,W,1
Sol Ring,LEA,265,3,test-id-4,,,1
Command Tower,CMD,229,1,test-id-5,,,0"""

    db = Database()
    await db.connect()
    result = await db.ingest_manabox_csv(csv_content)
    print(f"   ✓ Ingested {result['cards_added']} cards")
    
    # Test 2: Get Collection Stats
    print("\n2. Testing Collection Statistics...")
    cards = await db.get_all_cards()
    total_cards = len(cards)
    total_quantity = sum(card.quantity for card in cards)
    color_dist = {}
    for card in cards:
        for color in card.color_identity:
            color_dist[color] = color_dist.get(color, 0) + 1
    
    print(f"   ✓ Unique cards: {total_cards}")
    print(f"   ✓ Total quantity: {total_quantity}")
    print(f"   ✓ Color distribution: {json.dumps(color_dist)}")
    
    # Test 3: Color Identity Filtering
    print("\n3. Testing Color Identity Filtering...")
    red_cards = await db.get_cards_by_color_identity(["R"])
    blue_cards = await db.get_cards_by_color_identity(["U"])
    wu_cards = await db.get_cards_by_color_identity(["W", "U"])
    
    print(f"   ✓ Red cards: {len(red_cards)} ({', '.join(c.name for c in red_cards)})")
    print(f"   ✓ Blue cards: {len(blue_cards)} ({', '.join(c.name for c in blue_cards)})")
    print(f"   ✓ W/U compatible: {len(wu_cards)} cards")
    
    await db.close()
    
    # Test 4: Rules RAG Engine
    print("\n4. Testing BM25s Rules RAG Engine...")
    rag = RulesRAG()
    await rag.initialize()
    
    queries = ["protection from", "commander damage", "stack"]
    for query in queries:
        results = await rag.search(query, top_k=2)
        if results:
            print(f"   ✓ '{query}': Found {len(results)} rules")
            print(f"      → Top: Rule {results[0]['rule_number']} (score: {results[0]['score']:.3f})")
    
    # Test 5: API Clients (Note: These may fail if services are down)
    print("\n5. Testing API Client Initialization...")
    
    archidekt = ArchidektClient()
    print("   ✓ Archidekt client initialized")
    await archidekt.close()
    
    edhrec = EDHRECClient()
    print("   ✓ EDHREC client initialized")
    await edhrec.close()
    
    spellbook = CommanderSpellbookClient()
    print("   ✓ Commander Spellbook client initialized")
    await spellbook.close()
    
    print("\n" + "=" * 70)
    print("✅ All components tested successfully!")
    print("=" * 70)
    print("\nThe MCP server is ready to use. Run with:")
    print("  python -m mtg_mcp.server")
    print("\nOr with Docker:")
    print("  docker build -t mtg-mcp . && docker run -i mtg-mcp")


if __name__ == "__main__":
    asyncio.run(main())
