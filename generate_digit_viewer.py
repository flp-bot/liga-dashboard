import json

with open('data/unique_digit_pos.json', 'r', encoding='utf-8') as f:
    pos_data = json.load(f)

html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Digit Resolver</title>
<style>
body { background: #0f172a; color: #fff; font-family: sans-serif; padding: 20px; }
.grid { display: flex; flex-wrap: wrap; gap: 16px; }
.card { background: #1e293b; border: 1px solid #334155; padding: 12px; border-radius: 8px; text-align: center; }
.card img { background: #fff; padding: 4px; border-radius: 4px; image-rendering: pixelated; width: 32px; height: 44px; }
input { width: 40px; text-align: center; font-size: 18px; font-weight: bold; margin-top: 8px; }
</style>
</head>
<body>
<h2>Mapeador de Dígitos CSS Sprite</h2>
<div class="grid">
"""

for bg_pos, item in pos_data.items():
    b64 = item['b64']
    html_content += f"""
    <div class="card">
        <div><img src="data:image/png;base64,{b64}"></div>
        <div style="font-size:11px; margin-top:4px; color:#94a3b8">{bg_pos}</div>
        <input type="text" maxlength="1" data-pos="{bg_pos}" placeholder="?">
    </div>
    """

html_content += """
</div>
</body>
</html>
"""

with open('data/view_digits.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Saved data/view_digits.html")
