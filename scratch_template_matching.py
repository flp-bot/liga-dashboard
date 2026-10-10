from playwright.sync_api import sync_playwright
import hashlib
import json
import re

# PNG header & chunk parser in standard python library
import zlib
import struct

def parse_png_pixels(png_bytes):
    """
    Parses uncompressed PNG pixel luminance array from raw PNG file bytes using built-in zlib.
    """
    try:
        # Find IDAT chunk
        idat_data = b""
        pos = 8
        while pos < len(png_bytes):
            length, chunk_type = struct.unpack(">I4s", png_bytes[pos:pos+8])
            if chunk_type == b"IDAT":
                idat_data += png_bytes[pos+8:pos+8+length]
            pos += 12 + length
            if chunk_type == b"IEND":
                break

        decompressed = zlib.decompress(idat_data)
        return decompressed
    except Exception:
        return b""

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto('https://www.pacdeck.com.br/?view=ecom/itens&id=662762&page=1&tcg=2&txt_estoque=1&ultimas=1', wait_until='domcontentloaded')
        page.wait_for_timeout(2500)

        # Get all digit elements
        digit_elements = page.query_selector_all('.price .vidgmi div')
        print(f"Total digit sub-elements: {len(digit_elements)}")

        pos_pixels_map = {}
        for el in digit_elements:
            style = el.evaluate("e => e.getAttribute('style') || ''")
            bg_pos = el.evaluate("e => window.getComputedStyle(e).backgroundPosition")
            if 'v.png' in style or not bg_pos:
                continue

            if bg_pos not in pos_pixels_map:
                screenshot_bytes = el.screenshot()
                decomp = parse_png_pixels(screenshot_bytes)
                pos_pixels_map[bg_pos] = {
                    "raw_len": len(decomp),
                    "md5": hashlib.md5(screenshot_bytes).hexdigest()[:8]
                }

        print("Extracted position PNG pixel data:")
        for bg_pos, info in pos_pixels_map.items():
            print(f"  Pos: {bg_pos} -> Decompressed Length: {info['raw_len']} | Hash: {info['md5']}")

        browser.close()

if __name__ == '__main__':
    main()
