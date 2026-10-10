from playwright.sync_api import sync_playwright
import os, json

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto('https://www.pacdeck.com.br/?view=ecom/itens&id=662762&page=1&tcg=2&txt_estoque=1&ultimas=1', wait_until='domcontentloaded')
        page.wait_for_timeout(2500)

        # Get all price digit elements on page
        digit_elements = page.query_selector_all('.price .vidgmi div')
        print(f"Total price sub-elements found: {len(digit_elements)}")

        os.makedirs('data/crops', exist_ok=True)

        class_seen = {}
        for idx, el in enumerate(digit_elements):
            cls = el.evaluate("e => e.className")
            style = el.evaluate("e => e.getAttribute('style') || ''")
            bg_pos = el.evaluate("e => window.getComputedStyle(e).backgroundPosition")
            
            if 'v.png' in style:
                continue

            if bg_pos and bg_pos not in class_seen:
                class_seen[bg_pos] = cls
                filepath = f"data/crops/pos_{len(class_seen)}.png"
                el.screenshot(path=filepath)
                print(f"Captured screenshot for {cls} | Pos: {bg_pos} -> {filepath}")

        browser.close()

if __name__ == '__main__':
    main()
