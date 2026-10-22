<!-- mcp-name: io.github.sepehr071/basalam-mcp -->

<div align="center">

# basalam-mcp: Basalam MCP server for AI agents

**Let your AI agent shop on Basalam (باسلام).**<br>
An unofficial, read-only MCP server for [Basalam](https://basalam.com), Iran's marketplace of independent shops:<br>
search products, find the cheapest in-stock offers, read shops, categories and customer reviews, all from Claude, Cursor or Copilot.

[![PyPI](https://img.shields.io/pypi/v/basalam-mcp?color=2563eb)](https://pypi.org/project/basalam-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/basalam-mcp)](https://pypi.org/project/basalam-mcp/)
[![CI](https://github.com/sepehr071/basalam-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sepehr071/basalam-mcp/actions/workflows/ci.yml)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-io.github.sepehr071%2Fbasalam--mcp-7c3aed)](https://registry.modelcontextprotocol.io/?q=basalam-mcp)
[![License: MIT](https://img.shields.io/badge/license-MIT-16a34a)](https://github.com/sepehr071/basalam-mcp/blob/main/LICENSE)

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_basalam--mcp-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect/mcp/install?name=basalam&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22basalam-mcp%22%5D%7D)

[For AI agents](#for-ai-agents) · [Quick start](#quick-start) · [What it can do](#what-it-can-do) · [Tools](#tools) · [FAQ](#faq) · [فارسی](#فارسی)

</div>

---

## For AI agents

- **What:** unofficial MCP server (model context protocol) for Basalam (basalam.com), Iran's marketplace of small shops. Persian queries match best; prices in Toman.
- **Install:** `uvx basalam-mcp` or `claude mcp add basalam -- uvx basalam-mcp`. Transport: stdio. Needs [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python 3.10+).
- **Auth:** none, no API key or account. Optional `BASALAM_MCP_PROXY` (HTTP proxy URL, or a comma-separated list).
- **Access:** read-only. No login, basket, order, chat or review posting, so no confirmation is needed before calling any tool.
- **Tools:** 7, all prefixed `bs_`. Start with `bs_search` or `bs_find_cheapest`. Typical sequence: `bs_find_cheapest` -> `bs_product` -> `bs_reviews`.
- **Use when:** finding, comparing or judging products, prices, shops and reviews on Basalam.
- **Do not use when:** the user wants to buy something or needs anything behind a login.
- **Output:** compact JSON. Prices in Toman (the API reports Rial; converted), ratings 0-5, null and empty fields omitted. A product link is `https://basalam.com/p/<id>`.
- **Machine-readable:** [`server.json`](https://github.com/sepehr071/basalam-mcp/blob/main/server.json) and the
  [awesome-iran-mcp catalog](https://github.com/sepehr071/awesome-iran-mcp) (`TOOLS.md`, `servers.json`, `llms.txt`).

## Why

Basalam is a marketplace of thousands of small shops, so the same kind of item is listed many times at very
different prices, and a plain "cheapest first" sort is full of filler listings priced at a few hundred Toman.
Finding the real cheapest offer, then checking the product options, the shop and what buyers say, takes a lot of
clicking. With `basalam-mcp` an agent does it in a few calls: `bs_find_cheapest` (filler prices hidden by default),
`bs_product`, `bs_vendor` and `bs_reviews`.

## What it can do

- **Search** products with price range (Toman), category, free shipping, discount, top-shop and installment filters, sorted by relevance, sales, price or newest
- **Find the cheapest in-stock offers** for a query, with a price floor and an optional minimum rating
- **Read one product**: price, discount, stock, sales count, free-shipping threshold, options (sizes, colors), attributes, rating and its shop
- **Check a shop**: city, activity, product count, shipping methods, and browse or search its products
- **Browse categories**: the whole tree, children of a category, or search by name; ids feed the `category_id` filter
- **Read reviews** with the star histogram of the product and its shop
- **Read-only by design**: no login, no basket, no orders

Example prompts:

- "Cheapest handmade wool rug on Basalam with at least 4 stars?"
- "Find saffron under 500,000 Toman with free shipping, best sellers first."
- "Is this shop reliable? Show its profile, its newest products and the latest reviews."
- "List the sub-categories of home decor on Basalam."
- <span dir="rtl">ارزان&zwnj;ترین زعفران نگین با ارسال رایگان در باسلام کدام است؟</span>
- <span dir="rtl">نظر خریداران درباره این محصول را بخوان و بگو ایرادش چیست.</span>

## Quick start

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). No API key or account.

<details open>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add basalam -- uvx basalam-mcp
```
</details>

<details>
<summary><b>Claude Desktop</b></summary>

Settings → Developer → Edit Config, then add:

```json
{
  "mcpServers": {
    "basalam": { "command": "uvx", "args": ["basalam-mcp"] }
  }
}
```
</details>

<details>
<summary><b>Cursor</b></summary>

Add the Claude Desktop block above to `~/.cursor/mcp.json` (or `.cursor/mcp.json` in a project).
</details>

<details>
<summary><b>VS Code (Copilot agent mode)</b></summary>

Click **Install in VS Code** above, or add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "basalam": { "type": "stdio", "command": "uvx", "args": ["basalam-mcp"] }
  }
}
```
</details>

<details>
<summary><b>Codex CLI</b></summary>

```bash
codex mcp add basalam -- uvx basalam-mcp
```

Or in `~/.codex/config.toml`:

```toml
[mcp_servers.basalam]
command = "uvx"
args = ["basalam-mcp"]
```
</details>

<details>
<summary><b>Gemini CLI</b></summary>

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "basalam": { "command": "uvx", "args": ["basalam-mcp"] }
  }
}
```
</details>

<details>
<summary><b>Windsurf</b></summary>

Add the Claude Desktop block to `~/.codeium/windsurf/mcp_config.json`.
</details>

<details>
<summary><b>Anything else</b></summary>

It's a standard stdio MCP server: run `uvx basalam-mcp`, or `pip install basalam-mcp` and run `basalam-mcp`.
</details>

## Tools

All 7 tools are annotated `readOnlyHint: true` and return compact JSON, so they don't flood the agent's context.

| Tool | What it does |
|---|---|
| `bs_search` | Search Basalam products and return a page of cards with prices in Toman. |
| `bs_find_cheapest` | List the cheapest in-stock offers for a query, cheapest first, prices in Toman. |
| `bs_categories` | Browse Basalam's category tree and return ids for the category_id filter of bs_search. |
| `bs_product` | Get one product: price in Toman, discount, stock, options (colors, sizes), attributes, rating and its shop. |
| `bs_vendor` | Get a Basalam shop's profile: city, product count, shipping methods, activity and notice. |
| `bs_vendor_products` | List one shop's products with prices in Toman, searchable and sortable. |
| `bs_reviews` | Read customer reviews of a product with the star histogram, newest first. |

## How it works

```text
  AI agent  (Claude, Cursor, Copilot, ...)
      │
      │  MCP over stdio
      ▼
  basalam-mcp  (runs on your machine)
      │
      │  HTTPS
      └──────▶  services.basalam.com, core.basalam.com   search, products, shops, reviews
```

`basalam-mcp` runs locally and calls the same public endpoints the basalam.com web app uses. There is no hosted
server in between, no API key, and nothing about you is sent anywhere else. Only those two Basalam hosts are allowed.

## Good to know

- **Prices are in Toman.** The Basalam API answers in Rial; every tool divides by 10 (and price filters are multiplied by 10), so numbers match the website.
- **Ratings are 0-5.** A missing rating means not rated.
- **Persian queries match best.**
- **Result totals stop at 10000** (the search index cap). Pages hold at most 30 products to keep replies small; a short page is refilled from the following rows, so neighbouring pages can repeat a few products.
- **"Cheapest" sorts are full of filler listings** priced at a few hundred Toman; `bs_find_cheapest` hides prices under 5000 Toman by default (`min_price`).
- **Sales count and free-shipping threshold** of a product are read with two extra calls the product page uses; if one fails, its fields are simply missing.
- **Dates and times** are passed through as Basalam returns them (Iran local time, not converted).
- **Review, description and shop text is user-generated** and cut to 400 characters unless `full_text=true`.
- **Not exposed:** the vendor API's own `score` (always 0; use the shop stars from `bs_reviews`), and the rating and same-city search filters.
- **It does not** log in, fill a basket, order, chat with shops or post reviews.
- **Answers are cached for 60 seconds**; a timeout, 5xx or 429 is retried.

## FAQ

<details>
<summary><b>Is there a Basalam API or MCP server for AI agents?</b></summary>

Yes: `basalam-mcp` is an unofficial MCP server with 7 read-only tools for product search, cheapest offers, shops,
categories and reviews. It calls the same public endpoints the basalam.com web app uses; no API key is needed.
</details>

<details>
<summary><b>How do I use Basalam with Claude, Cursor or Copilot?</b></summary>

Add the server with `claude mcp add basalam -- uvx basalam-mcp` (or the matching config in
[Quick start](#quick-start)), then ask in plain language, in Persian or English.
</details>

<details>
<summary><b>Is it official, safe and free?</b></summary>

It is unofficial and not affiliated with Basalam. It is read-only (no login, basket or orders), runs on your
machine, and is free under the MIT license.
</details>

<details>
<summary><b>Do I need an Iranian IP?</b></summary>

No. In testing (2026-10-19) Basalam answered both from a Turkish exit and directly. If your network blocks it,
set `BASALAM_MCP_PROXY` to an HTTP proxy. Normal system proxy variables are ignored on purpose.
</details>

<details>
<summary><b>Can it buy something for me?</b></summary>

No, and that is deliberate. It has no login and only reads public data. The agent finds the best option; you buy it on the site.
</details>

<details>
<summary><b>Why are some prices missing or tiny?</b></summary>

Sorting by price puts filler listings at a few hundred Toman first. Use `bs_find_cheapest`, which hides prices under
5000 Toman by default; lower `min_price` if you really want them.
</details>

<details>
<summary><b>How do I filter by category?</b></summary>

Call `bs_categories` (with `query` to search by name, or `parent_id` to list children), then pass the id as `category_id` to `bs_search`.
</details>

<details>
<summary><b>Claude Desktop says <code>uvx</code> is not found</b></summary>

Use the full path to `uvx` (`where uvx` on Windows, `which uvx` on macOS/Linux) as `command`.
</details>

<details>
<summary><b>How do I debug what the agent sees?</b></summary>

```bash
npx @modelcontextprotocol/inspector uvx basalam-mcp
```
</details>

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `BASALAM_MCP_PROXY` | unset | Optional HTTP proxy URL; system proxy settings are ignored. Also accepts a comma-separated list: one is used until it gets blocked or fails to connect, then the next |

<a id="فارسی"></a>

## فارسی: سرور MCP باسلام

<div dir="rtl">

**basalam-mcp** یک سرور MCP غیررسمی و فقط&zwnj;خواندنی برای باسلام، بازار آنلاین کسب&zwnj;وکارهای کوچک و غرفه&zwnj;داران ایرانی، است. این سرور به دستیار هوش مصنوعی شما (Claude، Cursor، Copilot و ...) اجازه می&zwnj;دهد در باسلام جستجو کند، ارزان&zwnj;ترین پیشنهادها را پیدا کند و محصول، غرفه، دسته&zwnj;بندی و نظر خریداران را بخواند.

**چه کارهایی می&zwnj;کند**

- **جستجوی محصول** با فیلتر بازه قیمت، دسته&zwnj;بندی، ارسال رایگان، تخفیف، غرفه&zwnj;های برتر و پرداخت اقساطی؛ مرتب&zwnj;سازی بر اساس مرتبط&zwnj;ترین، پرفروش&zwnj;ترین، قیمت یا جدیدترین.
- **ارزان&zwnj;ترین پیشنهادهای موجود** برای یک عبارت، با حداقل قیمت و حداقل امتیاز اختیاری.
- **جزئیات محصول**: قیمت، تخفیف، موجودی، تعداد فروش، حد ارسال رایگان، گزینه&zwnj;ها (رنگ و سایز)، ویژگی&zwnj;ها، امتیاز و غرفه&zwnj;دار.
- **پروفایل غرفه**: شهر، تعداد محصول، روش&zwnj;های ارسال و فهرست محصولات غرفه.
- **درخت دسته&zwnj;بندی&zwnj;ها** و جستجوی دسته با نام.
- **نظرات خریداران** همراه با نمودار ستاره&zwnj;ها.

**نکته&zwnj;ها**

- فقط خواندنی است: وارد حساب نمی&zwnj;شود، سبد خرید نمی&zwnj;سازد و سفارش ثبت نمی&zwnj;کند.
- همه قیمت&zwnj;ها به تومان است و امتیازها از ۵.
- روی سیستم خود شما اجرا می&zwnj;شود و کلید API لازم ندارد.
- جستجو به فارسی بهتر جواب می&zwnj;دهد.

**نصب** (اول [uv](https://docs.astral.sh/uv/getting-started/installation/) را نصب کنید). در Claude Code:

</div>

```bash
claude mcp add basalam -- uvx basalam-mcp
```

<div dir="rtl">

در Claude Desktop، Cursor و بقیه برنامه&zwnj;ها همان تنظیم بخش [Quick start](#quick-start) را بگذارید.

**نمونه پرسش&zwnj;ها**

- «ارزان&zwnj;ترین زعفران نگین در باسلام کدام است؟»
- «محصولات دست&zwnj;ساز با ارسال رایگان زیر ۵۰۰ هزار تومان را نشان بده.»
- «این غرفه قابل اعتماد است؟ نظرات خریداران را بخوان.»
- «زیردسته&zwnj;های دسته خانه و دکور را فهرست کن.»

**کلمات کلیدی:** باسلام، خرید آنلاین از باسلام، بازار آنلاین کسب&zwnj;وکارهای کوچک، مقایسه قیمت، ارزان&zwnj;ترین قیمت، غرفه، صنایع دستی، سرور MCP، هوش مصنوعی.

</div>

## Development

```bash
git clone https://github.com/sepehr071/basalam-mcp && cd basalam-mcp
uv sync
uv run python -m pytest -q          # offline, against recorded responses
uv run python -m pytest -m live -q  # one live test per tool
uv run ruff check .
```

Tools live in `src/basalam_mcp/catalog.py` and `shop.py`; each is a typed async function with a docstring that tells
the agent when to use it. Issues and PRs are welcome, especially new tools and fixes for API changes.

Releases: bump the version in `pyproject.toml` and `server.json`, then push a `v*` tag. GitHub Actions tests,
publishes to PyPI and the [MCP Registry](https://registry.modelcontextprotocol.io), and creates the GitHub Release.

## Related servers

- [awesome-iran-mcp](https://github.com/sepehr071/awesome-iran-mcp): catalog of all Iranian-service MCP servers
- [Digikala MCP server](https://github.com/sepehr071/digikala-mcp) for Iran's largest online store
- [Torob MCP server](https://github.com/sepehr071/torob-mcp) for price comparison across Iranian shops
- [Technolife MCP server](https://github.com/sepehr071/technolife-mcp) for electronics prices
- [Banimode MCP server](https://github.com/sepehr071/banimode-mcp) for fashion
- [Divar MCP server](https://github.com/sepehr071/divar-mcp) for classified ads

## Disclaimer

Unofficial and not affiliated with or endorsed by Basalam. It uses the public endpoints of the basalam.com web app,
which can change without notice. Please keep request rates reasonable.

## License

[MIT](https://github.com/sepehr071/basalam-mcp/blob/main/LICENSE)
