from playwright.sync_api import sync_playwright
import json

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('file:///c:/liga/data/view_digits.html')
        
        digits_map = page.evaluate('''() => {
            const results = {};
            const cards = document.querySelectorAll('.card');
            
            cards.forEach(card => {
                const img = card.querySelector('img');
                const pos = card.querySelector('div:nth-child(2)').innerText.trim();
                
                const canvas = document.createElement('canvas');
                canvas.width = img.naturalWidth || 12;
                canvas.height = img.naturalHeight || 16;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                
                const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                let darkPixels = 0;
                let topDark = 0, midDark = 0, botDark = 0;
                const h = canvas.height, w = canvas.width;
                
                for (let y = 0; y < h; y++) {
                    for (let x = 0; x < w; x++) {
                        const idx = (y * w + x) * 4;
                        const luma = (data[idx] + data[idx+1] + data[idx+2]) / 3;
                        if (luma < 128) {
                            darkPixels++;
                            if (y < h/3) topDark++;
                            else if (y < 2*h/3) midDark++;
                            else botDark++;
                        }
                    }
                }
                results[pos] = { w, h, darkPixels, topDark, midDark, botDark };
            });
            return results;
        }''')
        
        for pos, m in digits_map.items():
            print(f"{pos} -> total_dark={m['darkPixels']}, top={m['topDark']}, mid={m['midDark']}, bot={m['botDark']}")

        browser.close()

if __name__ == '__main__':
    main()
