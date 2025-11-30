# MTG MCP Server Usage Examples

This document provides examples of how to use the MTG MCP server tools.

## Prerequisites

Ensure the server is installed:

```bash
pip install -e .
```

## Running the Server

The server uses stdio transport for MCP communication:

```bash
python -m mtg_mcp.server
```

Or using the installed command:

```bash
mtg-mcp
```

## Tool Examples

### 1. Ingest ManaBox CSV

Import your card collection from ManaBox:

```json
{
  "tool": "ingest_manabox_csv",
  "arguments": {
    "csv_content": "Name,Set,Collector Number,Quantity,Scryfall ID,Colors,Color Identity\nLightning Bolt,LEA,161,4,test-id-1,R,R\nSol Ring,LEA,265,1,test-id-2,,"
  }
}
```

Response:
```json
{
  "cards_added": 2,
  "cards_updated": 0,
  "total_cards": 2,
  "errors": []
}
```

### 2. Fetch Archidekt Deck

Get deck information from Archidekt:

```json
{
  "tool": "fetch_archidekt_deck",
  "arguments": {
    "deck_id": 123456
  }
}
```

Response:
```json
{
  "id": 123456,
  "name": "My Commander Deck",
  "format": "commander",
  "commander": "Atraxa, Praetors' Voice",
  "cards": [...]
}
```

### 3. Compute Unused Cards

Find cards in your collection that fit a commander's color identity:

```json
{
  "tool": "compute_unused_cards",
  "arguments": {
    "color_identity": ["W", "U", "B", "G"],
    "exclude_cards": ["Sol Ring", "Command Tower"]
  }
}
```

Response:
```json
{
  "color_identity": ["W", "U", "B", "G"],
  "total_unused": 15,
  "cards": [
    {
      "oracle_id": "...",
      "name": "Path to Exile",
      "colors": ["W"],
      ...
    }
  ]
}
```

### 4. Query EDHREC

Get commander recommendations from EDHREC:

```json
{
  "tool": "query_edhrec",
  "arguments": {
    "commander_name": "Atraxa, Praetors' Voice"
  }
}
```

Response:
```json
{
  "name": "Atraxa, Praetors' Voice",
  "color_identity": ["W", "U", "B", "G"],
  "cards": [
    {
      "name": "Doubling Season",
      "synergy": 0.95,
      "inclusion": 0.85
    }
  ]
}
```

### 5. Query Commander Spellbook

Search for combos:

```json
{
  "tool": "query_commander_spellbook",
  "arguments": {
    "card_name": "Thassa's Oracle",
    "color_identity": ["U"]
  }
}
```

Response:
```json
{
  "total": 5,
  "combos": [
    {
      "id": "...",
      "cards": ["Thassa's Oracle", "Demonic Consultation"],
      "color_identity": "U,B",
      "result": "Win the game"
    }
  ]
}
```

### 6. Search Rules (RAG)

Search MTG comprehensive rules:

```json
{
  "tool": "search_rules_rag",
  "arguments": {
    "query": "protection from",
    "top_k": 5
  }
}
```

Response:
```json
{
  "query": "protection from",
  "results": [
    {
      "rule_number": "702.15a",
      "rule_text": "Protection is a static ability...",
      "score": 0.95
    }
  ]
}
```

### 7. Get Collection Stats

Get statistics about your collection:

```json
{
  "tool": "get_collection_stats",
  "arguments": {}
}
```

Response:
```json
{
  "total_unique_cards": 150,
  "total_quantity": 300,
  "color_distribution": {
    "W": 30,
    "U": 35,
    "B": 28,
    "R": 32,
    "G": 25
  }
}
```

## Integration with Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "mtg-mcp": {
      "command": "python",
      "args": ["-m", "mtg_mcp.server"],
      "cwd": "/path/to/mtg-mcp"
    }
  }
}
```

## Docker Usage

Build and run with Docker:

```bash
docker build -t mtg-mcp .
docker run -i mtg-mcp
```

Or use with Claude Desktop:

```json
{
  "mcpServers": {
    "mtg-mcp": {
      "command": "docker",
      "args": ["run", "-i", "mtg-mcp"]
    }
  }
}
```
