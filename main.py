"""
Property Search MCP Server (using Melo API) - Real Estate Search API
"""

import json
import logging
from typing import Literal, Optional

import httpx
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from pydantic import Field

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("melo-mcp")

# API Configuration
MELO_API_BASE_URL = "https://api.notif.immo"

# No authentication on the MCP server - relies on pass-through
mcp = FastMCP("Real Estate Search", stateless_http=True)

logger.info("🔓 MCP Server initialized (pass-through authentication)")


async def _search_melo_properties(
    api_key: str,
    property_type: Optional[int] = None,
    transaction_type: Optional[int] = None,
    budget_min: Optional[int] = None,
    budget_max: Optional[int] = None,
    surface_min: Optional[int] = None,
    surface_max: Optional[int] = None,
    price_per_meter_min: Optional[int] = None,
    price_per_meter_max: Optional[int] = None,
    bedroom_min: Optional[int] = None,
    included_zipcodes: Optional[list[str]] = None,
    order_by: Optional[str] = None,
    items_per_page: int = 10,
    page: int = 1,
) -> dict:
    """
    Internal function to call the Melo API using the provided API key.

    Args:
        property_type: Property type (0=Apartment, 1=House, 2=Building, 3=Parking, 4=Office, 5=Land, 6=Shop)
        transaction_type: Transaction type (0=Sell, 1=Rent)
        budget_min: Minimum budget for the property
        budget_max: Maximum budget for the property
        surface_min: Minimum surface area in square meters
        surface_max: Maximum surface area in square meters
        price_per_meter_min: Minimum price per square meter
        price_per_meter_max: Maximum price per square meter
        bedroom_min: Minimum number of bedrooms
        included_zipcodes: List of zip codes to search in
        order_by: Ordering criteria (pricePerMeter, price, updatedAt)
        items_per_page: Number of results per page (max 30)
        page: Page number for pagination

    Returns:
        API response as a dictionary
    """
    url = f"{MELO_API_BASE_URL}/documents/properties"

    # Build query parameters, filtering out None values
    # Using list of tuples to support multiple values for same key (zip codes)
    params = []

    if property_type is not None:
        params.append(("propertyTypes[]", str(property_type)))
    if transaction_type is not None:
        params.append(("transactionType", str(transaction_type)))
    if budget_min is not None:
        params.append(("budgetMin", str(budget_min)))
    if budget_max is not None:
        params.append(("budgetMax", str(budget_max)))
    if surface_min is not None:
        params.append(("surfaceMin", str(surface_min)))
    if surface_max is not None:
        params.append(("surfaceMax", str(surface_max)))
    if price_per_meter_min is not None:
        params.append(("pricePerMeterMin", str(price_per_meter_min)))
    if price_per_meter_max is not None:
        params.append(("pricePerMeterMax", str(price_per_meter_max)))
    if bedroom_min is not None:
        params.append(("bedroomMin", str(bedroom_min)))

    if included_zipcodes:
        for zipcode in included_zipcodes:
            params.append(("includedZipcodes[]", zipcode))

    # Handle ordering
    if order_by:
        if order_by == "pricePerMeter":
            params.append(("order[pricePerMeter]", "asc"))
        elif order_by == "price":
            params.append(("order[price]", "asc"))
        elif order_by == "updatedAt":
            params.append(("order[updatedAt]", "desc"))

    params.append(("itemsPerPage", str(items_per_page)))
    params.append(("page", str(page)))
    params.append(("withCoherentPrice", "true"))

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    }

    # Log request details
    logger.info("=" * 80)
    logger.info("🔍 Melo API Request")
    logger.info(f"URL: {url}")
    logger.info("Parameters:")
    for key, value in params:
        logger.info(f"  {key}: {value}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            response_data = response.json()

            # Log response details
            logger.info("-" * 80)
            logger.info("✅ Melo API Response")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Total Items: {response_data.get('hydra:totalItems', 'N/A')}")
            logger.info(
                f"Properties Returned: {len(response_data.get('hydra:member', []))}"
            )
            logger.info(
                f"Response Preview: {json.dumps(response_data, indent=2)[:500]}..."
            )
            logger.info("=" * 80)

            return response_data
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [401, 403]:
                logger.error("❌ Invalid Melo API key")
                raise ValueError("Invalid Melo API key. Please check your credentials.")
            raise


@mcp.tool(
    title="Search Properties",
    description="Search for real estate properties using the Melo API with comprehensive filtering options",
)
async def search_properties(
    property_type: Literal["apartment", "house"] = Field(
        default="apartment",
        description="Type of property: 'apartment' or 'house'",
    ),
    transaction_type: Literal["sell", "rent"] = Field(
        default="sell",
        description="Transaction type: 'sell' for purchase or 'rent' for rental",
    ),
    budget_min: Optional[int] = Field(
        default=None,
        description="Minimum budget/price in euros",
    ),
    budget_max: Optional[int] = Field(
        default=None,
        description="Maximum budget/price in euros",
    ),
    surface_min: Optional[int] = Field(
        default=None,
        description="Minimum surface area in square meters",
    ),
    surface_max: Optional[int] = Field(
        default=None,
        description="Maximum surface area in square meters",
    ),
    price_per_meter_min: Optional[int] = Field(
        default=None,
        description="Minimum price per square meter in euros",
    ),
    price_per_meter_max: Optional[int] = Field(
        default=None,
        description="Maximum price per square meter in euros",
    ),
    bedroom_min: Optional[int] = Field(
        default=None,
        description="Minimum number of bedrooms",
    ),
    zip_codes: Optional[list[str]] = Field(
        default=None,
        description="List of zip codes to search in (e.g., ['75011', '23158'])",
    ),
    order_by: Optional[Literal["pricePerMeter", "price", "updatedAt"]] = Field(
        default=None,
        description="Sort results by: 'pricePerMeter', 'price', or 'updatedAt'",
    ),
    items_per_page: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of results per page (1-10)",
    ),
    page: int = Field(
        default=1,
        ge=1,
        description="Page number for pagination",
    ),
) -> dict:
    """
    Search for real estate properties in France using the Melo API. Requires X-API-KEY header with a valid Melo API key.

    Returns a collection of properties matching the specified criteria, including
    detailed information about each property such as location, price, surface area,
    features, and available pictures.

    Example usage:
    - Search for apartments to buy in Paris with 2+ bedrooms:
      property_type="apartment", transaction_type="sell", bedroom_min=2, zip_codes=["75001", "75002"]
    - Find houses for rent under 2000€:
      property_type="house", transaction_type="rent", budget_max=2000
    """

    # Extract API key from request headers using get_http_headers()
    headers = get_http_headers()
    api_key = headers.get("x-api-key")

    if not api_key:
        logger.error("❌ Missing X-API-KEY header")
        raise ValueError("Missing X-API-KEY header. Please provide your Melo API key.")

    logger.info("🔑 Using API key from request headers")

    # Map user-friendly values to API values
    property_type_map = {"apartment": 0, "house": 1}
    transaction_type_map = {"sell": 0, "rent": 1}

    return await _search_melo_properties(
        api_key=api_key,
        property_type=property_type_map[property_type],
        transaction_type=transaction_type_map[transaction_type],
        budget_min=budget_min,
        budget_max=budget_max,
        surface_min=surface_min,
        surface_max=surface_max,
        price_per_meter_min=price_per_meter_min,
        price_per_meter_max=price_per_meter_max,
        bedroom_min=bedroom_min,
        included_zipcodes=zip_codes,
        order_by=order_by,
        items_per_page=items_per_page,
        page=page,
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
