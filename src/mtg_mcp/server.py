"""MCP server for MTG Commander collection management."""

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .api_clients import ArchidektClient, CommanderSpellbookClient, EDHRECClient
from .database import Database
from .rules_rag import RulesRAG

# Initialize server
app = Server("mtg-mcp")

# Global instances
db = Database()
archidekt_client = ArchidektClient()
edhrec_client = EDHRECClient()
spellbook_client = CommanderSpellbookClient()
rules_rag = RulesRAG()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="ingest_manabox_csv",
            description="Ingest ManaBox CSV export into the in-memory card collection database. "
            "CSV should contain card data with columns like Name, Set, Quantity, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "csv_content": {"type": "string", "description": "CSV content as a string"}
                },
                "required": ["csv_content"],
            },
        ),
        Tool(
            name="fetch_archidekt_deck",
            description="Fetch a deck from Archidekt by deck ID. Returns deck information "
            "including name, format, commander, and card list.",
            inputSchema={
                "type": "object",
                "properties": {"deck_id": {"type": "integer", "description": "Archidekt deck ID"}},
                "required": ["deck_id"],
            },
        ),
        Tool(
            name="compute_unused_cards",
            description="Compute which cards in your collection are valid for a given commander's "
            "color identity but not currently in any deck. Filters by color identity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "color_identity": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Commander color identity (e.g., ['W', 'U', 'B', 'R', 'G'])",
                    },
                    "exclude_cards": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Optional list of card names to exclude (cards already in deck)"
                        ),
                    },
                },
                "required": ["color_identity"],
            },
        ),
        Tool(
            name="query_edhrec",
            description="Query EDHREC for commander recommendations and popular cards. "
            "Provides synergy scores and inclusion rates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "commander_name": {
                        "type": "string",
                        "description": "Name of the commander to query",
                    }
                },
                "required": ["commander_name"],
            },
        ),
        Tool(
            name="query_commander_spellbook",
            description="Search Commander Spellbook for combos. Can filter by card name "
            "or color identity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "card_name": {
                        "type": "string",
                        "description": "Optional card name to search for in combos",
                    },
                    "color_identity": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional color identity filter",
                    },
                },
            },
        ),
        Tool(
            name="search_rules_rag",
            description="Search MTG comprehensive rules using BM25s-based RAG engine. "
            "Returns relevant rule sections with relevance scores.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for rules"},
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_collection_stats",
            description="Get statistics about your card collection, including total cards, "
            "color distribution, and more.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


async def ensure_db_connected():
    """Ensure database is connected."""
    if not db.db:
        await db.connect()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "ingest_manabox_csv":
            csv_content = arguments.get("csv_content", "")
            await ensure_db_connected()
            result = await db.ingest_manabox_csv(csv_content)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "fetch_archidekt_deck":
            deck_id = arguments.get("deck_id")
            if not deck_id:
                raise ValueError("deck_id is required")

            deck_data = await archidekt_client.get_deck(deck_id)
            return [TextContent(type="text", text=json.dumps(deck_data, indent=2))]

        elif name == "compute_unused_cards":
            color_identity = arguments.get("color_identity", [])
            exclude_cards = set(arguments.get("exclude_cards", []))

            await ensure_db_connected()

            cards = await db.get_cards_by_color_identity(color_identity)

            # Filter out excluded cards
            unused_cards = [card.model_dump() for card in cards if card.name not in exclude_cards]

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "color_identity": color_identity,
                            "total_unused": len(unused_cards),
                            "cards": unused_cards,
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "query_edhrec":
            commander_name = arguments.get("commander_name")
            if not commander_name:
                raise ValueError("commander_name is required")

            data = await edhrec_client.get_commander_data(commander_name)
            return [TextContent(type="text", text=json.dumps(data, indent=2))]

        elif name == "query_commander_spellbook":
            card_name = arguments.get("card_name")
            color_identity = arguments.get("color_identity")

            data = await spellbook_client.search_combos(card_name, color_identity)
            return [TextContent(type="text", text=json.dumps(data, indent=2))]

        elif name == "search_rules_rag":
            query = arguments.get("query")
            if not query:
                raise ValueError("query is required")

            top_k = arguments.get("top_k", 5)
            results = await rules_rag.search(query, top_k)

            return [
                TextContent(
                    type="text", text=json.dumps({"query": query, "results": results}, indent=2)
                )
            ]

        elif name == "get_collection_stats":
            await ensure_db_connected()

            cards = await db.get_all_cards()
            total_cards = len(cards)
            total_quantity = sum(card.quantity for card in cards)

            # Color distribution
            color_dist = {}
            for card in cards:
                for color in card.color_identity:
                    color_dist[color] = color_dist.get(color, 0) + 1

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "total_unique_cards": total_cards,
                            "total_quantity": total_quantity,
                            "color_distribution": color_dist,
                        },
                        indent=2,
                    ),
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [
            TextContent(type="text", text=json.dumps({"error": str(e), "tool": name}, indent=2))
        ]


async def cleanup():
    """Cleanup resources."""
    await db.close()
    await archidekt_client.close()
    await edhrec_client.close()
    await spellbook_client.close()


async def main():
    """Main entry point for the MCP server."""
    try:
        # Initialize database
        await db.connect()

        # Run server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
