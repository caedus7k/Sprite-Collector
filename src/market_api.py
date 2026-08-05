import base64
import os
from typing import Any, Dict, List

import requests

EBAY_AUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
TCGPLAYER_TOKEN_URL = "https://api.tcgplayer.com/token"
TCGPLAYER_SEARCH_URL = "https://api.tcgplayer.com/v1.39.0/catalog/products"
TCGPLAYER_PRICE_URL = "https://api.tcgplayer.com/v1.39.0/pricing/product/"


class MarketplaceError(Exception):
    pass


def _get_env_or_raise(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    raise ValueError(
        f"Missing required environment variables: {', '.join(names)}."
        " Set them in .env or your environment before running the app."
    )


def _basic_auth_header(client_id: str, client_secret: str) -> str:
    encoded = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    return f"Basic {encoded}"


def load_ebay_access_token() -> str:
    token = os.getenv("EBAY_OAUTH_TOKEN")
    if token:
        return token

    client_id = _get_env_or_raise("EBAY_CLIENT_ID")
    client_secret = _get_env_or_raise("EBAY_CLIENT_SECRET")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": _basic_auth_header(client_id, client_secret),
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }
    response = requests.post(EBAY_AUTH_URL, headers=headers, data=data, timeout=15)
    if response.status_code != 200:
        raise MarketplaceError(f"eBay auth failed: {response.text}")
    payload = response.json()
    return payload.get("access_token") or ""


def fetch_ebay_sales(query: str, limit: int = 12) -> List[Dict[str, Any]]:
    if not query:
        return []

    token = load_ebay_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    params = {
        "q": query,
        "limit": limit,
        "sort": "price",
        "fieldgroups": "ASPECT_REFINEMENTS",
    }
    response = requests.get(EBAY_SEARCH_URL, headers=headers, params=params, timeout=15)
    if response.status_code != 200:
        raise MarketplaceError(f"eBay search failed: {response.text}")

    items = []
    for item in response.json().get("itemSummaries", []):
        items.append(
            {
                "title": item.get("title"),
                "price": item.get("price", {}).get("value"),
                "currency": item.get("price", {}).get("currency"),
                "condition": item.get("condition"),
                "item_url": item.get("itemWebUrl"),
                "image_url": item.get("image", {}).get("imageUrl"),
                "shipping": item.get("shippingOptions", [{}])[0]
                .get("shippingCost", {})
                .get("value"),
                "seller": item.get("seller", {}).get("username"),
            }
        )
    return items


def load_tcgplayer_access_token() -> str:
    token = os.getenv("TCGPLAYER_OAUTH_TOKEN")
    if token:
        return token

    client_id = _get_env_or_raise("TCGPLAYER_CLIENT_ID")
    client_secret = _get_env_or_raise("TCGPLAYER_CLIENT_SECRET")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": _basic_auth_header(client_id, client_secret),
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(
        TCGPLAYER_TOKEN_URL, headers=headers, data=data, timeout=15
    )
    if response.status_code != 200:
        raise MarketplaceError(f"TCGplayer auth failed: {response.text}")
    payload = response.json()
    return payload.get("access_token") or ""


def fetch_tcgplayer_sales(query: str, limit: int = 12) -> List[Dict[str, Any]]:
    if not query:
        return []

    access_token = load_tcgplayer_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    params = {"productName": query, "limit": limit}
    response = requests.get(
        TCGPLAYER_SEARCH_URL, headers=headers, params=params, timeout=15
    )
    if response.status_code != 200:
        raise MarketplaceError(f"TCGplayer search failed: {response.text}")

    products = []
    for product in response.json().get("results", []):
        product_id = product.get("productId")
        pricing = {}
        if product_id is not None:
            price_resp = requests.get(
                f"{TCGPLAYER_PRICE_URL}{product_id}", headers=headers, timeout=15
            )
            if price_resp.status_code == 200:
                pricing = price_resp.json().get("results", [{}])[0]

        products.append(
            {
                "name": product.get("productName"),
                "set_name": product.get("groupName") or product.get("subTypeName"),
                "condition": product.get("condition")
                or product.get("productCondition"),
                "product_id": product_id,
                "url": (
                    f"https://www.tcgplayer.com/search/product/productId/{product_id}"
                    if product_id
                    else None
                ),
                "market_price": pricing.get("marketPrice"),
                "avg_price": pricing.get("midPrice"),
                "low_price": pricing.get("lowPrice"),
                "high_price": pricing.get("highPrice"),
            }
        )
    return products
