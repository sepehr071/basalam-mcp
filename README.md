<!-- mcp-name: io.github.sepehr071/basalam-mcp -->

# basalam-mcp: Basalam marketplace MCP server for AI agents

**Let your AI agent shop on Basalam (باسلام).** An unofficial, read-only MCP server for Iran's marketplace of
independent shops: search products with price, category, shipping and discount filters, find the cheapest in-stock
offers, read product details, shops, categories and customer reviews, all from Claude, Cursor or Copilot.

## For AI agents

- **What:** unofficial MCP server for Basalam (basalam.com). Queries in Persian match best; prices in Toman.
- **Install:** `uvx basalam-mcp` or `claude mcp add basalam -- uvx basalam-mcp`. Transport: stdio. Needs [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python 3.10+).
- **Auth:** none, no API key or account. Basalam answers from non-Iranian IPs too.
- **Optional env:** `BASALAM_MCP_PROXY`, an HTTP proxy URL (or a comma-separated list). System proxy settings are ignored on purpose.
- **Read-only:** no login, basket, order, chat or review posting.

## Quick start

```bash
claude mcp add basalam -- uvx basalam-mcp
```

Or in any MCP client config: `{"command": "uvx", "args": ["basalam-mcp"]}`.

## Tools

| Tool | What it does |
|---|---|
| `bs_search` | Search products; filters: price range (Toman), category, free shipping, discount, top shops, installments; sort by relevance, sales, price, newest. |
| `bs_find_cheapest` | Cheapest in-stock offers for a query, cheapest first, with a price floor and optional minimum rating. |
| `bs_product` | One product: price, discount, stock, sales count, free-shipping threshold, options (sizes, colors), attributes, rating, shop. |
| `bs_vendor` | A shop's profile: city, activity, product count, shipping methods. |
| `bs_vendor_products` | One shop's products, searchable, filterable and sortable; an unknown shop is an error. |
| `bs_categories` | The category tree: top level, children of an id, or search by name (inside `parent_id` when both are given). Ids feed `category_id`. |
| `bs_reviews` | Customer reviews with the star histogram of the product and its shop. |

## Notes

- Prices are Toman. The upstream API reports Rial; the server divides by 10.
- Result totals stop at 10000 (the search index cap). Pages hold at most 30 products (keeps each reply under 15 KB; a product's link is `https://basalam.com/p/<id>`), and a short page is refilled from the following rows, so neighbouring pages can repeat a few products.
- The cheapest sort is full of filler listings priced at a few hundred Toman; `bs_find_cheapest` hides prices under 5000 Toman by default.
- Dates and times are passed through as Basalam returns them (Iran local time, not converted; unconfirmed). The vendor API's own `score` field is always 0, so it is not exposed; use the shop stars from `bs_reviews`.
- Review and description text is user-generated and cut to 400 characters unless `full_text=true`.

## Development

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv run python -m pytest -q          # offline unit tests
uv run python -m pytest -m live -q  # one live test per tool
uv build
```

Unofficial: not affiliated with Basalam. MIT License.
