import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io, base64, os

def generate_captcha():
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    text = ''.join(random.choices(chars, k=6))

    img = Image.new('RGB', (200, 70), color=(245, 245, 250))
    draw = ImageDraw.Draw(img)

    # noise dots
    for _ in range(400):
        x, y = random.randint(0,200), random.randint(0,70)
        draw.point((x,y), fill=(random.randint(100,200), random.randint(100,200), random.randint(100,200)))

    # noise lines
    for _ in range(6):
        x1,y1 = random.randint(0,200), random.randint(0,70)
        x2,y2 = random.randint(0,200), random.randint(0,70)
        draw.line([(x1,y1),(x2,y2)], fill=(random.randint(100,180),random.randint(100,180),random.randint(100,180)), width=1)

    # draw chars
    for i, ch in enumerate(text):
        x = 18 + i * 28 + random.randint(-4,4)
        y = random.randint(8, 22)
        r = random.randint(30,120)
        g = random.randint(30,120)
        b = random.randint(30,120)
        draw.text((x, y), ch, fill=(r,g,b))

    img = img.filter(ImageFilter.SMOOTH)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    return text, f'data:image/png;base64,{b64}'
