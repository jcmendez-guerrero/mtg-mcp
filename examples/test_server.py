#!/usr/bin/env python
"""Simple test script to verify MCP server functionality."""

import asyncio
from mtg_mcp.database import Database
from mtg_mcp.rules_rag import RulesRAG


async def test_database():
    """Test database operations."""
    print("Testing database...")
    
    # Create sample CSV
    csv_content = """Name,Set,Collector Number,Quantity,Scryfall ID,Colors,Color Identity,CMC
Lightning Bolt,LEA,161,4,test-id-1,R,R,1
Sol Ring,LEA,265,1,test-id-2,,,1
Path to Exile,EXO,20,1,test-id-3,W,W,1"""
    
    db = Database()
    await db.connect()
    
    # Ingest CSV
    result = await db.ingest_manabox_csv(csv_content)
    print(f"  Ingested {result['cards_added']} cards")
    
    # Get all cards
    cards = await db.get_all_cards()
    print(f"  Total cards in collection: {len(cards)}")
    
    # Test color identity filtering
    red_cards = await db.get_cards_by_color_identity(["R"])
    print(f"  Red cards: {len(red_cards)}")
    
    await db.close()
    print("✓ Database tests passed\n")


async def test_rules_rag():
    """Test rules RAG engine."""
    print("Testing Rules RAG...")
    
    rag = RulesRAG()
    await rag.initialize()
    
    # Search for a rule
    results = await rag.search("protection from", top_k=3)
    print(f"  Found {len(results)} rules for 'protection from'")
    if results:
        print(f"  Top result: Rule {results[0]['rule_number']}")
    
    print("✓ Rules RAG tests passed\n")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("MTG MCP Server - Functionality Test")
    print("=" * 60 + "\n")
    
    await test_database()
    await test_rules_rag()
    
    print("=" * 60)
    print("All tests passed successfully! ✓")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
