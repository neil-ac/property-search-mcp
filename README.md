# property-search-mcp

A FastMCP-based MCP server for searching real estate properties in France using the Melo (notif.immo) API.

## Overview
This MCP server provides a comprehensive tool for searching real estate properties through the Melo API. It allows AI assistants and other MCP clients to search for apartments and houses for sale or rent with extensive filtering options including price, surface area, location, and more.

## Prerequisites
- Install uv (https://docs.astral.sh/uv/getting-started/installation/)

## Installation

1. Clone the repository and navigate to the directory:

```bash
cd property-search-mcp
```

2. Install python version & dependencies:

```bash
uv python install
uv sync
```

3. Environment Variables: Create a `.env` file in the project root. Then add:

```bash
MELO_API_KEY="your_api_key_here"
```

You can obtain a Melo API key from [notif.immo](https://www.notif.immo/).

## Usage

Start the server on port 8000:

```bash
uv run main.py
```

The server will be available at `http://127.0.0.1:8000/mcp` using Streamable HTTP transport.

## Features

### `search_properties` Tool

The server provides a comprehensive property search tool with the following parameters:

- **property_type**: Choose between "apartment" or "house"
- **transaction_type**: Choose "sell" (purchase) or "rent" (rental)
- **budget_min/budget_max**: Filter by price range in euros
- **surface_min/surface_max**: Filter by surface area in square meters
- **price_per_meter_min/price_per_meter_max**: Filter by price per square meter
- **bedroom_min**: Minimum number of bedrooms
- **zip_codes**: List of French zip codes to search in (e.g., ["75011", "23158"])
- **order_by**: Sort results by "pricePerMeter", "price", or "updatedAt"
- **items_per_page**: Number of results per page (1-10, default: 5)
- **page**: Page number for pagination

### Example Queries

Through an AI assistant connected to this MCP server, you can ask:

- "Find apartments for sale in Paris 11th arrondissement with at least 2 bedrooms under 500,000€"
- "Show me houses for rent in Paris with a minimum of 80m² surface area"
- "Search for properties in the 75018 zip code sorted by price per meter"

## Development

### API Response Format

The Melo API returns property data in the following structure:

```json
{
  "hydra:member": [
    {
      "@id": "/documents/properties/...",
      "uuid": "...",
      "propertyType": 0,
      "transactionType": 1,
      "bedroom": 2,
      "room": 3,
      "surface": 30,
      "price": 950,
      "pricePerMeter": 31.66,
      "city": {
        "name": "Paris 18e",
        "zipcode": "75018",
        "department": {...}
      },
      "locations": {
        "lat": 48.8530933,
        "lon": 2.2487626
      },
      "pictures": [...],
      "adverts": [...],
      ...
    }
  ],
  "hydra:totalItems": 0,
  "hydra:view": {
    "hydra:next": "..."
  }
}
```

### Extending the Server

To add more filters or tools, you can extend the `_search_melo_properties` function or create new tools following the same pattern. The Melo API supports many more parameters than currently exposed - refer to the API documentation for the full list.

### Environment Variables

- `MELO_API_KEY`: Your Melo API key (required)

## License

This project is licensed under the MIT License.
