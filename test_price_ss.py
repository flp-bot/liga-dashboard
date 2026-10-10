from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.goto('https://www.pacdeck.com.br/?view=ecom%2Fitens&id=662762&page=1&tcg=2&txt_estoque=1&ultimas=1&txt_carta=&txt_edicao=&btBuscar=Buscar')
    page.wait_for_timeout(2500)
    
    # Hide all overlays
    page.evaluate("""() => {
        const banners = document.querySelectorAll('div');
        for (const b of banners) {
            if (b.innerText && b.innerText.includes('cookies')) {
                b.style.display = 'none';
            }
        }
    }""")
    
    cards = page.query_selector_all('.card-item')
    print(f"Total cards found: {len(cards)}")
    for i in range(min(5, len(cards))):
        c = cards[i]
        title = c.query_selector('.title').inner_text()
        price_el = c.query_selector('.price')
        if price_el:
            price_el.screenshot(path=f"price_{i}.png")
            print(f"Card {i}: {title} -> price_{i}.png")
            
    browser.close()
