"""Product search, cheapest offers and the category tree."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field

from .http import CORE, SERVICES, fetch
from .registry import clip, tool

SORTS = {"relevance": "rank", "bestselling": "sales", "cheapest": "price", "expensive": "pricedesc", "newest": "newest"}

Query = Annotated[
    str, Field(min_length=1, pattern=r"\S", description="Search words, Persian matches best, e.g. 'عسل طبیعی'.")
]
MinPrice = Annotated[int | None, Field(ge=0, description="Lowest price in Toman, e.g. 100000.")]
MaxPrice = Annotated[int | None, Field(ge=0, description="Highest price in Toman, e.g. 500000.")]
CategoryId = Annotated[
    int | None, Field(ge=1, description="Category id from bs_categories (any level), e.g. 172 for honey.")
]
FreeShipping = Annotated[bool, Field(description="Only products with free shipping to the whole country.")]
HasDiscount = Annotated[bool, Field(description="Only products with a discount or coupon.")]
TopVendors = Annotated[bool, Field(description="Only products from top-rated shops (غرفه برتر).")]
Installments = Annotated[bool, Field(description="Only products that can be bought in installments (قسطی).")]


def toman(rial: float | int | None) -> int | None:
    """Basalam prices are Rial; the tools speak Toman."""
    return None if rial is None else round(rial / 10)


def card(p: dict[str, Any]) -> dict[str, Any]:
    """One compact product row from a search hit."""
    price, old = p.get("price"), p.get("primaryPrice")
    v, r = p.get("vendor") or {}, p.get("rating") or {}
    return {
        "id": p["id"],
        "name": clip(p.get("name"), n=100),
        "price": toman(price),
        "original_price": toman(old) if old and price and old > price else None,
        "discount_pct": round((1 - price / old) * 100) if old and price and old > price else None,
        "rating": r.get("average") or None,
        "rating_count": r.get("count") or None,
        "free_shipping": p.get("isFreeShipping") or None,
        "in_stock": p.get("IsAvailable"),
        "stock": p.get("stock"),
        "unit": p.get("mainAttribute"),
        "category": p.get("categoryTitle"),
        "shop": v.get("name"),
        "shop_id": v.get("identifier"),
    }


def search_params(
    query: str | None,
    sort: str,
    min_price: int | None,
    max_price: int | None,
    category_id: int | None,
    free_shipping: bool,
    has_discount: bool,
    top_vendors: bool,
    installments: bool,
    vendor: str | None,
    start: int,
    size: int,
) -> dict[str, Any]:
    flags = {
        "freeShipping": free_shipping,
        "hasDiscount": has_discount,
        "vendorScore": top_vendors,
        "salampay": installments,
    }
    p: dict[str, Any] = {"q": query, "sort": SORTS[sort], "from": start, "size": size}
    p["filters.minPrice"] = min_price * 10 if min_price is not None else None  # API takes Rial
    p["filters.maxPrice"] = max_price * 10 if max_price is not None else None
    p["filters.categories"] = category_id
    p["filters.vendorIdentifier"] = vendor
    p.update({f"filters.{k}": "true" for k, on in flags.items() if on})
    return p


async def run_search(**kw: Any) -> tuple[list[dict[str, Any]], int]:
    """Fetch one search page; return deduplicated cards and the total match count (the API caps it at 10000).

    The API drops duplicate rows, so a page can come back short; the missing ones are fetched from the rows after it
    (at most 5 requests), which means neighbouring pages can repeat a few products.
    """
    start, size = kw.pop("start"), kw.pop("size")
    seen: set[int] = set()
    cards: list[dict[str, Any]] = []
    total = 0
    for _ in range(5):
        want = size - len(cards)
        body = await fetch(f"{SERVICES}/search/product/search", search_params(**kw, start=start, size=want))
        rows = body.get("products", [])
        for p in rows:
            if p["id"] not in seen:
                seen.add(p["id"])
                cards.append(card(p))
        total = (body.get("meta") or {}).get("count", len(cards))
        start += want
        if len(cards) >= size or not rows or start >= total:
            break
    return cards, total


@tool("Search products")
async def bs_search(
    query: Query,
    sort: Annotated[
        Literal["relevance", "bestselling", "cheapest", "expensive", "newest"], Field(description="Result order.")
    ] = "relevance",
    min_price: MinPrice = None,
    max_price: MaxPrice = None,
    category_id: CategoryId = None,
    free_shipping: FreeShipping = False,
    has_discount: HasDiscount = False,
    top_vendors: TopVendors = False,
    installments: Installments = False,
    page: Annotated[int, Field(ge=1, le=200, description="Page number, 1-based.")] = 1,
    limit: Annotated[
        int, Field(ge=1, le=30, description="Products per page (max 30, keeps the reply under 15 KB).")
    ] = 12,
) -> dict[str, Any]:
    """Search Basalam products and return a page of cards with prices in Toman.

    Use for browsing a product type; the filters and sort run on the server. To rank by real price use
    bs_find_cheapest, for one product bs_product, for one shop's catalog bs_vendor_products. A product's link is
    https://basalam.com/p/<id>; neighbouring pages can repeat a few products.
    """
    cards, total = await run_search(
        query=query,
        sort=sort,
        min_price=min_price,
        max_price=max_price,
        category_id=category_id,
        free_shipping=free_shipping,
        has_discount=has_discount,
        top_vendors=top_vendors,
        installments=installments,
        vendor=None,
        start=(page - 1) * limit,
        size=limit,
    )
    return {"total": total, "page": page, "products": cards[:limit]}


@tool("Find cheapest products")
async def bs_find_cheapest(
    query: Query,
    min_price: Annotated[
        int,
        Field(
            ge=0,
            description="Lowest price in Toman. Default 5000 hides sample or filler listings that cost a few hundred.",
        ),
    ] = 5000,
    max_price: MaxPrice = None,
    category_id: CategoryId = None,
    free_shipping: FreeShipping = False,
    top_vendors: TopVendors = False,
    rating_min: Annotated[
        float, Field(ge=0, le=5, description="Drop products rated below this; above 0 also drops unrated ones.")
    ] = 0,
    limit: Annotated[int, Field(ge=1, le=30, description="Offers to return.")] = 10,
) -> dict[str, Any]:
    """List the cheapest in-stock offers for a query, cheapest first, prices in Toman.

    Reads the server's price-ascending sort (two pages of 48), drops out-of-stock items and, with rating_min,
    low-rated ones. Raise min_price when results are still accessories; narrow with category_id from bs_categories.
    """
    offers: list[dict[str, Any]] = []
    total = 0
    for start in (0, 48):
        cards, total = await run_search(
            query=query,
            sort="cheapest",
            min_price=min_price,
            max_price=max_price,
            category_id=category_id,
            free_shipping=free_shipping,
            has_discount=False,
            top_vendors=top_vendors,
            installments=False,
            vendor=None,
            start=start,
            size=48,
        )
        offers += [c for c in cards if c["in_stock"] is not False and (c.get("rating") or 0) >= rating_min]
        if len(offers) >= limit or len(cards) < 48:
            break
    offers.sort(key=lambda c: c["price"] or 0)
    return {"total_matches": total, "offers": offers[:limit]}


def _node(c: dict[str, Any]) -> dict[str, Any]:
    return {"id": c["id"], "title": c["title"], "children": len(c.get("children") or [])}


def _find(nodes: list[dict[str, Any]], cid: int) -> dict[str, Any] | None:
    for n in nodes:
        if n["id"] == cid:
            return n
        if hit := _find(n.get("children") or [], cid):
            return hit
    return None


@tool("List categories")
async def bs_categories(
    parent_id: Annotated[
        int | None, Field(ge=1, description="Category id to list the children of, e.g. 1 (food). Omit for top level.")
    ] = None,
    query: Annotated[
        str | None,
        Field(
            min_length=2,
            description="Find categories whose title contains this, at any depth (inside parent_id when given), e.g. 'عسل'.",
        ),
    ] = None,
) -> dict[str, Any]:
    """Browse Basalam's category tree and return ids for the category_id filter of bs_search.

    Without arguments lists the 12 top-level categories; pass parent_id to go one level down, or query to
    find a category by name anywhere in the tree (returns its path). With both, query searches only inside
    parent_id's subtree. Ids at any level work as filters.
    """
    tree = await fetch(f"{CORE}/category")
    if query:
        root = tree
        base: list[str] = []
        if parent_id is not None:
            parent = _find(tree, parent_id)
            if parent is None:
                return {"categories": [], "note": f"No category {parent_id}."}
            root, base = parent.get("children") or [], [parent["title"]]

        def norm(s: str) -> str:  # ZWNJ as space, Arabic yeh/kaf as Persian
            return s.replace("\u200c", " ").replace("\u064a", "\u06cc").replace("\u0643", "\u06a9")

        q = norm(query)
        hits: list[dict[str, Any]] = []

        def walk(nodes: list[dict[str, Any]], path: list[str]) -> None:
            for n in nodes:
                here = [*path, n["title"]]
                if q in norm(n["title"]) and len(hits) < 30:
                    hits.append({**_node(n), "path": " > ".join(here)})
                walk(n.get("children") or [], here)

        walk(root, base)
        return {"categories": hits}
    if parent_id is None:
        return {"categories": [_node(c) for c in tree]}
    parent = _find(tree, parent_id)
    if parent is None:
        return {"categories": [], "note": f"No category {parent_id}."}
    return {"parent": parent["title"], "categories": [_node(c) for c in parent.get("children") or []]}
