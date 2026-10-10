from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('file:///c:/liga/data/view_prices.html')
        
        art_map = page.evaluate('''() => {
            const results = [];
            document.querySelectorAll('.card').forEach((card, idx) => {
                const img = card.querySelector('img');
                const canvas = document.createElement('canvas');
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                
                const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                let art = '';
                for (let y = 0; y < canvas.height; y += 2) {
                    let row = '';
                    for (let x = 0; x < canvas.width; x++) {
                        const i = (y * canvas.width + x) * 4;
                        const luma = (data[i] + data[i+1] + data[i+2]) / 3;
                        row += luma < 128 ? '#' : ' ';
                    }
                    art += row + '\\n';
                }
                results.push({ idx, art });
            });
            return results;
        }''')
        
        for item in art_map:
            print(f"=== Price {item['idx']} ===")
            print(item['art'])

        browser.close()

if __name__ == '__main__':
    main()
