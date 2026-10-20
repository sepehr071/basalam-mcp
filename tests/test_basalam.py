import httpx
import pytest
from conftest import fixture

from basalam_mcp import http
from basalam_mcp.registry import clip
from basalam_mcp.server import mcp

pytestmark = pytest.mark.anyio

SEARCH = "/web/v1/search/product/search"


async def test_search_converts_rial_and_sends_filters(client, api):
    api[SEARCH] = fixture("search.json")
    result = await client.call_tool(
        "bs_search",
        {"query": "عسل", "sort": "cheapest", "min_price": 5000, "max_price": 60000, "free_shipping": True, "limit": 3},
    )
    data = result.structured_content
    assert data["total"] == 10000
    assert [p["price"] for p in data["products"]] == [12000, 12000, 30000]
    first = data["products"][0]
    assert first["id"] == 39072910 and first["shop_id"] == "shahde_gole_biaban_honey"
    assert "url" not in first and "discount_pct" not in first
    q = api.calls[0].url.params
    assert q["q"] == "عسل" and q["sort"] == "price" and q["size"] == "3" and q["from"] == "0"
    assert q["filters.minPrice"] == "50000" and q["filters.maxPrice"] == "600000"  # Toman in, Rial out
    assert q["filters.freeShipping"] == "true" and "filters.hasDiscount" not in q


async def test_search_page_offset(client, api):
    api[SEARCH] = fixture("search.json")
    await client.call_tool("bs_search", {"query": "عسل", "page": 3, "limit": 12, "category_id": 172})
    q = api.calls[0].url.params
    assert q["from"] == "24" and q["filters.categories"] == "172" and "filters.minPrice" not in q


async def test_find_cheapest_skips_out_of_stock(client, api):
    body = fixture("search.json")
    body["meta"]["count"] = 3  # the whole result set, so no refill request
    api[SEARCH] = body
    result = await client.call_tool("bs_find_cheapest", {"query": "عسل", "limit": 5})
    offers = result.structured_content["offers"]
    assert [o["id"] for o in offers] == [39072910, 38264432]  # 32529152 is out of stock
    assert len(api.calls) == 1  # fewer than 48 hits: no second page
    q = api.calls[0].url.params
    assert q["sort"] == "price" and q["filters.minPrice"] == "50000"  # 5000 Toman floor


async def test_find_cheapest_rating_floor(client, api):
    body = fixture("search.json")
    body["meta"]["count"] = 3
    api[SEARCH] = body
    result = await client.call_tool("bs_find_cheapest", {"query": "عسل", "rating_min": 4.8})
    assert [o["id"] for o in result.structured_content["offers"]] == [39072910]


async def test_find_cheapest_rating_floor_drops_unrated(client, api):
    body = fixture("search.json")
    body["meta"]["count"] = 3
    body["products"][1]["rating"] = {"average": 0, "count": 0}  # one unrated, in stock
    api[SEARCH] = body
    for floor, ids in ((0, [39072910, 38264432]), (0.1, [39072910])):  # unrated pass only at 0
        result = await client.call_tool("bs_find_cheapest", {"query": "عسل", "rating_min": floor})
        assert [o["id"] for o in result.structured_content["offers"]] == ids


async def test_product(client, api):
    api["/api_v2/product/56850315"] = fixture("product.json")
    result = await client.call_tool("bs_product", {"product_id": 56850315})
    p = result.structured_content
    assert (
        p["id"] == 56850315
        and p["price"] == 1350000
        and p["original_price"] == 1500000
        and p["discount_pct"] == 10
        and p["stock"] == 25
    )
    assert p["shop"]["id"] == "asalhowraman98" and p["shop"]["city"]
    assert p["url"] == "https://basalam.com/p/56850315"


async def test_product_discount_pct_without_discount_object(client, api):
    body = fixture("product.json")
    body["discount"] = None  # real API often omits it while primary_price > price
    api["/api_v2/product/56850315"] = body
    p = (await client.call_tool("bs_product", {"product_id": 56850315})).structured_content
    assert p["discount_pct"] == 10 and p["sales_count"] is None


