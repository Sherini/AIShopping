
import re

# DEMO DATA ONLY.
# Product names, prices, and store links are examples.
# These are NOT verified live shopping listings.
# PNG images must exist inside frontend/images/.

DEMO_PRODUCTS = [
    {
        "name": "Comfortable Women's Sandals",
        "store": "Flipkart",
        "price": 599,
        "features": ["comfortable", "casual"],
        "image_url": "/images/sandals1.png",
        "product_url": (
            "https://www.flipkart.com/search?q=women+sandals"
        ),
    },
    {
        "name": "Women's Daily Wear Sandals",
        "store": "Amazon",
        "price": 649,
        "features": ["daily wear", "comfortable"],
        "image_url": "/images/sandals2.png",
        "product_url": (
            "https://www.amazon.in/s?k=women+sandals"
        ),
    },
    {
        "name": "Lightweight Women's Sandals",
        "store": "Meesho",
        "price": 399,
        "features": ["lightweight", "casual"],
        "image_url": "/images/sandals3.png",
        "product_url": (
            "https://www.meesho.com/search?q=women%20sandals"
        ),
    },
    {
        "name": "Women's Casual Sandals",
        "store": "Myntra",
        "price": 699,
        "features": ["casual", "comfortable"],
        "image_url": "/images/sandals4.png",
        "product_url": (
            "https://www.myntra.com/sandals"
        ),
    },
    {
        "name": "Women's Fashion Sandals",
        "store": "AJIO",
        "price": 749,
        "features": ["fashion", "lightweight"],
        "image_url": "/images/sandals1.png",
        "product_url": (
            "https://www.ajio.com/search/?text=sandals"
        ),
    },
]


def detect_budget(message: str):
    """Extract a budget such as 'under 700' or 'below ₹1,000'."""

    patterns = [
        r"(?:under|below|less than|within)\s*₹?\s*([\d,]+)",
        r"budget\s*(?:of|is|:)?\s*₹?\s*([\d,]+)",
        r"₹\s*([\d,]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, message.lower())

        if match:
            return int(match.group(1).replace(",", ""))

    return None


def detect_product_keywords(message: str):
    """Identify the product category requested by the user."""

    text = message.lower()

    categories = {
        "sandals": ["sandal", "sandals", "footwear"],
        "headphones": [
            "headphone",
            "headphones",
            "earphone",
            "earphones",
        ],
        "shirts": ["shirt", "t-shirt", "tshirt"],
        "bags": ["backpack", "bag", "bags"],
        "mouse": ["mouse"],
        "shoes": ["shoe", "shoes", "sneaker", "sneakers"],
    }

    for keywords in categories.values():
        if any(word in text for word in keywords):
            return keywords

    return []


def search_and_compare(message: str):
    """Filter demo products by category and budget, then rank them."""

    message_lower = message.lower().strip()
    max_price = detect_budget(message)
    keywords = detect_product_keywords(message)

    results = []

    for product in DEMO_PRODUCTS:
        product_name = product["name"].lower()

        # Do not return unrelated products.
        if not keywords:
            continue

        if not any(word in product_name for word in keywords):
            continue

        # Exclude products above the requested budget.
        if max_price is not None and product["price"] > max_price:
            continue

        item = product.copy()

        # Find matching preferences.
        item["preference_matches"] = [
            feature
            for feature in item["features"]
            if feature in message_lower
        ]

        item["demo_data"] = True
        item["listing_notice"] = (
            "Demo listing. Price and product details "
            "are not verified or live."
        )

        results.append(item)

    # Rank by preference matches first, then lowest price.
    results.sort(
        key=lambda item: (
            -len(item["preference_matches"]),
            item["price"],
        )
    )

    return {
        "query": message,
        "max_price": max_price,
        "data_notice": (
            "DEMO DATA ONLY. Prices and product details "
            "are examples, not live shopping data."
        ),
        "total_results": len(results),
        "recommended_products": results,
    }
