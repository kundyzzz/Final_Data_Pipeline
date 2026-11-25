
from src.scraper import parse_card


def test_parse_structured_card():
    item = {
        "sku": "SKU-HEA-0001",
        "name": "Lightweight Probiotics",
        "brand": "SoundWave",
        "rating": "4",
        "price": "$155.62",
        "original_price": "$206.69",
        "category": "Health",
        "availability": "In Stock",
        "href": "https://scrapingsandbox.com/product/1",
    }

    result = parse_card(item)

    assert result is not None

    # Product identification
    assert result["sku"] == "SKU-HEA-0001"
    assert result["name"] == "Lightweight Probiotics"
    assert result["brand"] == "SoundWave"

    # Product prices
    assert result["price"] == "155.62"
    assert result["original_price"] == "206.69"

    # Rating and category
    assert result["rating"] == "4"
    assert result["category"] == "Health"

    # Availability
    assert result["availability"] == "in_stock"

    # Product URL
    assert result["source_url"] == item["href"]


def test_parse_card_missing_required_fields():
    item = {
        "sku": "SKU-HEA-0002",
        "name": "",
        "price": "$25.00",
    }

    result = parse_card(item)

    assert result is None
