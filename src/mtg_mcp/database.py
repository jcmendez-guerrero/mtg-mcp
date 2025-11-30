"""Database operations for MTG card collection."""

import csv
import io
from typing import Optional

import aiosqlite

from .models import Card


class Database:
    """In-memory SQLite database for card collection."""

    def __init__(self):
        self.db_path = ":memory:"
        self.db: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Initialize database connection and create schema."""
        self.db = await aiosqlite.connect(self.db_path)
        await self._create_schema()

    async def _create_schema(self):
        """Create database schema."""
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS cards (
                oracle_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                mana_cost TEXT,
                cmc REAL,
                type_line TEXT,
                colors TEXT,
                color_identity TEXT,
                set_code TEXT,
                collector_number TEXT,
                rarity TEXT,
                quantity INTEGER DEFAULT 1
            )
        """
        )
        await self.db.commit()

    async def close(self):
        """Close database connection."""
        if self.db:
            await self.db.close()

    async def ingest_manabox_csv(self, csv_content: str) -> dict:
        """
        Ingest ManaBox CSV data into the database.

        Args:
            csv_content: CSV content as string

        Returns:
            Dictionary with ingestion statistics
        """
        if not self.db:
            await self.connect()

        # Parse CSV
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)

        cards_added = 0
        cards_updated = 0
        errors = []

        for row in reader:
            try:
                # Extract card data from ManaBox format
                # ManaBox CSV typically has: Name, Set, Collector Number, Quantity, etc.
                oracle_id = row.get("Scryfall ID", row.get("Oracle ID", ""))
                if not oracle_id:
                    # Generate a unique pseudo oracle_id if not available
                    import hashlib

                    name_part = row.get("Name", "")
                    set_part = row.get("Set", "")
                    num_part = row.get("Collector Number", "")
                    combined = f"{name_part}_{set_part}_{num_part}"
                    oracle_id = hashlib.md5(combined.encode()).hexdigest()

                name = row.get("Name", row.get("Card Name", ""))
                mana_cost = row.get("Mana Cost", row.get("Cost", ""))
                cmc = float(row.get("CMC", row.get("Mana Value", 0)))
                type_line = row.get("Type", row.get("Type Line", ""))
                colors = row.get("Colors", row.get("Color", ""))
                color_identity = row.get("Color Identity", colors)
                set_code = row.get("Set", row.get("Set Code", ""))
                collector_number = row.get("Collector Number", row.get("Number", ""))
                rarity = row.get("Rarity", "")
                quantity = int(row.get("Quantity", 1))

                # Check if card exists
                cursor = await self.db.execute(
                    "SELECT quantity FROM cards WHERE oracle_id = ?", (oracle_id,)
                )
                existing = await cursor.fetchone()

                if existing:
                    # Update quantity
                    new_quantity = existing[0] + quantity
                    await self.db.execute(
                        "UPDATE cards SET quantity = ? WHERE oracle_id = ?",
                        (new_quantity, oracle_id),
                    )
                    cards_updated += 1
                else:
                    # Insert new card
                    await self.db.execute(
                        """
                        INSERT INTO cards
                        (oracle_id, name, mana_cost, cmc, type_line, colors,
                         color_identity, set_code, collector_number, rarity, quantity)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            oracle_id,
                            name,
                            mana_cost,
                            cmc,
                            type_line,
                            colors,
                            color_identity,
                            set_code,
                            collector_number,
                            rarity,
                            quantity,
                        ),
                    )
                    cards_added += 1

            except Exception as e:
                errors.append(f"Error processing row: {str(e)}")

        await self.db.commit()

        return {
            "cards_added": cards_added,
            "cards_updated": cards_updated,
            "total_cards": cards_added + cards_updated,
            "errors": errors,
        }

    async def get_cards_by_color_identity(self, colors: list[str]) -> list[Card]:
        """
        Get cards that match the given color identity.

        Args:
            colors: List of color codes (W, U, B, R, G)

        Returns:
            List of Card objects
        """
        if not self.db:
            await self.connect()

        # Build query to match cards within color identity
        color_set = set(colors)

        cursor = await self.db.execute(
            """
            SELECT oracle_id, name, mana_cost, cmc, type_line, colors,
                   color_identity, set_code, collector_number, rarity, quantity
            FROM cards
        """
        )

        cards = []
        async for row in cursor:
            # row[6] is color_identity field - check against commander colors
            card_color_identity = set(row[6].split(",")) if row[6] else set()
            # Card is valid if its color identity is subset of commander colors
            if card_color_identity.issubset(color_set) or not card_color_identity:
                card = Card(
                    oracle_id=row[0],
                    name=row[1],
                    mana_cost=row[2],
                    cmc=row[3],
                    type_line=row[4],
                    colors=row[5].split(",") if row[5] else [],
                    color_identity=list(card_color_identity),
                    set_code=row[7],
                    collector_number=row[8],
                    rarity=row[9],
                    quantity=row[10],
                )
                cards.append(card)

        return cards

    async def get_all_cards(self) -> list[Card]:
        """Get all cards from the database."""
        if not self.db:
            await self.connect()

        cursor = await self.db.execute(
            """
            SELECT oracle_id, name, mana_cost, cmc, type_line, colors,
                   color_identity, set_code, collector_number, rarity, quantity
            FROM cards
        """
        )

        cards = []
        async for row in cursor:
            card = Card(
                oracle_id=row[0],
                name=row[1],
                mana_cost=row[2],
                cmc=row[3],
                type_line=row[4],
                colors=row[5].split(",") if row[5] else [],
                color_identity=row[6].split(",") if row[6] else [],
                set_code=row[7],
                collector_number=row[8],
                rarity=row[9],
                quantity=row[10],
            )
            cards.append(card)

        return cards

    async def get_card_count(self) -> int:
        """Get total number of unique cards in collection."""
        if not self.db:
            await self.connect()

        cursor = await self.db.execute("SELECT COUNT(*) FROM cards")
        result = await cursor.fetchone()
        return result[0] if result else 0