async def test_product_sales_and_free_shipping(client, api):
    api["/api_v2/product/56850315"] = fixture("product.json")  # price 1,350,000 Toman
    api["/web/v1/order-processing/orders-calculate-stats"] = {"result": 9604}
    zones = {"free_shipping_rate": {"is_available": True, "min_price": 5600000}}
    api["/web/v1/shipping/product-zones/56850315"] = zones
    p = (await client.call_tool("bs_product", {"product_id": 56850315})).structured_content
    assert p["sales_count"] == 9604 and p["free_shipping_over"] == 560000 and "free_shipping" in p
    assert p["free_shipping"] is True
    q = api.calls[1].url.params
    assert q["product_id"] == "56850315" and q["resource_count"] == "number-of-sales-per-product"
    http._cache.clear()
    zones["free_shipping_rate"]["min_price"] = 90000000  # 9,000,000 Toman: this product alone does not reach it
    p = (await client.call_tool("bs_product", {"product_id": 56850315})).structured_content
    assert p["free_shipping"] is False


async def test_product_always_free_shipping(client, api):
    api["/api_v2/product/56850315"] = fixture("product.json")
    api["/web/v1/shipping/product-zones/56850315"] = {
        "free_shipping_rate": {"is_available": False},
        "rate": {"type": "free"},
    }
    p = (await client.call_tool("bs_product", {"product_id": 56850315})).structured_content
    assert p["free_shipping"] is True and p["free_shipping_over"] is None


async def test_product_without_extra_calls(client, api):
    api["/api_v2/product/56850315"] = fixture("product.json")  # stats and zones answer 404
    p = (await client.call_tool("bs_product", {"product_id": 56850315})).structured_content
    assert [p["sales_count"], p["free_shipping"], p["free_shipping_over"]] == [None, None, None]


async def test_product_not_found(client, api):
    result = await client.call_tool("bs_product", {"product_id": 1})
    assert result.is_error and "404" in result.content[0].text


async def test_vendor(client, api):
    api["/api_v2/vendor/identifier/asalhowraman98"] = fixture("vendor.json")
    result = await client.call_tool("bs_vendor", {"vendor": "asalhowraman98"})
    v = result.structured_content
    assert v["name"] == "سوغات دیاری" and v["products"] == 50 and v["id"] == 1484831


async def test_vendor_products_filters_by_shop(client, api):
    api[SEARCH] = fixture("search.json")
    result = await client.call_tool("bs_vendor_products", {"vendor": "asalhowraman98", "query": "عسل"})
    assert len(result.structured_content["products"]) == 3
    q = api.calls[0].url.params
    assert q["filters.vendorIdentifier"] == "asalhowraman98" and q["sort"] == "newest"


async def test_vendor_products_unknown_shop_errors(client, api):
    api[SEARCH] = {"products": [], "meta": {"count": 0}}
    api["/api_v2/vendor/identifier/nosuchshop"] = lambda r: httpx.Response(422, json={"messages": [{"message": "x"}]})
    result = await client.call_tool("bs_vendor_products", {"vendor": "nosuchshop"})
    assert result.is_error and "No Basalam shop 'nosuchshop'" in result.content[0].text
    api["/api_v2/vendor/identifier/emptyshop"] = fixture("vendor.json")  # real shop, nothing matches the filters
    data = (await client.call_tool("bs_vendor_products", {"vendor": "emptyshop", "query": "zzz"})).structured_content
    assert data["total"] == 0 and data["products"] == []


async def test_reviews(client, api):
    api["/web/v1/review/product/1410736/reviews"] = fixture("reviews.json")
    result = await client.call_tool("bs_reviews", {"product_id": 1410736, "limit": 5})
    r = result.structured_content
    assert r["product"]["count"] == 7882 and r["product"]["by_star"]["5"] == 5527
    assert r["has_more"] is True and r["reviews"][0]["stars"] == 4 and r["reviews"][0]["date"] == "2026-10-19"
    assert api.calls[0].url.params["limit"] == "5"


async def test_reviews_variant_text(client, api):
    body = fixture("reviews.json")
    body["reviews"][0]["variation_metadata"] = [
        {"id": 1, "properties": [{"property": {"title": "سایز"}, "value": {"title": "37"}}]}
    ]
    api["/web/v1/review/product/1410736/reviews"] = body
    r = (await client.call_tool("bs_reviews", {"product_id": 1410736})).structured_content["reviews"]
    assert r[0]["variant"] == ["سایز: 37"] and "variant" not in r[1]


