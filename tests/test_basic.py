"""Test basic imports and module structure."""

import pytest


def test_imports():
    """Test that all modules can be imported."""
    from mtg_mcp import models
    from mtg_mcp import database
    from mtg_mcp import api_clients
    from mtg_mcp import rules_rag
    from mtg_mcp import server
    
    assert models is not None
    assert database is not None
    assert api_clients is not None
    assert rules_rag is not None
    assert server is not None


def test_models():
    """Test that Pydantic models work."""
    from mtg_mcp.models import Card, Deck, CommanderIdentity
    
    # Test Card model
    card = Card(
        oracle_id="test-id",
        name="Test Card",
        cmc=1.0,
        type_line="Creature",
        colors=["R"],
        color_identity=["R"]
    )
    assert card.name == "Test Card"
    assert card.oracle_id == "test-id"
    
    # Test Deck model
    deck = Deck(
        id=123,
        name="Test Deck",
        format="commander"
    )
    assert deck.name == "Test Deck"
    
    # Test CommanderIdentity model
    identity = CommanderIdentity(colors=["W", "U", "B", "G"])
    assert len(identity.colors) == 4


@pytest.mark.asyncio
async def test_database_creation():
    """Test database initialization."""
    from mtg_mcp.database import Database
    
    db = Database()
    await db.connect()
    
    count = await db.get_card_count()
    assert count == 0
    
    await db.close()


@pytest.mark.asyncio
async def test_csv_ingestion():
    """Test CSV ingestion."""
    from mtg_mcp.database import Database
    
    csv_content = """Name,Set,Collector Number,Quantity,Scryfall ID,Colors,Color Identity
Lightning Bolt,LEA,161,4,test-id-1,R,R
Sol Ring,LEA,265,1,test-id-2,,"""
    
    db = Database()
    await db.connect()
    
    result = await db.ingest_manabox_csv(csv_content)
    
    assert result["cards_added"] == 2
    assert result["total_cards"] == 2
    
    count = await db.get_card_count()
    assert count == 2
    
    await db.close()


@pytest.mark.asyncio
async def test_color_identity_filtering():
    """Test color identity filtering."""
    from mtg_mcp.database import Database
    
    csv_content = """Name,Set,Collector Number,Quantity,Scryfall ID,Colors,Color Identity
Lightning Bolt,LEA,161,1,test-id-1,R,R
Counterspell,LEA,50,1,test-id-2,U,U
Path to Exile,EXO,20,1,test-id-3,W,W"""
    
    db = Database()
    await db.connect()
    await db.ingest_manabox_csv(csv_content)
    
    # Get cards in red identity
    red_cards = await db.get_cards_by_color_identity(["R"])
    assert len(red_cards) == 1
    assert red_cards[0].name == "Lightning Bolt"
    
    # Get cards in W/U identity (should include W and U cards)
    wu_cards = await db.get_cards_by_color_identity(["W", "U"])
    assert len(wu_cards) == 2
    
    await db.close()
