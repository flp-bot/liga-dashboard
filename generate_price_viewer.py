import base64

html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Price Screenshots</title>
<style>
body { background: #0f172a; color: #fff; font-family: sans-serif; padding: 20px; }
.card { background: #1e293b; border: 1px solid #334155; padding: 12px; border-radius: 8px; margin-bottom: 12px; }
.card img { background: #fff; padding: 4px; border-radius: 4px; }
</style>
</head>
<body>
<h2>Price Screenshots captured by Playwright</h2>
"""

for i in range(5):
    try:
        with open(f'price_{i}.png', 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
        html_content += f"""
        <div class="card">
            <h3>Price {i}</h3>
            <img src="data:image/png;base64,{b64}">
        </div>
        """
    except Exception:
        pass

html_content += """
</body>
</html>
"""

with open('data/view_prices.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Saved data/view_prices.html")
