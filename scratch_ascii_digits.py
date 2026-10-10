from playwright.sync_api import sync_playwright
import json

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.pacdeck.com.br/?view=ecom/itens&id=662762&page=1&tcg=2&txt_estoque=1&ultimas=1', wait_until='domcontentloaded')
        page.wait_for_timeout(2500)

        ascii_art = page.evaluate('''async () => {
            const results = {};
            const elements = document.querySelectorAll('.price .vidgmi div');
            
            // Find sprite URL
            let spriteUrl = '';
            for (const sheet of document.styleSheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule.style && rule.style.backgroundImage && rule.style.backgroundImage.includes('imgnum')) {
                            spriteUrl = rule.style.backgroundImage.replace(/url\\(['"]?|['"]?\\)/g, '');
                        }
                    }
                } catch(e) {}
            }
            if (!spriteUrl.startsWith('http')) spriteUrl = window.location.protocol + spriteUrl;

            const img = new Image();
            img.crossOrigin = 'Anonymous';
            await new Promise(r => { img.onload = r; img.onerror = r; img.src = spriteUrl; });

            elements.forEach(el => {
                const bgPos = window.getComputedStyle(el).backgroundPosition;
                const style = el.getAttribute('style') || '';
                if (!bgPos || style.includes('v.png') || results[bgPos]) return;

                const canvas = document.createElement('canvas');
                canvas.width = 10;
                canvas.height = 14;
                const ctx = canvas.getContext('2d');
                
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, 10, 14);
                
                const matches = bgPos.match(/(-?\\d+)px\\s+(-?\\d+)px/);
                if (matches) {
                    const posX = Math.abs(parseInt(matches[1]));
                    const posY = Math.abs(parseInt(matches[2]));
                    try {
                        ctx.drawImage(img, posX, posY, 10, 14, 0, 0, 10, 14);
                    } catch(e) {}
                    
                    const imgData = ctx.getImageData(0, 0, 10, 14).data;
                    let art = '';
                    for (let y = 0; y < 14; y++) {
                        let row = '';
                        for (let x = 0; x < 10; x++) {
                            const i = (y * 10 + x) * 4;
                            const luma = (imgData[i] + imgData[i+1] + imgData[i+2]) / 3;
                            row += luma < 150 ? '#' : ' ';
                        }
                        art += row + '\\n';
                    }
                    results[bgPos] = art;
                }
            });
            return results;
        }''')
        
        for pos, art in ascii_art.items():
            print(f'=== Pos: {pos} ===')
            print(art)

        browser.close()

if __name__ == '__main__':
    main()