async def test_reviews_limit_range(client, api):
    for limit in (0, 21, 50):
        result = await client.call_tool("bs_reviews", {"product_id": 1, "limit": limit})
        assert result.is_error and not api.calls
    api["/web/v1/review/product/1/reviews"] = fixture("reviews.json")
    await client.call_tool("bs_reviews", {"product_id": 1, "limit": 7})
    assert api.calls[0].url.params["limit"] == "7"


async def test_blank_query_rejected(client, api):
    result = await client.call_tool("bs_search", {"query": "   "})
    assert result.is_error and not api.calls


async def test_error_text_reads_messages_list():
    body = {"http_status": 422, "messages": [{"message": "no such shop", "code": 0}]}
    assert http._error_text(body) == "no such shop"


async def test_categories_levels_and_search(client, api):
    api["/api_v2/category"] = fixture("categories.json")
    top = (await client.call_tool("bs_categories", {})).structured_content["categories"]
    assert [c["id"] for c in top] == [1, 10]
    kids = (await client.call_tool("bs_categories", {"parent_id": 1})).structured_content
    assert any(c["id"] == 20 for c in kids["categories"])
    hit = (await client.call_tool("bs_categories", {"query": "عسل"})).structured_content["categories"]
    assert hit and hit[0]["id"] == 20 and "مواد غذایی" in hit[0]["path"]
    arabic = (await client.call_tool("bs_categories", {"query": "غذاي"})).structured_content["categories"]
    assert [c["id"] for c in arabic] == [1]  # Arabic yeh still finds the Persian title
    missing = (await client.call_tool("bs_categories", {"parent_id": 999999})).structured_content
    assert missing["categories"] == [] and "note" in missing
    inside = (await client.call_tool("bs_categories", {"parent_id": 1, "query": "عسل"})).structured_content
    assert [c["id"] for c in inside["categories"]][0] == 20 and "مواد غذایی" in inside["categories"][0]["path"]
    outside = (await client.call_tool("bs_categories", {"parent_id": 10, "query": "عسل"})).structured_content
    assert outside["categories"] == []
    gone = (await client.call_tool("bs_categories", {"parent_id": 999999, "query": "عسل"})).structured_content
    assert gone["categories"] == [] and "note" in gone


async def test_search_refills_short_page(client, api):
    rows = fixture("search.json")["products"]
    pages = {"0": rows[:1] + rows[:1], "3": rows[1:2], "5": rows[2:]}  # first page has a duplicate row

    def handler(request):
        q = request.url.params
        return httpx.Response(200, json={"products": pages[q["from"]], "meta": {"count": 50}})

    api[SEARCH] = handler
    data = (await client.call_tool("bs_search", {"query": "عسل", "limit": 3})).structured_content
    assert [p["id"] for p in data["products"]] == [39072910, 38264432, 32529152]
    assert [(c.url.params["from"], c.url.params["size"]) for c in api.calls] == [("0", "3"), ("3", "2"), ("5", "1")]


async def test_search_limit_cap(client, api):
    result = await client.call_tool("bs_search", {"query": "عسل", "limit": 31})
    assert result.is_error and not api.calls


async def test_search_none_params_not_sent(client, api):
    api[SEARCH] = fixture("search.json")
    await client.call_tool("bs_search", {"query": "عسل"})
    assert not any(v == "" for v in api.calls[0].url.params.values())


async def test_http_retry_and_cache(api, monkeypatch):
    async def no_sleep(_):
        pass

    monkeypatch.setattr(http.asyncio, "sleep", no_sleep)
    hits = iter([httpx.Response(503), httpx.Response(200, json={"a": 1})])
    api["/x"] = lambda request: next(hits)
    assert await http.fetch("https://core.basalam.com/x", {"q": 1}) == {"a": 1}
    assert await http.fetch("https://core.basalam.com/x", {"q": 1}) == {"a": 1}  # cached
    assert len(api.calls) == 2


async def test_http_rejects_other_hosts(api):
    with pytest.raises(http.ApiError):
        await http.fetch("https://example.com/x")


def test_clip():
    assert clip(None) is None and clip("ab") == "ab"
    assert clip("x" * 500) == "x" * 400 + "...[cut]"


async def test_titles_stripped_and_read_only():
    from mcp import Client

    async with Client(mcp) as c:
        tools = (await c.list_tools()).tools
    assert all("title" not in p for t in tools for p in t.input_schema.get("properties", {}).values())
    assert all(t.annotations.read_only_hint for t in tools)
