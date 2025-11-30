"""API clients for external MTG services."""

from typing import Optional

import httpx


class ArchidektClient:
    """Client for Archidekt API."""

    BASE_URL = "https://archidekt.com/api"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def get_deck(self, deck_id: int) -> dict:
        """
        Fetch deck data from Archidekt.

        Args:
            deck_id: Archidekt deck ID

        Returns:
            Deck data dictionary
        """
        try:
            response = await self.client.get(f"{self.BASE_URL}/decks/{deck_id}/")
            response.raise_for_status()
            data = response.json()

            # Parse deck data
            deck_info = {
                "id": deck_id,
                "name": data.get("name", "Unknown"),
                "format": data.get("format", "commander"),
                "commander": None,
                "cards": [],
            }

            # Extract cards
            cards = data.get("cards", [])
            for card_data in cards:
                card_info = card_data.get("card", {})
                categories = card_data.get("categories", [])

                # Check if it's a commander
                if "Commander" in categories:
                    deck_info["commander"] = card_info.get("oracleCard", {}).get("name", "")

                deck_info["cards"].append(
                    {
                        "name": card_info.get("oracleCard", {}).get("name", ""),
                        "oracle_id": card_info.get("oracleCard", {}).get("oracleId", ""),
                        "quantity": card_data.get("quantity", 1),
                        "categories": categories,
                    }
                )

            return deck_info

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch Archidekt deck: {str(e)}")


class EDHRECClient:
    """Client for EDHREC data."""

    BASE_URL = "https://json.edhrec.com/pages"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def get_commander_data(self, commander_name: str) -> dict:
        """
        Fetch commander recommendations from EDHREC.

        Args:
            commander_name: Name of the commander

        Returns:
            Commander data dictionary
        """
        try:
            # EDHREC uses URL-friendly names
            url_name = commander_name.lower().replace(" ", "-").replace(",", "")
            response = await self.client.get(f"{self.BASE_URL}/commanders/{url_name}.json")
            response.raise_for_status()
            data = response.json()

            # Extract relevant data
            result = {
                "name": data.get("container", {}).get("json_dict", {}).get("name", commander_name),
                "color_identity": data.get("container", {})
                .get("json_dict", {})
                .get("coloridentity", []),
                "cards": [],
            }

            # Extract card recommendations
            cardlists = data.get("container", {}).get("json_dict", {}).get("cardlists", [])
            for cardlist in cardlists:
                for card in cardlist.get("cardviews", []):
                    result["cards"].append(
                        {
                            "name": card.get("name", ""),
                            "synergy": card.get("synergy", 0),
                            "inclusion": card.get("inclusion", 0),
                            "url": card.get("url", ""),
                        }
                    )

            return result

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch EDHREC data: {str(e)}")


class CommanderSpellbookClient:
    """Client for Commander Spellbook API."""

    BASE_URL = "https://commanderspellbook.com/api"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def search_combos(
        self, card_name: Optional[str] = None, color_identity: Optional[list[str]] = None
    ) -> dict:
        """
        Search for combos on Commander Spellbook.

        Args:
            card_name: Optional card name to search for
            color_identity: Optional color identity filter

        Returns:
            Combo search results
        """
        try:
            params = {}
            if card_name:
                params["card"] = card_name
            if color_identity:
                params["colorIdentity"] = ",".join(color_identity)

            response = await self.client.get(f"{self.BASE_URL}/combos", params=params)
            response.raise_for_status()
            data = response.json()

            combos = []
            for combo in data:
                combos.append(
                    {
                        "id": combo.get("id", ""),
                        "cards": [c.get("name", "") for c in combo.get("cards", [])],
                        "color_identity": combo.get("colorIdentity", ""),
                        "prerequisites": combo.get("prerequisites", ""),
                        "steps": combo.get("steps", ""),
                        "result": combo.get("result", ""),
                    }
                )

            return {"total": len(combos), "combos": combos}

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch Commander Spellbook data: {str(e)}")
