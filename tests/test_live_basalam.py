import pytest

pytestmark = [pytest.mark.anyio, pytest.mark.live]

PRODUCT = 1410736  # long-lived honey listing with thousands of reviews
SHOP = "asaltabieshiraz"


async def call(client, name, args):
    result = await client.call_tool(name, args)
    assert not result.is_error, result.content[0].text
    return result.structured_content


async def test_search(client):
    data = await call(client, "bs_search", {"query": "عسل", "limit": 5, "free_shipping": True})
    assert data["total"] > 0 and data["products"]
    assert all(p["free_shipping"] for p in data["products"])


async def test_search_price_range(client):
    data = await call(client, "bs_search", {"query": "عسل", "min_price": 500000, "max_price": 1000000, "limit": 10})
    assert data["products"] and all(500_000 <= p["price"] <= 1_000_000 for p in data["products"])


async def test_find_cheapest(client):
    data = await call(client, "bs_find_cheapest", {"query": "عسل", "limit": 5})
    prices = [o["price"] for o in data["offers"]]
    assert prices and prices == sorted(prices) and prices[0] >= 5000


async def test_product(client):
    data = await call(client, "bs_product", {"product_id": PRODUCT})
    assert data["id"] == PRODUCT and data["price"] > 0 and data["shop"]["id"]
    assert data["sales_count"] > 0 and data["free_shipping_over"] > 0


async def test_vendor(client):
    data = await call(client, "bs_vendor", {"vendor": SHOP})
    assert data["identifier"] == SHOP and data["products"] > 0


async def test_vendor_products(client):
    data = await call(client, "bs_vendor_products", {"vendor": SHOP, "limit": 5})
    assert data["products"] and all(p["shop_id"] == SHOP for p in data["products"])


async def test_vendor_products_unknown_shop(client):
    result = await client.call_tool("bs_vendor_products", {"vendor": "nonexistentshop123xyz"})
    assert result.is_error and "No Basalam shop" in result.content[0].text


async def test_search_page_is_full(client):
    data = await call(client, "bs_search", {"query": "عسل", "sort": "cheapest", "page": 2, "limit": 20})
    assert len(data["products"]) == 20


async def test_categories(client):
    top = await call(client, "bs_categories", {})
    assert any(c["id"] == 1 for c in top["categories"])
    found = await call(client, "bs_categories", {"query": "عسل"})
    assert any(c["id"] == 172 for c in found["categories"])


async def test_reviews(client):
    data = await call(client, "bs_reviews", {"product_id": PRODUCT, "limit": 5})
    assert data["product"]["count"] > 0 and len(data["reviews"]) == 5
