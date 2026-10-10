from playwright.sync_api import sync_playwright
import base64
import json

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto('https://www.pacdeck.com.br/?view=ecom/itens&id=662762&page=1&tcg=2&txt_estoque=1&ultimas=1', wait_until='domcontentloaded')
        page.wait_for_timeout(2500)

        digit_elements = page.query_selector_all('.price .vidgmi div')
        print(f"Total price sub-elements found: {len(digit_elements)}")

        pos_map = {}

        for idx, el in enumerate(digit_elements):
            cls = el.evaluate("e => e.className")
            style = el.evaluate("e => e.getAttribute('style') || ''")
            bg_pos = el.evaluate("e => window.getComputedStyle(e).backgroundPosition")
            
            if 'v.png' in style or not bg_pos:
                continue

            if bg_pos not in pos_map:
                # Capture element PNG bytes directly from Playwright
                png_bytes = el.screenshot()
                b64 = base64.b64encode(png_bytes).decode('utf-8')
                pos_map[bg_pos] = {
                    "class": cls,
                    "pos": bg_pos,
                    "b64": b64,
                    "size": len(png_bytes)
                }

        browser.close()

    print(f"Captured {len(pos_map)} unique position screenshots.")
    with open('data/unique_digit_pos.json', 'w', encoding='utf-8') as f:
        json.dump(pos_map, f, indent=2)

if __name__ == '__main__':
    main()
