"""Pydantic models for MTG data structures."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Card(BaseModel):
    """Card model normalized by Scryfall Oracle ID."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "oracle_id": "12345678-1234-1234-1234-123456789012",
                "name": "Lightning Bolt",
                "mana_cost": "{R}",
                "cmc": 1.0,
                "type_line": "Instant",
                "colors": ["R"],
                "color_identity": ["R"],
                "set_code": "LEA",
                "collector_number": "161",
                "rarity": "common",
                "quantity": 4,
            }
        }
    )

    oracle_id: str = Field(..., description="Scryfall Oracle ID")
    name: str = Field(..., description="Card name")
    mana_cost: Optional[str] = Field(None, description="Mana cost")
    cmc: float = Field(0.0, description="Converted mana cost")
    type_line: str = Field("", description="Type line")
    colors: list[str] = Field(default_factory=list, description="Card colors")
    color_identity: list[str] = Field(default_factory=list, description="Color identity")
    set_code: str = Field("", description="Set code")
    collector_number: str = Field("", description="Collector number")
    rarity: str = Field("", description="Rarity")
    quantity: int = Field(1, description="Quantity owned")


class Deck(BaseModel):
    """Archidekt deck model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 123456,
                "name": "My Commander Deck",
                "format": "commander",
                "commander": "Atraxa, Praetors' Voice",
                "cards": [],
            }
        }
    )

    id: int = Field(..., description="Deck ID")
    name: str = Field(..., description="Deck name")
    format: str = Field("commander", description="Deck format")
    commander: Optional[str] = Field(None, description="Commander card name")
    cards: list[dict] = Field(default_factory=list, description="List of cards in deck")


class CommanderIdentity(BaseModel):
    """Commander color identity."""

    model_config = ConfigDict(json_schema_extra={"example": {"colors": ["W", "U", "B", "G"]}})

    colors: list[str] = Field(..., description="Color identity (W, U, B, R, G)")


class RulesSearchResult(BaseModel):
    """Rules search result from RAG engine."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_number": "702.15a",
                "rule_text": "Protection is a static ability...",
                "score": 0.95,
            }
        }
    )

    rule_number: str = Field(..., description="Rule number")
    rule_text: str = Field(..., description="Rule text")
    score: float = Field(..., description="Relevance score")
