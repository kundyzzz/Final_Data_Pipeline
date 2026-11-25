"""Playwright browser scraper for the JS-rendered Scraping Sandbox page.
The site DOM may change: run `python -m src.scraper --debug` to inspect cards.
"""
import argparse
import csv
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://scrapingsandbox.com/infinite-scroll"
FIELDS = ["sku", "name", "brand", "category", "price", "original_price", "rating", "availability", "source_url", "scraped_at"]
LOG = logging.getLogger(__name__)
SKU_RE = re.compile(r"\bSKU-[A-Z]+-\d+\b", re.I)
PRICE_RE = re.compile(r"\$\s*(\d+(?:\.\d{1,2})?)")
RATING_RE = re.compile(r"(?<!\d)([3-5](?:\.\d)?)(?!\d)")

# The DOM discovery script uses the smallest meaningful ancestor with a SKU and price.
# It avoids assuming a CSS class that has not been verified in a live browser.

EXTRACT_JS = r"""() => {
  const skuRx = /SKU-[A-Z]+-\d+/i;

  const nodes = [...document.querySelectorAll('h3.product-name')];
  const records = new Map();

  for (const nameEl of nodes) {
    const card = nameEl.parentElement;
    if (!card) continue;

    const getText = (selector) =>
      card.querySelector(selector)?.textContent?.trim() || '';

    const sku = getText('.sku').match(skuRx)?.[0];
    if (!sku) continue;

    const link = nameEl.closest('a[href]') ||
                 card.closest('a[href]');

    records.set(sku.toUpperCase(), {
      sku: sku.toUpperCase(),
      name: getText('.product-name'),
      brand: getText('.vendor'),
      rating: getText('.rating'),
      price: getText('.price'),
      original_price: getText('.compare-at-price'),
      category: getText('.category'),
      availability: getText('.availability'),
      href: link?.href || ''
    });
  }

  return [...records.values()];
}"""



def parse_card(item):
    sku = str(item.get("sku", "")).strip().upper()
    name = str(item.get("name", "")).strip()
    brand = str(item.get("brand", "")).strip()
    category = str(item.get("category", "")).strip()

    def clean_price(value):
        value = str(value or "").strip()
        match = re.search(r"\d+(?:\.\d{1,2})?", value.replace(",", ""))
        return match.group() if match else ""

    price = clean_price(item.get("price"))
    original_price = clean_price(item.get("original_price"))

    rating = str(item.get("rating", "")).strip()

    availability_text = str(item.get("availability", "")).strip().lower()

    if "out of stock" in availability_text:
        availability = "out_of_stock"
    elif "in stock" in availability_text:
        availability = "in_stock"
    else:
        availability = "unknown"

    if not SKU_RE.fullmatch(sku) or not name or not price:
        return None

    return {
        "sku": sku,
        "name": name,
        "brand": brand,
        "category": category,
        "price": price,
        "original_price": original_price,
        "rating": rating,
        "availability": availability,
        "source_url": item.get("href") or URL,
        "scraped_at": datetime.now(timezone.utc).isoformat()
    }


def scrape_products(output_path='data/raw.csv', min_records=200, max_scrolls=90, headless=True, debug=False):
    output = Path(output_path);output.parent.mkdir(parents=True,exist_ok=True)
    records = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, args=['--no-sandbox'])
        try:
            page = browser.new_page(viewport={'width':1366,'height':900})
            response = page.goto(URL, wait_until='domcontentloaded', timeout=60000)
            if response and response.status >= 400:
                raise RuntimeError(f'Website HTTP {response.status}')
            page.wait_for_timeout(1500)
            stagnant = 0
            for step in range(max_scrolls):
                cards = page.evaluate(EXTRACT_JS)
                before = len(records)
                for item in cards:
                    parsed = parse_card(item)
                    if parsed: records[parsed['sku']] = parsed
                LOG.info('Scroll %d: DOM cards=%d unique=%d',step,len(cards),len(records))
                if debug and step==0:
                    LOG.info('First card diagnostic: %s',json_safe(cards[0] if cards else {}))
                if len(records)==before: stagnant+=1
                else: stagnant=0
                if stagnant>=7: break
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(1100)
            if debug:
                page.screenshot(path=str(output.parent/'scraper_debug.png'),full_page=True)
        finally:
            browser.close()
    if len(records)<min_records:
        raise RuntimeError(f'Only {len(records)} products collected; minimum {min_records}. Check DOM and infinite scroll. No CSV overwritten.')
    with output.open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(records.values())
    LOG.info('Saved %d products to %s',len(records),output)
    return len(records)

def json_safe(value):
    import json
    return json.dumps(value,ensure_ascii=False)[:1500]

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='data/raw.csv');ap.add_argument('--min-records',type=int,default=200);ap.add_argument('--headed',action='store_true');ap.add_argument('--debug',action='store_true')
    a=ap.parse_args();logging.basicConfig(level=logging.INFO,format='%(levelname)s %(message)s')
    scrape_products(a.output,a.min_records,headless=not a.headed,debug=a.debug)
