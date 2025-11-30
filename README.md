# MTG MCP Server

A Python MCP (Model Context Protocol) server for Magic: The Gathering Commander collection management. This server provides async tools for managing your MTG card collection, fetching deck data, computing unused cards, and searching rules.

## Features

- **ManaBox CSV Ingestion**: Import your card collection from ManaBox CSV exports into an in-memory SQLite database, normalized by Scryfall Oracle ID
- **Archidekt Integration**: Fetch deck data from Archidekt by deck ID
- **Commander Color Identity**: Compute which cards in your collection are valid for a commander's color identity
- **EDHREC Integration**: Query EDHREC for commander recommendations and popular cards
- **Commander Spellbook**: Search for combos by card name or color identity
- **Rules RAG Engine**: BM25s-based rules search engine for MTG comprehensive rules

## Installation

### Using pip

```bash
pip install -e .
```

### Using Docker

```bash
docker build -t mtg-mcp .
docker run -i mtg-mcp
```

## Usage

### Running the Server

The server uses stdio transport for MCP communication:

```bash
python -m mtg_mcp.server
```

Or using the installed script:

```bash
mtg-mcp
```

### Available Tools

#### 1. ingest_manabox_csv

Ingest ManaBox CSV export into the card collection database.

```json
{
  "csv_content": "Name,Set,Collector Number,Quantity,Colors,Color Identity\nLightning Bolt,LEA,161,4,R,R"
}
```

#### 2. fetch_archidekt_deck

Fetch a deck from Archidekt by deck ID.

```json
{
  "deck_id": 123456
}
```

#### 3. compute_unused_cards

Compute which cards in your collection are valid for a commander's color identity.

```json
{
  "color_identity": ["W", "U", "B", "G"],
  "exclude_cards": ["Sol Ring", "Command Tower"]
}
```

#### 4. query_edhrec

Query EDHREC for commander recommendations.

```json
{
  "commander_name": "Atraxa, Praetors' Voice"
}
```

#### 5. query_commander_spellbook

Search Commander Spellbook for combos.

```json
{
  "card_name": "Thassa's Oracle",
  "color_identity": ["U"]
}
```

#### 6. search_rules_rag

Search MTG comprehensive rules using BM25s-based RAG engine.

```json
{
  "query": "protection from",
  "top_k": 5
}
```

#### 7. get_collection_stats

Get statistics about your card collection.

```json
{}
```

## MCP Configuration

To use this server with Claude Desktop or other MCP clients, add to your MCP configuration:

```json
{
  "mcpServers": {
    "mtg-mcp": {
      "command": "python",
      "args": ["-m", "mtg_mcp.server"]
    }
  }
}
```

Or with Docker:

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

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## Architecture

- **Database**: In-memory SQLite database with normalized card storage by Scryfall Oracle ID
- **Models**: Pydantic models for type safety and validation
- **API Clients**: Async HTTP clients for Archidekt, EDHREC, and Commander Spellbook
- **Rules RAG**: BM25s-based search engine for MTG comprehensive rules
- **MCP Server**: Stdio transport-based MCP server with async tool handlers

## Requirements

- Python 3.11+
- Dependencies managed via pyproject.toml

## License

MIT License - See LICENSE file for details
